Golem - Documentation
==================================================


# Installation
--------------------------------------

Currently Golem is only guaranteed to work with Python 3.5+, you may download and install it from here [python.org/downloads/](http://www.python.org/downloads/) 


#### 1. Clone the Golem repo and install

Create a directory anywhere in your system:

```
git clone https://github.com/lucianopuccio/Golem.git golem
```


#### 2. Using virtualenv

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

#### 3. Install Golem from source

```
cd golem
python setup.py install
```


# QuickStart
--------------------------------------
#### **1. Create the test projects root directory**

A directory must be created to contain the projects, tests and required files. Open a console wherever you want the new directory to be.


**Create the test directory:**

```
golem-admin createdirectory <directory_name>
```

This will create a folder that will contain all subsequent projects.


##### **2. Create a new project**

Next, create a **new** project inside the test directory
```
cd <directory_name>
python golem.py createproject <project_name>
```

##### **3. Start the GUI**

To start the Golem GUI run the following command:

```
python golem.py gui
```

The GUI can be accessed at http://localhost:5000/

By default, this is the first user available: user: **admin** / password: **admin**

# Automate a Test Case
--------------------------------------
To automate a test case first you must define the pages with which you are going to interact.

#### ****

# Actions
--------------------------------------


- **add_step(message='')**

Log a new step to be displayed in the report later

- **capture(message='')**

Take a screenshot of the browser, the message is optional

 - **click(element)**

Perform a click

- **close()**

Closes the webdriver browser

 - **go_to(url)**

Navigate to a URL

 - **random(args)**

Generate a random string

- **select_by_index(element, text)**

Select an option from a <select> by the index of the option

- **select_by_text(element, text)**

Select an option from a <select> by the option text

- **select_by_value(element, value)**

Select an option from a <select> by the option value. For example:
```
<select>
    <option value="AR">Argentina</option>
    <option value="BR">Brazil</option>
</select>
```

- **send_keys(element, text)**

Perform a click

- **store(key, value)**

Store a value in the given key for later use

- **verify_exists(element)**

Verify an element exists in the page

- **verify_is_enabled(element)**

Verify an element is enabled

- **verify_is_not_enabled(element)**

Verify an element is not enabled

- **verify_not_exists(element)**

Verify an element does not exist in the page

- **verify_selected_option(element, text)**

Verify that the option selected in a <select> is the one given (by the option text)

- **verify_text(text)**

Verify the given text is present anywhere on the page (entire DOM)

- **verify_text_in_element(element, text)**

Verify that an element contains the given text.

- **wait(seconds)**

Pause execution for the given amount of seconds

- **wait_for_element_visible(element, timeout)**

Pause execution for the given amount of seconds until the element is visible (default is 20 seconds)

- **wait_for_element_enabled(element, timeout)**

Pause execution for the given amount of seconds until the element is enabled (default is 20 seconds)


# Test Suite
--------------------------------------

The test is comprised of the following: list of test cases, browsers to execute and amount of workers.

When selecting all the test cases inside a folder, it can be abbreviated with the name of the folder followed by a forward dash like so: "folder_name/". An asterisc marks every test case to be executed inside the suite


# Configuration Options
--------------------------------------

- **implicit_wait**

Default time to wait looking for an element until it is found

- **screenshot_on_error**

Take a screenshot on error by default, default: false

- **screenshot_on_step**

Take a screenshot on every step, default: false

- **default_driver**

Define the driver to use, unless overriden by the -d/--driver flag

- **chrome_driver_path**

Path to the chrome driver executable. If the chromedriver is inside the test dir, it can be referenced as './chromedriver'

- **wait_hook**

Custom wait method to use before each step, must be defined inside extend.py



# Command Line
--------------------------------------

- **run project test_case|test_suite [-t|--threads -d|--driver]**

Run a test case or test suite from a project. Threads indicates the amount of test cases to execute in parallel, default is 1. Driver indicates wich driver to use to run the tests, options are: firefox, chrome, default is firefox. Chrome driver requires chrome_driver_path setting to be defined in settings file.

- **gui [-p|--port]**

Start Golem GUI. Port indicates which port number to use, default is 5000.

- **createproject project**

Creates a new project with the given name. Creates the base files and folders.