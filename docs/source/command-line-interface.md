The CLI
==================================================

## golem-admin

### createdirectory

```
golem-admin createdirectory <name>
```

Used to generate a new test directory.
Name must be a relative or absolute path for the new test directory. Use '.' to use CWD.

## golem

### run

The command to run tests or suites from the command line:

```
golem run <project> <test|suite|directory> [-b|--browsers]
          [-p|--processes] [-e|--environments] [-t|--tags]
          [-i|--interactive] [-r|--report] [--report-folder]
          [--report-name] [--timestamp] 
```

#### -b, \-\-browsers

One or more browsers to use for the tests.
If not provided, the browsers defined inside the suite or the default browser defined in settings will be used.
The valid options are listed [here](browsers.html#valid-options).

#### -p, \-\-processes

The number of tests to run in parallel. The default is 1.

#### -e, \-\-environments

The environments to use for the execution.
If not provided, the environments defined inside the suite will be used.

#### -t, \-\-tags

Filter the tests by tags.

Example, run all tests with tag "smoke":

```
golem run project_name . --tags smoke
```

Or using a tag expression:

```
golem run project suite --tags "smoke and (regression or not 'release 001')"
```

#### -i, \-\-interactive

Run the test in interactive mode.
This is required for the *interactive_mode* and *set_trace* actions.

See [Interactive Mode](interactive-mode.html)

#### -r, \-\-report

Select which reports should be generated at the end of the execution.
Options are: *junit*, *html*, *html-no-images*, and *json*

#### \-\-report-folder

Absolute path to the generated reports.
The default is ```/<testdir>/projects/<project>/resports/<suite>/<timestamp>```

#### \-\-report-name

Name of the generated reports. The default is 'report'

#### \-\-timestamp

Used by the execution. Optional. 
The default is auto-generated with the format: 'year.month.day.hour.minutes.seconds.milliseconds' 

### gui

```
golem gui [-p|--port]
```

Start Golem Web Module (GUI). Port indicates which port number to use, default is 5000.

### createproject

```
golem createproject <project name>
```

Creates a new project with the given name. Creates the base files and folders.

### createtest

```
golem createtest <project name> <test name>
```

Creates a new test inside the given project.

### createsuite

```
golem createsuite <project name> <suite name>
```

Creates a new suite inside the given project.

### createuser

```
golem createuser <username> <password> [-a|--admin -p|--projects -r|--reports]
```

Add a new user, projects is a list of projects that the user can access and reports determines which project reports the user can see.
In both cases use '*' to give the user access to all projects

## webdriver-manager

### update

```
webdriver-manager update -b chrome
```

To learn more about the Webdriver Manager see: <https://github.com/golemhq/webdriver-manager>.
