from debug_utils import LOG_NOTE

from gui.hidedecorativecrosshairs import config
from gui.hidedecorativecrosshairs.override_utils import override, restore

PANEL_MODULE = (
    "gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.panels."
    "decorative_crosshairs_panel"
)

_overrides = []


def _is_installed():
    return bool(_overrides)


def _patched_add_mechanic_ui_components(original, self, mechanicComponents):
    # A panel that outlives uninstall() still holds this function as its class
    # attribute until restore runs, so check before filtering.
    if not _is_installed() or not config.is_enabled():
        return original(self, mechanicComponents)
    kept = tuple(name for name in mechanicComponents if not config.is_hidden(name))
    return original(self, kept)


def _load_panel_class():
    try:
        module = __import__(PANEL_MODULE, fromlist=["DecorativeCrosshairPanel"])
    except ImportError:
        return None
    return getattr(module, "DecorativeCrosshairPanel", None)


def install():
    if _is_installed():
        return True

    panel_cls = _load_panel_class()
    if panel_cls is None or "_addMechanicUIComponents" not in vars(panel_cls):
        LOG_NOTE(
            "Hide Decorative Crosshairs: DecorativeCrosshairPanel not found, "
            "this client is not supported"
        )
        return False

    _overrides.append(
        override(
            panel_cls,
            "_addMechanicUIComponents",
            _patched_add_mechanic_ui_components,
        )
    )
    return True


def uninstall():
    while _overrides:
        restore(_overrides.pop())
