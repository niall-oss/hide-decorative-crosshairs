"""Check for new World of Tanks game versions and publish mod updates to wgmods.net."""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import httpx2

BASE_URL = "https://wgmods.net"
MOD_ID = 8207
REPO_ROOT = Path(__file__).resolve().parent.parent

# Without X-Requested-With the API answers 404 with an HTML page.
API_HEADERS = {"Accept": "application/json", "X-Requested-With": "XMLHttpRequest"}


@dataclass(frozen=True)
class GameVersion:
    id: int
    version: str


@dataclass(frozen=True)
class ModVersion:
    id: int
    version: str
    game_version: GameVersion
    created_at: str


@dataclass(frozen=True)
class PortalSettings:
    game_versions: list[GameVersion]
    max_versions: int


class WgmodsError(RuntimeError):
    pass


def read_mod_version() -> str:
    build_py = (REPO_ROOT / "build.py").read_text(encoding="utf-8")
    match = re.search(r'default="(\d+\.\d+\.\d+)"', build_py)
    if not match:
        raise WgmodsError("Could not find the mod version default in build.py")
    return match.group(1)


def parse_mod_versions(mod: dict) -> list[ModVersion]:
    return [
        ModVersion(
            id=item["id"],
            version=item["version"],
            game_version=GameVersion(**item["game_version"]),
            created_at=item["created_at"],
        )
        for item in mod.get("versions", [])
    ]


class Wgmods:
    def __init__(self, sessionid: str | None = None, csrftoken: str | None = None):
        cookies = {}
        headers = dict(API_HEADERS)
        if sessionid and csrftoken:
            cookies = {"sessionid": sessionid, "csrftoken": csrftoken}
            headers["X-CSRFToken"] = csrftoken
            headers["Referer"] = f"{BASE_URL}/{MOD_ID}/edit/"
        self.is_authenticated = bool(cookies)
        self.client = httpx2.Client(
            base_url=BASE_URL,
            headers=headers,
            cookies=cookies,
            timeout=httpx2.Timeout(30.0, write=300.0),
        )

    @classmethod
    def from_env(cls) -> Wgmods:
        return cls(
            os.environ.get("WGMODS_SESSIONID"), os.environ.get("WGMODS_CSRFTOKEN")
        )

    def portal_settings(self) -> PortalSettings:
        html = (
            self.client.get("/", headers={"Accept": "text/html"})
            .raise_for_status()
            .text
        )
        match = re.search(
            r'window\.__SETTINGS__\s*=\s*JSON\.parse\((".*?")\);', html, re.DOTALL
        )
        if not match:
            raise WgmodsError(
                "window.__SETTINGS__ not found on wgmods.net; the page layout changed"
            )
        settings = json.loads(json.loads(match.group(1)))
        return PortalSettings(
            game_versions=[GameVersion(**gv) for gv in settings["gameVersions"]],
            max_versions=settings["modMaxVersions"],
        )

    def mod_versions(self) -> list[ModVersion]:
        """Owner view when authenticated, so updates still in review count too."""
        path = (
            f"/api/mods/{MOD_ID}/owner/"
            if self.is_authenticated
            else f"/api/mods/{MOD_ID}/"
        )
        return parse_mod_versions(self._json("GET", path))

    def check_auth(self) -> None:
        response = self.client.get(f"/api/mods/{MOD_ID}/owner/")
        if response.status_code != 200 or "json" not in response.headers.get(
            "content-type", ""
        ):
            raise WgmodsError(
                f"wgmods session rejected (HTTP {response.status_code}); refresh the cookie secrets"
            )

    def upload_file(self, path: Path) -> tuple[int, str]:
        with path.open("rb") as fh:
            response = self.client.post(
                "/api/mods/mod_file_upload",
                files={"source": (path.name, fh, "application/octet-stream")},
            )
        if response.status_code != 201:
            raise WgmodsError(
                f"File upload failed (HTTP {response.status_code}): {response.text[:500]}"
            )
        data = response.json()
        item = data[0] if isinstance(data, list) else data
        return item["id"], item["access_token"]

    def create_version(self, body: dict) -> dict:
        return self._json("POST", "/api/mods/versions/", json=body)

    def delete_version(self, version_id: int) -> None:
        self._json("DELETE", f"/api/mods/versions/{version_id}/")

    def _json(self, method: str, path: str, **kwargs) -> dict:
        response = self.client.request(method, path, **kwargs)
        if response.is_error:
            raise WgmodsError(
                f"{method} {path} failed (HTTP {response.status_code}): {response.text[:500]}"
            )
        return response.json() if response.content else {}


