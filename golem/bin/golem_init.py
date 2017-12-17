"""A CLI script to start golem from any location
"""
import os

from golem.main import execute_from_command_line


def main():
    execute_from_command_line(os.getcwd())
