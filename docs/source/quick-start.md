Quick Start
==================================================

Let's create a Test Directory, a new Project inside of it and start the Golem Web Module.

##### Create a Test Directory

The **Test Directory** holds one or more projects that you will work on and all the required files. To create a Test Directory, open a console wherever you want the new directory to be and execute this command:

```
golem-admin createdirectory <directory_name>
```

This will create a folder that will contain all subsequent projects.


##### Download the Webdriver Executables

Golem needs the latest webdrivers in order to work, by default, it will pick up the executables placed in the *<test_directory>/drivers directory*, this setting can be overriden from the settings.
The latests versions of the webdrivers can be found here:
* Chrome: [https://sites.google.com/a/chromium.org/chromedriver/](https://sites.google.com/a/chromium.org/chromedriver/)
* Firefox: [https://github.com/mozilla/geckodriver/releases](https://github.com/mozilla/geckodriver/releases)

For more detailed information, check [this page](web-drivers.html)


##### Start the Web Module

To start the Golem Web Module, run the following command:

```
golem gui
```

The Web Module can be accessed at [http://localhost:5000/](http://localhost:5000/)

By default, the following user is available: username: **admin** / password: **admin**


##### Create a new project

Next, create a new **project** inside the test directory

```
cd <directory_name>
golem createproject <project_name>
```

Or, create a new project using the Web Module:

![add-project](_static/img/add-project.png "Add Project")


Next, go to [Adding Tests](adding-tests.html)
