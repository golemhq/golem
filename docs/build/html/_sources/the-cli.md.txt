The CLI
==================================================


##### Commands for golem-admin:

**golem-admin createdirectory name**

Used to generate a new test directory.


##### Commands for golem.py:

**python golem.py run project \<test\>|\<suite\> [-t|--threads -d|--driver]**

Run a test case or test suite from a project. Threads indicates the amount of test cases to execute in parallel, default is 1. Driver indicates wich driver to use to run the tests, options are: firefox, chrome, default is firefox. Chrome requires chrome_driver_path setting to be defined in the settings file.

**python golem.py gui [-p|--port]**

Start Golem Web Module (GUI). Port indicates which port number to use, default is 5000.

**python golem.py createproject \<project name\>**

Creates a new project with the given name. Creates the base files and folders.

**python golem.py createtest \<project name\> \<test name\>**

Creates a new test inside the given project.

**python golem.py createsuite \<project name\> \<suite name\>**

Creates a new suite inside the given project.

**python golem.py createuser \<username\> \<password\> [-a|--admin -p|--projects -r|--reports]**

Add a new user, projects is a list of projects that the user can access and reports determines which project reports the user can see. In both cases use '*' to give the user access to all projects


Next, go to [The Web Module](the-web-module.html)