def write_outputs(**values: str) -> None:
    lines = [f"{key}={value}" for key, value in values.items()]
    print("\n".join(lines))
    if output_file := os.environ.get("GITHUB_OUTPUT"):
        with open(output_file, "a", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")


def resolve_game_version(
    settings: PortalSettings, requested: str | None
) -> GameVersion:
    if not requested:
        return settings.game_versions[0]
    for gv in settings.game_versions:
        if gv.version == requested:
            return gv
    available = ", ".join(gv.version for gv in settings.game_versions)
    raise WgmodsError(
        f"Game version {requested} is not selectable on wgmods (available: {available})"
    )


def cmd_check(api: Wgmods, _args: argparse.Namespace) -> None:
    latest = api.portal_settings().game_versions[0]
    newest_supported = max(
        (v.game_version for v in api.mod_versions()), key=lambda gv: gv.id, default=None
    )
    is_new = newest_supported is None or latest.id > newest_supported.id
    print(
        f"Latest game version {latest.version}, newest on mod {newest_supported and newest_supported.version}"
    )
    write_outputs(
        new=str(is_new).lower(),
        game_version=latest.version,
        game_version_id=str(latest.id),
        mod_version=read_mod_version(),
    )


def cmd_auth_check(api: Wgmods, _args: argparse.Namespace) -> None:
    if not api.is_authenticated:
        raise WgmodsError("WGMODS_SESSIONID and WGMODS_CSRFTOKEN must be set")
    api.check_auth()
    print("wgmods session OK")


def cmd_mod_version(_api: Wgmods, _args: argparse.Namespace) -> None:
    write_outputs(mod_version=read_mod_version())


def cmd_publish(api: Wgmods, args: argparse.Namespace) -> None:
    if not api.is_authenticated:
        raise WgmodsError("WGMODS_SESSIONID and WGMODS_CSRFTOKEN must be set")
    api.check_auth()

    mod_version = read_mod_version()
    settings = api.portal_settings()
    game_version = resolve_game_version(settings, args.game_version)
    existing = sorted(api.mod_versions(), key=lambda v: v.created_at)

    if any(
        v.version == mod_version and v.game_version.id == game_version.id
        for v in existing
    ):
        print(
            f"{mod_version} for WoT {game_version.version} is already on wgmods; nothing to do"
        )
        return

    wotmod = Path(args.wotmod)
    if not wotmod.is_file():
        raise WgmodsError(f"{wotmod} does not exist")

    overflow = existing[: max(0, len(existing) - settings.max_versions + 1)]
    body = {
        "mod": MOD_ID,
        "game_version": game_version.id,
        "version": mod_version,
        "is_visible": True,
        "change_log": args.changes,
        "comment": args.comment,
    }

    print(
        f"Publishing {wotmod.name} as {mod_version} for WoT {game_version.version} (id {game_version.id})"
    )
    for old in overflow:
        print(
            f"Will delete oldest update {old.version} / WoT {old.game_version.version} (id {old.id}) to stay within {settings.max_versions}"
        )
    if args.dry_run:
        print("Dry run, request body:", json.dumps(body, indent=2))
        return

    for old in overflow:
        api.delete_version(old.id)
    file_id, token = api.upload_file(wotmod)
    created = api.create_version(
        body
        | {
            "temporary_version_file": file_id,
            "temporary_version_file_access_token": token,
        }
    )
    print(f"Submitted update id {created.get('id')} for review")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(required=True)

    sub.add_parser(
        "check",
        help="Report whether wgmods lists a game version newer than the mod supports",
    ).set_defaults(func=cmd_check)
    sub.add_parser(
        "auth-check", help="Verify the stored wgmods session cookies"
    ).set_defaults(func=cmd_auth_check)
    sub.add_parser(
        "mod-version", help="Print the mod version from build.py"
    ).set_defaults(func=cmd_mod_version)

    publish = sub.add_parser(
        "publish", help="Upload a .wotmod as a new update on wgmods"
    )
    publish.add_argument("--wotmod", required=True)
    publish.add_argument(
        "--game-version",
        help="Game version string, e.g. 2.4.1.1; defaults to the latest",
    )
    publish.add_argument("--changes", default="")
    publish.add_argument("--comment", default="")
    publish.add_argument("--dry-run", action="store_true")
    publish.set_defaults(func=cmd_publish)

    args = parser.parse_args()
    try:
        args.func(Wgmods.from_env(), args)
    except WgmodsError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
