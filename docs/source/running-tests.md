Running tests
==================================================

## Run from the Command Line

The command to run tests or suites from the command line:

```bash
golem run <project> <test|suite|dir> [-b|--browsers] [-t|--threads]
          [-e|--environments] [-i|--interactive]
```

**-b|--browsers**

One or more browsers to use for these tests.
If not provided, the browsers defined inside the suite will be used.
If the suite does not have browsers defined or this is a test, the *default_browser* setting will be used.
The valid options are listed [here](browsers.html#specifying-the-browser-for-a-test).

**-t|--threads**

The number of tests to run in parallel. The default is 1.

**-e|--environments**

The environments to use for this execution.
If not provided, the environments defined inside the suite will be used.

**-i|--interactive**

Run the test in interactive mode.
This is required for the *interactive_mode* and *set_trace* actions.


### Run a single test

```bash
golem run project test_name
golem run project test_name.py
golem run project folder.test_name
golem run project folder/test_name.py
```

All paths are relative to the *project/tests/* folder.

### Run a suite

```bash
golem run project suite_name
golem run project suite_name.py
golem run project folder.suite_name
golem run project folder/suite_name.py
```

All paths are relative to the *project/suites/* folder.

### Run every test in a directory

```bash
golem run project folder/
golem run project .         ## run every test
```

All paths are relative to the *project/tests/* folder.