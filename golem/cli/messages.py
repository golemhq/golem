
USAGE_MSG = """
Usage: golem

  golem run <project> <test|suite|dir> [-b -t -e]
  golem gui [-p]
  golem createproject <project>
  golem createtest <project> <test>
  golem createsuite <project> <suite>
  golem createuser <username> <password> [-a -p -r]

Usage: golem run

  Run tests or suites

  positional arguments:
    projects            name of the project
    test|suite|dir      name of a single test, a suite or a
                        directory of tests.

  optional arguments:
    -b, --browsers      a list of browsers
    -t, --threads       amount of threads, default is 1
    -e, --environments  a list of environments

Usage: golem gui
  
  Start the Golem GUI module

  optional arguments:
    -p, --port          which port to use, default is 5000

Type: golem -h <command> for more help
"""

RUN_USAGE_MSG = """
Usage: golem run <project> <test|suite|dir> [-b|--browsers]
                 [-t|--threads] [-e|--environments]
                 [-i|--interactive]

  Run tests, suites or entire test directories

  positional arguments:
    project             name of the project
    test|suite|dir      name of a single test, a suite or a
                        directory of tests.

  optional arguments:
    -b, --browsers      a list of browsers
    -t, --threads       amount of threads, default is 1
    -e, --environments  a list of environments
    -i, --interactive   run in interactive mode
"""

GUI_USAGE_MSG = """
Usage: golem gui [-p|--port]
  
  Start the Golem GUI module

  optional arguments:
    -p, --port          which port to use, default is 5000
"""

CREATEPROJECT_USAGE_MSG = """
Usage: golem createproject <project>
  
  Create a new project

  positional arguments:
    project             project name
"""

CREATETEST_USAGE_MSG = """
Usage: golem createtest <project> <test>
  
  Create a new test inside a project

  positional arguments:
    project             an existing project name
    test                the name of the new test. Use dots
                        to create inside sub-folders.
"""

CREATESUITE_USAGE_MSG = """
Usage: golem createsuite <project> <suite>
  
  Create a new test suite inside a project

  positional arguments:
    project             an existing project name
    suite               the name of the new suite. Use dots
                        to create inside sub-folders.
"""

CREATEUSER_USAGE_MSG = """
Usage: golem createuser <username> <password> [-a|--admin]
                        [-p|--projects] [-r|--reports]
  
  Create a new user

  positional arguments:
    username            the username of the user
    password            the password of the user

  optional arguments:
    -a, --admin         make the user admin. Admin users
                        have access to all projects.
    -p, --projects      a list of projects to give the user
                        access
    -r, --reports       a list of projects to give the user
                        access to the reports
"""

ADMIN_USAGE_MSG = """
Usage: golem-admin

  golem-admin createdirectory <directory-name>

  Create a new directory with the structure and files
  required for golem projects.
"""
