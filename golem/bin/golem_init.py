"""A CLI script to start golem from any location
"""
import os
import sys
import subprocess

from golem.main import execute_from_command_line


def main():
    # Starting the gui using the console script: 'golem gui'
    # won't work in windows there is a bug in windows when
    # starting the flask app from a console script
    # (setup.py, console_scripts) check out
    # https://github.com/pallets/werkzeug/issues/1136
    #
    # In the meantime, for windows, ensure that the 'golem_start.py'
    # file is present otherwise create it first and use it to
    # kickstart golem.
    # TODO
    if os.name == 'nt':
        path = os.path.join(os.getcwd(), 'golem_start.py') 
        if not os.path.isfile(path):
            golem_start_py_content = ("import os\n\n"
                                      "from golem.main import execute_from_command_line"
                                      "\n\n"
                                      "if __name__ == '__main__':\n"
                                      "    execute_from_command_line(os.getcwd())\n")
            with open(path, 'w') as golem_start_file:
                golem_start_file.write(golem_start_py_content)

        del sys.argv[0]
        cmd_list = ['python', 'golem_start.py'] + sys.argv
        subprocess.call(cmd_list)
    else:
        execute_from_command_line(os.getcwd())
