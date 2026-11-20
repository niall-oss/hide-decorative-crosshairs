# Hide Decorative Crosshairs

A World of Tanks PC mod that hides the decorative overlays some vehicle mechanics draw around your own reticle, starting with the Leopard 120 Verbessert's Accuracy Stacks overlay. You keep the normal reticle; the mechanic itself, including its accuracy bonus, is unchanged.

## Overlays

Nothing is hidden until you tick it. Example vehicles are from the 2.4.1.1 EU client.

| Overlay | Mechanic | Example vehicles |
|---|---|---|
| `accuracy` | Accuracy Stacks | Leopard 120 Verbessert |
| `fury` | Battle Fury | T803 |
| `concentration` | Concentration Mode | XM69 Hacker |
| `temperatureGunOverheat` | Gun Overheat | None yet |
| `overheat` | Overheat Stacks | Hirschkäfer |
| `pillboxSiege` | Pillbox Siege Mode | Strv 107-12 |

Mechanics whose HUD is drawn by Gameface are not affected.

## Installation

1. Put the `.wotmod` in `World_of_Tanks/mods/<game_version>/`.
2. Optional, for the garage settings window: install [OpenWG Gameface](https://gitlab.com/openwg/wot.gameface/), [ModsList](https://gitlab.com/wot-public-mods/mods-list/) and [ModsSettings API](https://github.com/izeberg/modssettingsapi) in the same folder.

## Usage

With ModsSettings API, open **Mods** in the garage → **Mod configurator** → **Hide Decorative Crosshairs**, tick the overlays to hide and click **Apply**. Changes apply from your next battle.

Without it, edit `World_of_Tanks/mods/<game_version>/configs/ANIALLATOR.hide_decorative_crosshairs/config.json` and restart the game:

```json
{
  "enabled": true,
  "hidden": ["accuracy"]
}
```

The default is `"hidden": []`.

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

### Decompiled reference

See [docs/DECOMPILED_REFERENCE.md](docs/DECOMPILED_REFERENCE.md) for the game and ModsSettings API versions the mod is written against, and how to update them for a new patch.

## Credits

- [StranikS-Scan / WorldOfTanks-Decompiled](https://github.com/StranikS-Scan/WorldOfTanks-Decompiled) — decompiled game sources
- [ModsSettings API](https://github.com/izeberg/modssettingsapi) — mod configuration menu
- [LockBlock-dev](https://github.com/LockBlock-dev/wot-mods/tree/master/auto-packer) — original packer script
