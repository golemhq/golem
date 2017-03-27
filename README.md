Golem - Test Automation Framework
==================================================

Intro
--------------------------------------

Golem is a test automation framework for functional tests that uses keyworddriven, datadriven and Page Objects patterns. I'ts written in python and uses Selenium-Webdriver as the automation engine.

Installation
--------------------------------------

Golem works with Python 3.5+, you may download and install it from here [python.org/downloads/](http://www.python.org/downloads/) 


##### **1. Clone the Golem repo and install**

First, Create a directory anywhere in your system:

```
mkdir golem && cd golem
```

```
git clone https://github.com/lucianopuccio/Golem.git .
```


##### **2. Using virtualenv**

It is optional but recommended to install Golem and it's dependencies in a [virtual environment](http://www.virtualenv.org/en/latest/) instead of globally.

```
virtualenv env
```

- **Windows**:

```
env\scripts\activate
```

- **Mac/Linux**:

```
source env/bin/activate
```

##### **3. Install Golem from source**

```
cd golem
```

```
python setup.py install
```

QuickStart
--------------------------------------
##### **1. Create the test projects root directory**

A directory must be created to contain the project, tests and required files. Open a console wherever you want the new directory to be.


Create the test directory:

```
golem-admin createdirectory <directory_name>
```

This will create a folder for all subsequent projects.


##### **2. Create a new project**

Next, create a **new** test project inside the test directory
```
cd <directory_name>
```
```
python golem.py createproject <project_name>
```

##### **3. Start the GUI**

To start the Golem GUI run the following command:

```
python golem.py gui
```

The GUI can be accessed at http://localhost:5000/

By default, this is the first user available: user: **admin** / password: **admin**

To add or edit users, the following file must be editted: _<test_directory>/users.json_

<br>

See the full documentation: [https://github.com/lucianopuccio/golem/wiki/Golem---Documentation](https://github.com/lucianopuccio/golem/wiki/Golem---Documentation)
