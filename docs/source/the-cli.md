The CLI
==================================================

All the tasks in Golem can be done using the command line. This are the available commands:


##### Commands for golem-admin:

**golem-admin createdirectory \<name\>**

Used to generate a new test directory.


##### Commands for golem.py:

**python golem.py run project \<test\>|\<suite\> [-t|--threads -b|--browsers -i|--interactive -e|--environments]**

Run a test case or test suite from a project. 

Threads indicates the amount of test cases to execute in parallel, default is 1. 

Browsers indicates wich browser(s) to use, options are: chrome, firefox, chrome-remote, chrome-headless, chrome-remote-headless, firefox-remote, default is chrome, it accepts one or more browsers, like so:

```
>python golem.py run project_name test_name -b firefox chrome
```

Note: the test will be run once per each browser defined.

Environments can be a list of environments defined in the environments.json. If not provided it will try to use the first if possible.

```
>python golem.py run project_name test_name -e test stage
```

See [Managing Environments](environments.html) for more detail.


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

<br>

Next, go to [The Web Module](the-web-module.html)