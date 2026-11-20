__version__ = "1.0.0"


def init():
    from gui.hidedecorativecrosshairs import config
    from gui.hidedecorativecrosshairs import hooks
    from gui.hidedecorativecrosshairs.mods_settings import register_mods_settings

    config.load()
    if hooks.install():
        register_mods_settings()


def fini():
    from gui.hidedecorativecrosshairs import hooks
    from gui.hidedecorativecrosshairs.mods_settings import unregister_mods_settings

    unregister_mods_settings()
    hooks.uninstall()
