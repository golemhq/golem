Installation
==================================================

##### Requirements

**Python**

Golem requires Python 3.4 or higher.

- Windows:

The Windows installer works fine, you can get it from here: [python.org/downloads/](http://www.python.org/downloads/)

- Mac:

To install on Mac OS follow this instructions: [Installing Python 3 on Mac OS X](http://python-guide-pt-br.readthedocs.io/en/latest/starting/install3/osx/)

- Linux:

Debian 8 and Ubuntu 14.04 comes with Python 3.4 pre-installed, newer Linux distributions might come with newer Python versions. 

Since Linux tends to have both Python 2 and 3 installed alongside eachother, the command to execute the latter should be 'python3' instead of just 'python'.

**PIP**

PIP is the package manager for Python and is required to install Golem and it's dependencies. Check if you already have it, it come bundled with the newer versions of Python.

```
pip --version

or

pip3 --version
```

If you don't have PIP installed, follow [these instructions](https://pip.pypa.io/en/stable/installing/).


##### Using virtualenv (optional)

It is recommended to install Golem and it's dependencies in a [virtual environment](http://www.virtualenv.org/en/latest/) instead of globally. To do that, follow this steps:

Install virtualenv

```
pip install virtualenv
```

Create a new virtualenv in the 'env/' folder

```
virtualenv env
```

If the virtual environment is not created with Python 3 you should instead use the following command:

```
virtualenv env -p python3
```


- **Windows**:

```
env\scripts\activate
```

- **Mac/Linux**:

```
source env/bin/activate
```

##### Install Using PIP

The quickest and the prefered way to install Golem.

```
pip install golem-framework
```


##### Install From Source

Only install from source if you need the latest development version.

**1. Clone the Golem repo locally**

```
git clone https://github.com/lucianopuccio/Golem.git golem
```

**2. Install using setup.py**

```
cd golem
python setup.py install
```

<br>

Next, go to [Quick Start](quick-start.html)