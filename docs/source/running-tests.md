Running tests
==================================================

## Run a single test

A single test can be run using the file path or the test module path.
In both cases it should be relative to the *tests* folder.
```
golem run project test_name
golem run project test_name.py
golem run project folder.test_name
golem run project folder/test_name.py
```

## Run a suite

Similar to a test, a suite can be run using the file path or the test module path.
In both cases it should be relative to the *suites* folder.

```
golem run project suite_name
golem run project suite_name.py
golem run project folder.suite_name
golem run project folder/suite_name.py
```

## Run every test in a directory

To select all the tests in a directory and subdirectories a relative path can be supplied.
The path has to be relative to the *tests* folder.

```
golem run project folder/
```

### Run every test in a project

```
golem run project .
```

## Select Browsers

```
golem run project suite -b chrome firefox
```

Every selected test will be run for each of the selected browsers.
Browsers can also be defined inside a suite.
If no browser is set, the default defined in settings will be used.
The valid options for browsers are listed [here](browsers.html#valid-options).

## Run Tests in Parallel

To run tests in parallel the number of processes must be set to more than 1.
This can be done through the *golem run* command or by the *processes* attribute of a suite. 

```
golem run project suite_name -p 3
```

## Select Environments

Select which [environments](test-data.html#environments) to use for a test execution:

```
golem run project suite -e internal staging
```

## Filter Tests by Tags

The selected tests for an execution can be filtered by tags.

```
golem run project suite -t smoke "release 42.11.01"
```

Multiple tags are always used with *and* operator.
To use a combination of *and*, *or*, and *not*, a tag expression must be used:

```
golem run project suite -t "smoke and (regression or not 'release 001')"
``` 
