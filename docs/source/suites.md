Suites
==================================================

A suite can execute a set of tests with the specified configuration.
A suite contains a list of *tests*,  *browsers*, and *environments* and the number of *processes*, and *tags*.
Consider the following example:

**full_regression.py**
```python

browsers = ['firefox', 'chrome']

environments = []

processes = 2

tags = []

tests = [
    'test1',
    'test2',
    'some_folder.test3',
]

```

<img class="border-image" src="https://raw.githubusercontent.com/golemhq/resources/master/img/suite_example.jpg">

<div class="admonition note">
    <p class="first admonition-title">Note</p>
    <p>This suite will execute all marked tests, once per each browser, environment and test set</p>
</div>


### Test Parallelization

The 'processes = 2' tells Golem how many tests should be executed at the same time. The default is one (one at a time). How many tests can be parallelized depends on your test infrastructure.


### Environments

Environments are defined in the environments.json file inside a project. See [Environments](test-data.html#environments).
