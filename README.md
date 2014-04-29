Golem - Test Automation Framework
==================================================

Intro
--------------------------------------

Golem is a test automation framework for functional tests, with keyworddriven and datadriven aproaches built in, multiplatform, written in python and currently using Selenium-Webdriver tool to fuel the automation engine.

**Important!** Golem is currently in alpha stage, so handle with care. Test it if you may, and feel free to submit any issue/improvement.


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

With **Windows**:

```
env\scripts\activate
```

With **Unix**:

```
source env/bin/activate
```

 - **Install Golem from source**

```
cd golem
```

```
python setup.py develop
```

QuickStart
--------------------------------------
 - **Create the test projects root directory**

Create a new directory anywhere in your system:

```
mkdir testroot && cd testroot
```

Create a **new** test project inside the test projects root

```
python golem-admin.py create <project name>
```

This will create a folder structure for the selected project name.

To create a **demo** project that is ready to run and experiment, execute the following:

```
python golem-admin.py create demo
```

To execute a test run the following command:

```
python golem.py wiki search_article
```

To start the Golem GUI run the following command:

```
python golem.py gui
```

Ways to colaborate
---------------------------------

You can ubmit issues or feature requests directly into the issues page:

