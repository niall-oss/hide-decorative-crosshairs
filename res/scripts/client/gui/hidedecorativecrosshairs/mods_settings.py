from debug_utils import LOG_NOTE

from gui.hidedecorativecrosshairs import config

MOD_LINKAGE = "hide_decorative_crosshairs"
SETTINGS_VERSION = 2

HINT_TOOLTIP = (
    "{HEADER}Decorative crosshairs{/HEADER}"
    "{BODY}Some vehicle mechanics draw an extra overlay around your reticle. "
    "Ticked overlays are not shown. The mechanic itself, including any "
    "accuracy bonus, is unchanged. Changes apply from your next battle.{/BODY}"
)

CHECKBOX_TOOLTIP = (
    "{HEADER}%s{/HEADER}{BODY}%s Hiding it does not change how the "
    "mechanic works.{/BODY}"
)

_api = None


def _get_mods_settings_api():
    try:
        from gui.modsSettingsApi import g_modsSettingsApi
    except ImportError:
        return None
    return g_modsSettingsApi


def _build_template():
    from gui.modsSettingsApi import templates

    column1 = [
        templates.createLabel("Hide these reticle overlays:", tooltip=HINT_TOOLTIP),
    ]
    for name, label, description in config.KNOWN_COMPONENTS:
        column1.append(
            templates.createCheckbox(
                label,
                name,
                config.is_hidden(name),
                tooltip=CHECKBOX_TOOLTIP % (label, description),
            )
        )

    return {
        "modDisplayName": "Hide Decorative Crosshairs",
        "settingsVersion": SETTINGS_VERSION,
        "enabled": config.is_enabled(),
        "column1": column1,
        "column2": [],
    }


def _apply_settings(settings):
    known = set(component[0] for component in config.KNOWN_COMPONENTS)
    # Names added by hand to config.json have no checkbox; keep them.
    hidden = [name for name in config.hidden_components() if name not in known]
    for name, _, _ in config.KNOWN_COMPONENTS:
        if settings.get(name, config.is_hidden(name)):
            hidden.append(name)

    config.apply_values(
        enabled=settings.get("enabled", config.is_enabled()), hidden=hidden
    )


def _on_settings_changed(linkage, settings):
    if linkage != MOD_LINKAGE:
        return
    _apply_settings(settings)


def register_mods_settings():
    global _api

    if _api is not None:
        return True

    api = _get_mods_settings_api()
    if api is None:
        LOG_NOTE(
            "ModsSettings API not installed. Configure hidden overlays via "
            "mods/configs/ANIALLATOR.hide_decorative_crosshairs/config.json"
        )
        return False

    _api = api
    template = _build_template()
    saved = api.getModSettings(MOD_LINKAGE, template)

    if saved:
        api.registerCallback(MOD_LINKAGE, _on_settings_changed)
        _apply_settings(saved)
    else:
        settings = api.setModTemplate(MOD_LINKAGE, template, _on_settings_changed)
        if settings:
            _apply_settings(settings)
    return True


def unregister_mods_settings():
    global _api

    if _api is None:
        return

    # ModsSettings API has no unregister call; this mirrors registerCallback.
    _api.onSettingsChanged -= _on_settings_changed
    _api = None
