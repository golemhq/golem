from golem.core import test_execution
from golem import gui


def run_gui(port_number, debug):
    gui.root_path = test_execution.root_path
    gui.app.run(debug=debug, host='0.0.0.0', port=port_number)