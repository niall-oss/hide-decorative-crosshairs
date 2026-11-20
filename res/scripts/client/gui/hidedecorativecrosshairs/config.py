import json
import os

try:
    _STRING_TYPES = (basestring,)  # noqa: F821 - Python 2 client
except NameError:
    _STRING_TYPES = (str,)

CONFIG_DIR = "mods/configs/ANIALLATOR.hide_decorative_crosshairs"
CONFIG_FILE = CONFIG_DIR + "/config.json"

# Values of DECORATIVE_CROSSHAIR_CONSTS, keyed to the mechanic that adds them.
KNOWN_COMPONENTS = (
    ("accuracy", "Accuracy Stacks"),
    ("fury", "Battle Fury"),
    ("concentration", "Concentration Mode"),
    ("temperatureGunOverheat", "Gun Overheat"),
    ("overheat", "Overheat Stacks"),
    ("pillboxSiege", "Pillbox Siege Mode"),
)

DEFAULTS = {
    "enabled": True,
    "hidden": ["accuracy"],
}

_enabled = DEFAULTS["enabled"]
_hidden = list(DEFAULTS["hidden"])


def _parse_hidden(value):
    if not isinstance(value, list):
        return list(DEFAULTS["hidden"])
    names = []
    for name in value:
        if isinstance(name, _STRING_TYPES) and name and name not in names:
            names.append(str(name))
    return names


def load():
    global _enabled, _hidden

    if not os.path.isfile(CONFIG_FILE):
        save()
        return

    try:
        with open(CONFIG_FILE, "r") as handle:
            data = json.load(handle)
    except (IOError, ValueError):
        data = {}
    if not isinstance(data, dict):
        data = {}

    _enabled = bool(data.get("enabled", DEFAULTS["enabled"]))
    _hidden = _parse_hidden(data.get("hidden", DEFAULTS["hidden"]))


def save():
    if not os.path.isdir(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

    with open(CONFIG_FILE, "w") as handle:
        json.dump({"enabled": _enabled, "hidden": _hidden}, handle, indent=2)


def is_enabled():
    return _enabled


def hidden_components():
    return tuple(_hidden)


def is_hidden(name):
    return name in _hidden


def apply_values(enabled=None, hidden=None):
    global _enabled, _hidden

    if enabled is not None:
        _enabled = bool(enabled)
    if hidden is not None:
        _hidden = _parse_hidden(list(hidden))

    save()
