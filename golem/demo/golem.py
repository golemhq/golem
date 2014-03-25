#!/usr/bin/env python
import os
import sys

sys.dont_write_bytecode = True #remove for performance

if __name__ == "__main__":
    del sys.path[0]
    sys.path.append('')
    from golem.main import execute_from_command_line    

    execute_from_command_line()
