Tutorial - Part 1
==================================================

Let's create the first test in Golem and learn the main features along the way.
This tutorial assumes Golem is already installed. If not, head over to the [Installation](installation.html) section.


## Create a Test Directory

A **Test Directory** needs to be created first. This directory contains the initial folder structure and some config files.
To create a Test Directory, open a console wherever you want the new directory to be and execute this command:

```
golem-admin createdirectory testdir
```

This will create a **testdir** folder that will be used for all subsequent projects.


## Download Webdriver Executables

Each browser requires its own Webdriver executable. Golem uses the webdriver-manager tool to download these automatically.

```
cd <test_directory>
webdriver-manager update
``` 

The executables can be downloaded manually from these locations:

* Chrome: <https://sites.google.com/a/chromium.org/chromedriver/downloads>
* Firefox: <https://github.com/mozilla/geckodriver/releases>
* IE: <http://selenium-release.storage.googleapis.com/index.html>
* Edge: <https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/>
* Opera: <https://github.com/operasoftware/operachromiumdriver/releases>

By default, the executables are downloaded into the *drivers* folder inside the Test Directory.

The settings.json file contains a key for each browser that should point to the Webdriver file for that browser.
For example:

*settings.json*
```
{
    "chromedriver_path": "./drivers/chromedriver*"
}
```

Notice the '\*' wildcard at the end of the path. It is used to match the highest version available, in the case there's more than one present.

This doesn't need to be modified unless the Webdriver files are located elsewhere.


For more detail, check [this page](browsers.html#webdriver-manager).


## Start the Web Module

To start the Golem Web Module, run the following command:

```
golem gui
```

The Web Module can be accessed at [http://localhost:5000/](http://localhost:5000/)

By default, the following superuser is available: username: **admin** / password: **admin**



## Create a New Project

The tests are grouped in one or more projects. Each project, for example, can represent a module of a larger application or a different application altogether.  

A new **project** can be created by using the Web Module or by the following command:

```
cd <directory_name>
golem createproject <project_name>
```

A new project has the following structure:
```
project_name/
    pages/
    reports/
    suites/
    tests/
    environments.json
    settings.json
```


Once the test directory and the project are created you can proceed to [Tutorial - Part 2](tutorial-part-2.html)