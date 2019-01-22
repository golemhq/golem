"""CLI script to start golem"""
import os
import sys

from golem.main import execute_from_command_line


def main():
    sys.dont_write_bytecode = True
    execute_from_command_line(os.getcwd())
