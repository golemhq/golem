Suites
==================================================

A suite can execute a set of tests with the specified configuration.
For example, running the most important tests or the tests for a specific module.
It can define which browsers to use and how many tests should run in parallel.

A suite contains a list of *tests*, a list of *browsers*, a list of *environments* and the number of *processes*. Consider the following example:

**full_regression.py**
```python

browsers = ['firefox', 'chrome']

environments = []

processes = 2

tests = [
    'test1',
    'test2',
    'some_folder.test3',
]

```

<img class="border-image" src="_static/img/suite-example.png">

<div class="admonition note">
    <p class="first admonition-title">Note</p>
    <p>This suite will execute all marked tests, once per each browser, environment and test set</p>
</div>


### Test Parallelization

The 'processes = 2' tells Golem how many tests should be executed at the same time. The default is one (one at a time). How many tests can be parallelized depends on your test infrastructure.


### Environments

Environments are defined in the environments.json file inside a project
