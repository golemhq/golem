Tutorial - Part 1
==================================================

Let's create the first test in Golem and learn the main features along the way.
This tutorial assumes Golem is already installed. If not, head over to the [Installation](installation.html) section.


## Create a Test Directory

A **Test Directory** needs to be created first. This directory contains the initial folder structure and some config files.
To create a Test Directory, open a console wherever you want the new directory to be and execute this command:

```
golem-admin createdirectory <test_dir_name>
```

This will create a **testdir** folder that will be used for all subsequent projects.


## Download Webdriver

Each browser requires its own Webdriver executable.
Golem uses the [webdriver-manager](https://github.com/golemhq/webdriver-manager) tool to download these automatically.

```
cd <test_directory>
webdriver-manager update
```

The Webdriver executables are downloaded into the *drivers* folder inside the Test Directory.

The settings.json file contains a key for each browser that should point to the Webdriver file for that browser.
For example:

*settings.json*
```
{
    "chromedriver_path": "./drivers/chromedriver*"
}
```

The '\*' wildcard at the end of the path is used to match the highest version available, in the case there's more than one present.

This doesn't need to be modified unless the Webdriver files are located elsewhere.


For more detail, check [this page](browsers.html#webdriver-manager).


## Start the Web Module

To start the Golem Web Module, run the following command:

```
golem gui
```

The Web Module can be accessed at [http://localhost:5000/](http://localhost:5000/)

The following superuser is available at the start: username: **admin** / password: **admin**



## Create a New Project

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