Installation
==================================================

## Requirements

### Python

Golem requires Python 3.5 or higher.

**Windows**:

The Windows installer works fine, you can get it from here: [python.org/downloads/](http://www.python.org/downloads/)

**Mac**:

To install on Mac OS follow these instructions: [Installing Python 3 on Mac OS X](http://python-guide.readthedocs.io/en/latest/starting/install3/osx/)

**Linux**:

Debian 8 and Ubuntu 14.04 comes with Python 3.4 pre-installed, newer Linux distributions might come with newer Python versions. 

Since Linux tends to have both Python 2 and 3 installed alongside each other, the command to execute the latter should be 'python3' instead of just 'python'.

### PIP

PIP is the package manager for Python. It is required to install Golem and its dependencies. Check if you already have it. PIP comes bundled with the newer versions of Python.

```
pip --version
```
or
```
pip3 --version
```

If you don't have PIP installed, follow [these instructions](https://pip.pypa.io/en/stable/installing/).


## Create a Virtual Environment

It is recommended to install Golem and its dependencies in a [virtual environment](http://www.virtualenv.org/en/latest/) instead of globally. To do that, follow these steps:

### Install Virtualenv

```
pip install virtualenv
```

Create a new virtualenv in the './env' folder

```
virtualenv env
```

If the virtual environment is being created with Python 2 instead of 3, use the following command instead:

```
virtualenv env -p python3
```

### Activate the Environment

To use a virtual environment it needs to be activated first.

**Windows**:

```
env\scripts\activate
```

**Mac/Linux**:

```
source env/bin/activate
```

## Install Golem Using PIP

The quickest and the preferred way to install Golem.

```
pip install golem-framework
```


## Installing From Source

```
pip install -U https://github.com/golemhq/golem/archive/master.tar.gz
```
