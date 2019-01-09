The CLI
==================================================

The list of available Golem CLI commands:


## golem-admin

### createdirectory

**golem-admin createdirectory \<name\>**

Used to generate a new test directory.
Name must be a relative or absolute path for the new test directory. Use '.' to use CWD.


## golem

### run

See [Running Tests](../running-tests.html)

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

To learn more about the Webdriver Manager see: <https://github.com/golemhq/webdriver-manager>.
