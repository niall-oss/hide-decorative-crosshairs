"""Filtering, settings and init/fini behaviour against the game fakes."""

from conftest import CONFIG_DIR, read_config, write_config
from fakes import (
    ACCURACY_STACKS,
    BATTLE_FURY,
    CONCENTRATION_MODE,
    OVERHEAT_GUN,
    OVERHEAT_STACKS,
    PILLBOX_SIEGE_MODE,
)

ALL_MECHANICS = (
    ACCURACY_STACKS,
    BATTLE_FURY,
    CONCENTRATION_MODE,
    OVERHEAT_GUN,
    OVERHEAT_STACKS,
    PILLBOX_SIEGE_MODE,
)


def _battle(game, *mechanics, **kwargs):
    panel = game.Panel(**kwargs)
    panel.onTrackedMechanicsUpdate(mechanics)
    return panel.flashObject.decor_crosshairs


def _linkage(game):
    return game.mods_settings.MOD_LINKAGE


def _apply(game, **fields):
    settings = dict(game.api.state["settings"][_linkage(game)])
    settings.update(fields)
    game.api.apply(_linkage(game), settings)


def test_default_config_hides_accuracy_only(game):
    game.entry.init()

    assert _battle(game, ACCURACY_STACKS) == []
    assert _battle(game, *ALL_MECHANICS) == [
        "fury",
        "concentration",
        "temperatureGunOverheat",
        "overheat",
        "pillboxSiege",
    ]
    assert read_config() == {"enabled": True, "hidden": ["accuracy"]}


def test_config_hides_every_listed_component(game):
    write_config(hidden=["accuracy", "fury", "overheat"])

    game.entry.init()

    assert _battle(game, *ALL_MECHANICS) == [
        "concentration",
        "temperatureGunOverheat",
        "pillboxSiege",
    ]


def test_disabled_config_shows_everything(game):
    write_config(enabled=False)

    game.entry.init()

    assert _battle(game, ACCURACY_STACKS) == ["accuracy"]


def test_empty_hidden_list_shows_everything(game):
    write_config(hidden=[])

    game.entry.init()

    assert _battle(game, ACCURACY_STACKS, BATTLE_FURY) == ["accuracy", "fury"]


def test_unreadable_config_falls_back_to_defaults(game):
    CONFIG_DIR.mkdir(parents=True)
    (CONFIG_DIR / "config.json").write_text("not json")

    game.entry.init()

    assert _battle(game, ACCURACY_STACKS, BATTLE_FURY) == ["fury"]


def test_non_list_hidden_falls_back_to_defaults(game):
    CONFIG_DIR.mkdir(parents=True)
    (CONFIG_DIR / "config.json").write_text('{"hidden": "fury"}')

    game.entry.init()

    assert _battle(game, ACCURACY_STACKS, BATTLE_FURY) == ["fury"]


def test_gameface_mechanic_is_untouched(game):
    game.entry.init()

    assert _battle(game, ACCURACY_STACKS, gameface_mechanics={ACCURACY_STACKS}) == []
    assert _battle(game, BATTLE_FURY, gameface_mechanics={ACCURACY_STACKS}) == ["fury"]


def test_settings_window_unticking_shows_overlay_next_battle(game):
    game.entry.init()

    _apply(game, accuracy=False)

    assert _battle(game, ACCURACY_STACKS) == ["accuracy"]
    assert read_config()["hidden"] == []


def test_settings_window_ticking_hides_more_overlays(game):
    game.entry.init()

    _apply(game, fury=True, pillboxSiege=True)

    assert _battle(game, *ALL_MECHANICS) == [
        "concentration",
        "temperatureGunOverheat",
        "overheat",
    ]


def test_settings_window_disable_shows_everything(game):
    game.entry.init()

    _apply(game, enabled=False)

    assert _battle(game, ACCURACY_STACKS) == ["accuracy"]
    assert read_config()["enabled"] is False


def test_settings_window_keeps_hand_added_names(game):
    write_config(hidden=["accuracy", "futureOverlay"])
    game.entry.init()

    _apply(game, accuracy=False)

    assert read_config()["hidden"] == ["futureOverlay"]


def test_saved_settings_apply_on_next_start(game):
    game.entry.init()
    _apply(game, accuracy=False, fury=True)
    game.entry.fini()
    write_config(hidden=["accuracy"])

    game.entry.init()

    assert _battle(game, ACCURACY_STACKS, BATTLE_FURY) == ["accuracy"]


def test_works_without_mods_settings_api(game_without_api):
    game = game_without_api

    game.entry.init()

    assert _battle(game, ACCURACY_STACKS, BATTLE_FURY) == ["fury"]
    assert any("ModsSettings API not installed" in note for note in game.notes)


def test_fini_restores_original_and_listeners(game):
    game.entry.init()

    game.entry.fini()
    game.entry.fini()

    assert game.Panel.__dict__["_addMechanicUIComponents"] is game.original
    assert list(game.api.onSettingsChanged) == []
    assert _battle(game, ACCURACY_STACKS) == ["accuracy"]


def test_stale_wrapper_passes_through_after_fini(game):
    game.entry.init()
    stale = game.Panel.__dict__["_addMechanicUIComponents"]
    panel = game.Panel()

    game.entry.fini()
    stale(panel, ("accuracy",))

    assert panel.flashObject.decor_crosshairs == ["accuracy"]


def test_fini_leaves_another_mods_wrapper_in_place(game):
    game.entry.init()
    ours = game.Panel.__dict__["_addMechanicUIComponents"]

    def theirs(self, mechanicComponents):
        return ours(self, mechanicComponents)

    game.Panel._addMechanicUIComponents = theirs

    game.entry.fini()

    assert game.Panel.__dict__["_addMechanicUIComponents"] is theirs
    assert game.notes
    assert _battle(game, ACCURACY_STACKS) == ["accuracy"]


def test_reinit_does_not_stack_wrappers_or_listeners(game):
    game.entry.init()
    first = game.Panel.__dict__["_addMechanicUIComponents"]
    game.entry.init()

    assert game.Panel.__dict__["_addMechanicUIComponents"] is first
    assert len(game.api.onSettingsChanged) == 1

    game.entry.fini()
    game.entry.init()

    assert len(game.api.onSettingsChanged) == 1
    assert _battle(game, ACCURACY_STACKS, BATTLE_FURY) == ["fury"]

    game.entry.fini()

    assert game.Panel.__dict__["_addMechanicUIComponents"] is game.original


def test_unsupported_client_does_not_register(game):
    del game.Panel._addMechanicUIComponents

    game.entry.init()

    assert "_addMechanicUIComponents" not in vars(game.Panel)
    assert list(game.api.onSettingsChanged) == []
    assert any("not supported" in note for note in game.notes)
