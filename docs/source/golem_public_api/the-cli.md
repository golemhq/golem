The CLI
==================================================

The list of available Golem CLI commands:


## golem-admin

### createdirectory

**golem-admin createdirectory \<name\>**

Used to generate a new test directory.


## golem

### run

**golem run \<project\> \<test\>|\<suite\> [-t|--threads -b|--browsers -e|--environments -i|--interactive ]**

Run a test case or suite from a project. 

Threads indicates the amount of test cases to execute in parallel, default is 1. 

Browsers indicates which browser(s) to use:

```
golem run project_name test_name -b firefox chrome
```

Environments can be a list of environments defined in the environments.json. If not provided it will try to use the first if possible.
See [Test Data - Environments](test-data.html#environments) for more detail.

Interactive runs the test in interactive mode. Required for *interactive_mode* and *set_trace* actions.

### gui

**golem gui [-p|--port]**

Start Golem Web Module (GUI). Port indicates which port number to use, default is 5000.

### createproject

**golem createproject \<project name\>**

Creates a new project with the given name. Creates the base files and folders.

### createtest

**golem createtest \<project name\> \<test name\>**

Creates a new test inside the given project.

### createsuite

**golem createsuite \<project name\> \<suite name\>**

Creates a new suite inside the given project.

### createuser

**golem createuser \<username\> \<password\> [-a|--admin -p|--projects -r|--reports]**

Add a new user, projects is a list of projects that the user can access and reports determines which project reports the user can see. In both cases use '*' to give the user access to all projects

## webdriver-manager

### update

**webdriver-manager update -b chrome**

To learn more about the Webdriver Manager see: <https://github.com/lucianopuccio/webdriver-manager>.
