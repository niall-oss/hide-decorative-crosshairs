# Decompiled reference

The mod is written against these sources. Update the pins when a new game patch or ModsSettings API release ships.

| Source | Pinned version |
|---|---|
| Game client | [StranikS-Scan/WorldOfTanks-Decompiled `2.4.1_EU`](https://github.com/StranikS-Scan/WorldOfTanks-Decompiled/tree/2.4.1_EU) (live client v2.4.1.1 EU) |
| ModsSettings API | [izeberg/modssettingsapi 1.7.1](https://github.com/izeberg/modssettingsapi) |

Game paths are under `source/res/scripts/client/gui/Scaleform/`; ModsSettings paths are under `sources/scripts/client/gui/modsSettingsApi/`.

## Game behaviour the mod relies on

- **Panel**: `daapi/view/battle/shared/vehicle_mechanics/panels/decorative_crosshairs_panel.py`. `DecorativeCrosshairPanel._VEHICLE_MECHANIC_UI_COMPONENTS_MAP` maps each `VehicleMechanicKeys` value to a tuple of component names: `ACCURACY_STACKS → accuracy`, `BATTLE_FURY → fury`, `CONCENTRATION_MODE → concentration`, `OVERHEAT_GUN → temperatureGunOverheat`, `OVERHEAT_STACKS → overheat`, `PILLBOX_SIEGE_MODE → pillboxSiege`. `_addMechanicUIComponents(self, mechanicComponents)` calls `as_addDecorCrosshairS(name)` for each name. The mod overrides `_addMechanicUIComponents` and passes the original only the names that are not hidden.
- **Component names**: `genConsts/DECORATIVE_CROSSHAIR_CONSTS.py`. These are the strings in `config.KNOWN_COMPONENTS` and in `config.json`.
- **Caller**: `daapi/view/battle/shared/vehicle_mechanics/panels_common.py`. `VehicleMechanicsPanel.onTrackedMechanicsUpdate(mechanics)` skips mechanics where `arenaVisitor.extra.isGfHudMechanicEnabled(m)` is true (they are drawn by Gameface, not this panel), looks the rest up in the map and calls `_addMechanicUIComponents` once per mechanic. Overlays are added once per battle, so settings changes apply from the next battle.
- **Flash bridge**: `daapi/view/meta/DecorativeCrosshairPanelMeta.py`. `as_addDecorCrosshairS(type)` calls `flashObject.as_addDecorCrosshair(type)`. The Flash side was not inspected.
- **Gameplay**: `AccuracyStacksController.py` and `cgf_components/accuracy_stacks_manager.py` do not touch the gun marker or this panel, so hiding the overlay does not change the stacks' dispersion bonus.

## ModsSettings API behaviour the mod relies on

- `api.py` `setModTemplate`/`registerCallback` do `onSettingsChanged += callback`. There is no unregister call, so the mod removes it with `-=`.
- `templates.py` `createCheckbox(text, varName, value, tooltip=None, ...)`.
- `compareTemplates` replaces a stored template only when `settingsVersion` increases. Bump `SETTINGS_VERSION` in `mods_settings.py` when the checkboxes change.

## Updating for a new patch

1. Find the new branch: `git ls-remote --heads https://github.com/StranikS-Scan/WorldOfTanks-Decompiled.git`.
2. Re-check the files above for a renamed `_addMechanicUIComponents`, new entries in `_VEHICLE_MECHANIC_UI_COMPONENTS_MAP` or new `DECORATIVE_CROSSHAIR_CONSTS` values. Add new names to `config.KNOWN_COMPONENTS`.
3. Check the installed ModsSettings API version against the latest release and re-read `api.py` and `templates.py`.
4. Update `tests/fakes.py` if any of this behaviour changed, then the pins in this file.
