Suites
==================================================


A suite lets you arbitrarily select a sub-set of tests to execute as a group. Let's say, you want to test only the most important tests, or the tests for a specific module. In that ocasion, you use a suite.

A suite contains a list of *tests*, a list of *browsers* and the amount of *workers*. Consider the following example:


**full_regression.py**
```python

browsers = ['firefox', 'chrome']

workers = 2

tests = [
    'test1',
    'test2',
    'some_folder.test3',
]

```

![suite example](_static/img/suite-example.png "Suite Example")

<div class="admonition note">
    <p class="first admonition-title">Note</p>
    <p>This suite will execute all marked tests, once per each browser and test set</p>
</div>


##### Test Parallelization

The 'workers = 2' tells Golem how many tests should be executed at the same time. Default is one (one at a time). How many tests can be parallelized depends on your test infrastructure


Next, go to [Actions](actions.html)
