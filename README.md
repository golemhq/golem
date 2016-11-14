Golem - Test Automation Framework
==================================================

Intro
--------------------------------------

Golem is a test automation framework for functional tests, with keyworddriven, datadriven and Page Objects pattern built in, written in python and Selenium-Webdriver as the automation engine.


Installation
--------------------------------------

Currently Golem is only guaranteed to work with Python 2.7, you may download and install it from here [python.org/downloads/](http://www.python.org/downloads/) 


 - **Clone the Golem repo and install**

Create a directory anywhere in your system:

```
mkdir golemroot && cd golemroot
```

```
git clone https://github.com/lucianopuccio/Golem.git
```


 - **Using virtualenv**

It is optional but recommended to install Golem and it's dependencies in a [virtual environment](http://www.virtualenv.org/en/latest/) instead of globally.

```
virtualenv env
```

**Windows**:

```
env\scripts\activate
```

**Linux**:

```
source env/bin/activate
```

 - **Install Golem from source**

```
cd golem
```

```
python setup.py install
```

QuickStart
--------------------------------------
 - **Create the test projects root directory**

You need to create a new projects directory to hold the test cases and required files. Open a console wherever you want the new directory

Create a **new** test project inside the test projects root

```
golem-admin startdirectory <directory name>
```

This will create a folder for all subsequent projects.

 - **Create a new project**
 ```
golem-admin createdirectory <directory name>
```

==============

To start the Golem GUI run the following command:

```
python golem.py gui
```

