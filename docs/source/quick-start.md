Quick Start
==================================================

Let's create a Test Directory, a new Project inside of it and start the Golem Web Module.

##### Create a Test Directory

The **Test Directory** holds one or more projects that you will work on and all the required files. To create a Test Directory, open a console wherever you want the new directory to be and execute this command:

```
golem-admin createdirectory <directory_name>
```

This will create a folder that will contain all subsequent projects.


##### Create a new project

Next, create a new **project** inside the test directory

```
cd <directory_name>
python golem.py createproject <project_name>
```

##### Start the Web Module

To start the Golem Web Module, run the following command:

```
python golem.py gui
```

The Web Module can be accessed at [http://localhost:5000/](http://localhost:5000/)

By default, the following user is available: username: **admin** / password: **admin**

Next, go to [Adding Tests](adding-tests.html)
