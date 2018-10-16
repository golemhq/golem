Running tests
==================================================

## Run from the Command Line

The command to run tests or suites from the command line is:

```bash
golem run <project> <test|suite|dir> [-b|--browsers] [-t|--threads]
          [-e|--environments] [-i|--interactive]
```

**-b|--browsers**

One or more browsers to use for this tests.
If not provided, the browsers defined inside the suite will be used.
If the suite does not have browsers defined or this is a test, the *default_browser* setting will be used.
The valid options are listed [here](browsers.html#specifying-the-browser-for-a-test).

**-t|--threads**

The amount of tests to run in parallel. The default is 1.

**-e|--environments**

The environments to use for this execution.
If not provided, the environments defined inside the suite will be used.

**-i|--interactive**

Run the test in interactive mode.
This is required for the *interactive_mode* and *set_trace* actions. 
