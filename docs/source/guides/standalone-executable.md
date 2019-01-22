Generate a Standalone Executable
==================================================

## Using PyInstaller

A Golem standalone executable without any dependencies (including Python) can be generated using [PyInstaller](https://pyinstaller.readthedocs.io/).

Note: the executable must be generated in the same platform that it will be used (e.g.: Windows 10 64 with Python 3.7)

### Steps

Create an empty virtualenv (having the required packages only reduces the final executable size):

```
virtualenv env
```

Clone the repo and install:

```
git clone https://github.com/golemhq/golem.git
cd golem
pip install .
```

Install PyInstaller

```
pip install pyinstaller
```

Install python3-dev if needed (Linux)
```
apt-get install python3-dev
```

Generate the executable

Linux:
```
pyinstaller golem/bin/golem_standalone.py --onefile -n golem --add-data "golem/gui/templates:golem/gui/templates" --add-data "golem/gui/static:golem/gui/static"
```

Windows:
```
pyinstaller golem\bin\golem_standalone.py --onefile -n golem --add-data "golem\gui\templates;golem\gui\templates" --add-data "golem\gui\static;golem\gui\static"
```

Where:

```--onefile``` generates a single file instead of a folder

```-n golem``` is the name of the executable

```--add-data``` includes the templates and static files required by the GUI

The executable is generated in the *dist* folder.


## How to Use the Standalone Executable

Put the executable in your path.

The executable includes the *golem*, *golem-admin*, and *webdriver-manager* interfaces.

Usage:

```
golem golem-admin createdirectory .
golem webdriver-manager update
golem gui
golem run project test
```
