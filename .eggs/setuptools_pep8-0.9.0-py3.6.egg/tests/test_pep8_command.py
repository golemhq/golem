#!/usr/bin/env python
# encoding: utf-8


import unittest
import subprocess
import setuptools
from tempfile import TemporaryFile
from os.path import abspath, join, dirname
from setuptools_pep8.setuptools_command import Pep8Command


FIXTURES_DIR = abspath(join(dirname(__file__), "fixtures"))


class SetupCfgDirectives(unittest.TestCase):

    def test_case_is_setup_correctly(self):
        self.assertTrue(issubclass(Pep8Command, setuptools.Command))

    def test_can_use_excludes_parameter_in_setup_cfg(self):
        cmdline = "python setup.py pep8".split()
        with TemporaryFile() as stdout_stderr:
            return_code = subprocess.call(cmdline, stdout=stdout_stderr, stderr=subprocess.STDOUT, cwd=FIXTURES_DIR)
            stdout_stderr.seek(0)
            output = stdout_stderr.read()
        self.assertNotEqual(0, return_code)
        self.assertNotIn("excdir", output)
        self.assertIn("incdir", output)


if __name__ == '__main__':
    unittest.main()
