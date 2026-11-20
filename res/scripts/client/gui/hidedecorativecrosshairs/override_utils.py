from debug_utils import LOG_NOTE

_MISSING = object()


class Override(object):
    def __init__(self, holder, name, previous, installed):
        self.holder = holder
        self.name = name
        self.previous = previous
        self.installed = installed


def override(holder, name, wrapper):
    previous = vars(holder).get(name, _MISSING)
    target = getattr(holder, name)

    def wrapped(*args, **kwargs):
        return wrapper(target, *args, **kwargs)

    installed = staticmethod(wrapped) if isinstance(previous, staticmethod) else wrapped
    setattr(holder, name, installed)
    return Override(holder, name, previous, installed)


def restore(handle):
    # Another mod may have wrapped our wrapper; removing ours would drop theirs.
    if vars(handle.holder).get(handle.name) is not handle.installed:
        LOG_NOTE(
            "Hide Decorative Crosshairs: %s was overridden again by another mod, "
            "leaving it in place" % handle.name
        )
        return False

    if handle.previous is _MISSING:
        delattr(handle.holder, handle.name)
    else:
        setattr(handle.holder, handle.name, handle.previous)
    return True
