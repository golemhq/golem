#!/usr/bin/env python
# encoding: utf-8


"""Integration of PEP8 tool with Setuptools."""

import setuptools
import pep8
import sys


class Pep8Command(setuptools.Command):
    """Run PEP8 on your modules"""

    description = __doc__
    user_options = [(opt._long_opts[0][2:] + ("=" if opt.default != ("NO", "DEFAULT") else ""), None, opt.help)
                    for opt in pep8.get_parser().option_list]

    def initialize_options(self):
        # NB: These aren't used, just stops setuptools arg parser from
        #     barfing because it doesn't know pep8's options
        for opt in self.user_options:
            setattr(self, opt[0].replace("-", "_").rstrip("="), None)

    def finalize_options(self):
        pass

    def run(self):
        sys.argv = sys.argv[1:] + ["."]
        pep8._main()
