# Hide Decorative Crosshairs

A World of Tanks PC mod that hides the decorative overlays some vehicle mechanics draw around your own reticle. You can keep the normal reticle; the mechanic itself, including its accuracy bonus, is unchanged.

[Wargaming Mod Portal](https://wgmods.net/8207/)

## Overlays

| Overlay | Mechanic | Example vehicles |
|---|---|---|
| `accuracy` | Accuracy Stacks | Leopard 120 Verbessert |
| `fury` | Battle Fury | T803 |
| `concentration` | Concentration Mode | XM69 Hacker |
| `temperatureGunOverheat` | Gun Overheat | None yet |
| `overheat` | Overheat Stacks | Hirschkäfer |
| `pillboxSiege` | Pillbox Siege Mode | Strv 107-12 |

## Normal gun marker on the Leopard 120 Verbessert

The Leopard 120 Verbessert swaps the gun marker you picked in Settings for its own solid Accuracy Stacks marker. Tick **Use my normal gun marker** (or set `"defaultGunMarker": true`) to keep your usual marker on it. It's the only vehicle in the 2.4.1.1 EU client with this mechanic. Off by default.

## Installation

1. Put the `.wotmod` in `World_of_Tanks/mods/<game_version>/`.
2. Optional, for the garage settings window: install [OpenWG Gameface](https://gitlab.com/openwg/wot.gameface/), [ModsList](https://gitlab.com/wot-public-mods/mods-list/) and [ModsSettings API](https://github.com/izeberg/modssettingsapi) in the same folder.

## Usage

With ModsSettings API, open **Mods** in the garage → **Mod configurator** → **Hide Decorative Crosshairs**, tick the overlays to hide and click **Apply**. Changes apply from your next battle.

Without it, edit `World_of_Tanks/mods/<game_version>/configs/ANIALLATOR.hide_decorative_crosshairs/config.json` and restart the game:

```json
{
  "enabled": true,
  "hidden": ["accuracy"],
  "defaultGunMarker": true
}
```

The defaults are `"hidden": []` and `"defaultGunMarker": false`.

`hidden` takes any overlay name from the table above, or a newer one added in a later patch.

## Development

- Python 2.7.18 ([download page](https://www.python.org/downloads/release/python-2718/)) to build the mod.
- [uv](https://docs.astral.sh/uv/) for the tests and checks.

### Build

```bash
# CMD or PowerShell
C:\Python27\python.exe build.py --username ANIALLATOR --version 1.0.0

# Git Bash
/c/Python27/python.exe build.py --username ANIALLATOR --version 1.0.0
```

Output: `build/ANIALLATOR.Hide_Decorative_Crosshairs_1.0.0.wotmod`

### Checks

`uv run pytest` tests filtering, settings, unloading and re-loading against stand-ins for the game and ModsSettings API. CI also runs `uv run ruff format --check` and `uv run ty check`.

### CI / Releases

GitHub Actions builds the mod on every pull request (artifact `wotmod-pr-{commit_sha}`) and publishes a `v{version}` GitHub Release on merges to `master`.

### Publishing to wgmods.net

The mod version lives in `build.py` (`--version` default). Release tooling in `scripts/wgmods.py` runs on the latest Python via [uv](https://docs.astral.sh/uv/) (`uv run scripts/wgmods.py --help`).

- **Game patches (automatic)**: the **Game patch update** workflow runs daily at 13:00 UTC. When wgmods lists a game version newer than the mod's latest update, it creates a `v{mod}+wot{game}` GitHub Release and submits the same mod version for that game version. If the mod already has the maximum number of updates (6), the oldest update is deleted first.
- **Code changes (manual)**: bump the version in `build.py`, then merge. Then run **Actions → Publish to wgmods** and enter the version changes text. Game version defaults to the latest; `dry_run` prints the request without uploading.

Both workflows authenticate with the repo secrets `WGMODS_SESSIONID` and `WGMODS_CSRFTOKEN`, which are your wgmods.net login cookies. Find them in DevTools → Application → Cookies → `https://wgmods.net`. If they stop working, the daily run opens a "wgmods session cookie expired" issue telling you to paste fresh ones.

### Decompiled reference

See [docs/DECOMPILED_REFERENCE.md](docs/DECOMPILED_REFERENCE.md) for the game and ModsSettings API versions the mod is written against, and how to update them for a new patch.

## Credits

- [StranikS-Scan / WorldOfTanks-Decompiled](https://github.com/StranikS-Scan/WorldOfTanks-Decompiled) — decompiled game sources
- [ModsSettings API](https://github.com/izeberg/modssettingsapi) — mod configuration menu
- [LockBlock-dev](https://github.com/LockBlock-dev/wot-mods/tree/master/auto-packer) — original packer script
