import threading, webbrowser

from golem.core import test_execution
from golem import gui


def open_app_in_browser(url):
    browser = webbrowser.open(url, new=2)


def run_gui(port, debug, open_app):
    host = '0.0.0.0'
    url = 'http://{}:{}/'.format(host, port)
    gui.root_path = test_execution.root_path
    if open_app:
        threading.Timer(1.25, open_app_in_browser, args=[url]).start()
    gui.app.run(debug=debug, host=host, port=port)


