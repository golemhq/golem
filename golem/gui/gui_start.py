"""A function to start the GUI application."""
import sys
import os

from golem import gui

from werkzeug import _reloader


ORIGINAL_GET_ARGS = None


def run_gui(host=None, port=5000, debug=False):
    # Patch Werkzeug._reloader._get_args_for_reloading()
    # The Flask development server reloader does not work when
    # started from the Golem standalone (PyInstaller) in Linux
    # TODO
    patch_werkzeug_get_args_for_reloading_wrapper()
    app = gui.create_app()
    app.run(host=host, port=port, debug=debug)


def patch_werkzeug_get_args_for_reloading_wrapper():
    global ORIGINAL_GET_ARGS
    if ORIGINAL_GET_ARGS is None:
        ORIGINAL_GET_ARGS = _reloader._get_args_for_reloading
        _reloader._get_args_for_reloading = _get_args_for_reloading_wrapper


def _get_args_for_reloading_wrapper():
    rv = ORIGINAL_GET_ARGS()
    __main__ = sys.modules["__main__"]
    py_script = rv[1]
    if __main__.__package__ is None:
        # Executed a file, like "python app.py".
        if os.name != 'nt' and os.path.isfile(py_script) and os.access(py_script, os.X_OK):
            # The file is marked as executable. Nix adds a wrapper that
            # shouldn't be called with the Python executable.
            rv.pop(0)
    return rv
