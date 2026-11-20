from debug_utils import LOG_NOTE

from gui.hidedecorativecrosshairs import config
from gui.hidedecorativecrosshairs.override_utils import override, restore

PANEL_MODULE = (
    "gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.panels."
    "decorative_crosshairs_panel"
)
GUN_MARKER_FACTORY_MODULE = "gui.Scaleform.daapi.view.battle.shared.crosshair.gm_factory"

_overrides = []


def _is_installed():
    return bool(_overrides)


def _is_active():
    # Game objects that outlive uninstall() can still reach a wrapper they
    # looked up earlier, so every wrapper checks this first.
    return _is_installed() and config.is_enabled()


def _patched_add_mechanic_ui_components(original, self, mechanicComponents):
    if not _is_active():
        return original(self, mechanicComponents)
    kept = tuple(name for name in mechanicComponents if not config.is_hidden(name))
    return original(self, kept)


def _patched_create_accuracy_gun_markers(original, self):
    if not _is_active() or not config.uses_default_gun_marker():
        return original(self)
    return self._createDefaultMarkers()


_TARGETS = (
    (
        PANEL_MODULE,
        "DecorativeCrosshairPanel",
        "_addMechanicUIComponents",
        _patched_add_mechanic_ui_components,
    ),
    (
        GUN_MARKER_FACTORY_MODULE,
        "_ControlMarkersFactory",
        "_createAccuracyGunMarkers",
        _patched_create_accuracy_gun_markers,
    ),
)


def _load_class(module_name, class_name):
    try:
        module = __import__(module_name, fromlist=[class_name])
    except ImportError:
        return None
    return getattr(module, class_name, None)


def install():
    if _is_installed():
        return True

    for module_name, class_name, method_name, wrapper in _TARGETS:
        cls = _load_class(module_name, class_name)
        if cls is None or method_name not in vars(cls):
            LOG_NOTE(
                "Hide Decorative Crosshairs: %s.%s not found, this client is "
                "not supported" % (class_name, method_name)
            )
            continue
        _overrides.append(override(cls, method_name, wrapper))
    return _is_installed()


def uninstall():
    while _overrides:
        restore(_overrides.pop())
