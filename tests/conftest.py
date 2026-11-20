import json
import sys
import types
from pathlib import Path

import pytest
from fakes import FakeModsSettingsApi, make_panel_classes, make_templates_module

CLIENT_SCRIPTS = Path(__file__).resolve().parents[1] / "res" / "scripts" / "client"
MOD_PACKAGES = ("gui.hidedecorativecrosshairs", "gui.mods")
CONFIG_DIR = Path("mods/configs/ANIALLATOR.hide_decorative_crosshairs")
PANEL_MODULE = (
    "gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.panels."
    "decorative_crosshairs_panel"
)


def _install_game_modules(monkeypatch, game):
    def module(name, **attrs):
        mod = types.ModuleType(name)
        mod.__dict__.update(attrs)
        monkeypatch.setitem(sys.modules, name, mod)
        parent, _, child = name.rpartition(".")
        if parent in sys.modules:
            setattr(sys.modules[parent], child, mod)
        return mod

    module("debug_utils", LOG_NOTE=game.notes.append)

    gui = module("gui")
    gui.__path__ = [str(CLIENT_SCRIPTS / "gui")]
    parts = PANEL_MODULE.split(".")
    for depth in range(2, len(parts)):
        module(".".join(parts[:depth]))
    module(PANEL_MODULE, DecorativeCrosshairPanel=game.Panel)

    if game.api is not None:
        templates = make_templates_module()
        module("gui.modsSettingsApi", g_modsSettingsApi=game.api, templates=templates)
        monkeypatch.setitem(sys.modules, templates.__name__, templates)


def _forget_mod_modules():
    for name in list(sys.modules):
        if any(name == pkg or name.startswith(pkg + ".") for pkg in MOD_PACKAGES):
            del sys.modules[name]


def _import_mod_fresh():
    _forget_mod_modules()
    import gui.mods.mod_hidedecorativecrosshairs as entry
    from gui.hidedecorativecrosshairs import mods_settings

    return entry, mods_settings


def write_config(enabled=True, hidden=("accuracy",)):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    (CONFIG_DIR / "config.json").write_text(
        json.dumps({"enabled": enabled, "hidden": list(hidden)})
    )


def read_config():
    return json.loads((CONFIG_DIR / "config.json").read_text())


def _make_game(monkeypatch, tmp_path, api):
    monkeypatch.chdir(tmp_path)

    Panel = make_panel_classes()
    game = types.SimpleNamespace(
        Panel=Panel,
        original=Panel.__dict__["_addMechanicUIComponents"],
        api=api,
        notes=[],
    )
    _install_game_modules(monkeypatch, game)
    game.entry, game.mods_settings = _import_mod_fresh()
    return game


@pytest.fixture
def game(monkeypatch, tmp_path):
    game = _make_game(monkeypatch, tmp_path, FakeModsSettingsApi())
    yield game
    game.entry.fini()
    _forget_mod_modules()


@pytest.fixture
def game_without_api(monkeypatch, tmp_path):
    game = _make_game(monkeypatch, tmp_path, None)
    yield game
    game.entry.fini()
    _forget_mod_modules()
