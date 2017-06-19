import os
import sys


# deactivate .pyc extention file generation
sys.dont_write_bytecode = True


if __name__ == '__main__':
    del sys.path[0]
    sys.path.append('')

    from golem.main import execute_from_command_line

    execute_from_command_line(os.getcwd())
