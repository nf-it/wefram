
__all__ = [
    'ensure_apps_loaded'
]


STATE = {
    'loaded': False
}


def ensure_apps_loaded() -> None:
    """ Ensures that all apps been loaded prior to return from this function.
    This routine does nothing if been executed before even once. """

    from ... import run

    if STATE['loaded']:
        return

    run.start()
    STATE['loaded'] = True

