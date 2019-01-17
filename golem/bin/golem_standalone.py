"""Golem standalone script

Use PyInstaller to generate an executable:

pyinstaller golem/bin/golem_standalone.py --distpath . --onefile -n golem
  --add-data "golem/gui/templates:golem/gui/templates"
  --add-data "golem/gui/static:golem/gui/static"

Note: use `;` (semi-colon) instead of `:` (colon) in Windows
"""
import os
import sys
from multiprocessing import freeze_support

from golem.main import execute_from_command_line
from golem.bin import golem_admin
from webdriver_manager.main import main as webdriver_manager_main
from golem.cli.messages import STANDALONE_USAGE


if __name__ == '__main__':
    freeze_support()
    if len(sys.argv) > 1:
        if sys.argv[1] in ['golem-admin', 'admin']:
            del sys.argv[1]
            golem_admin.main()
        elif sys.argv[1] == 'webdriver-manager':
            del sys.argv[1]
            webdriver_manager_main()
        else:
            execute_from_command_line(os.getcwd())
    else:
        print(STANDALONE_USAGE)
