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

This suite will execute the 3 tests, once per each browser defined. So it will execute a total of 6 tests. 

**Parallelisation**

The 'workers = 2' tells Golem how many tests should be executed at the same time. If instead we write 'workers = 6', then all the tests would be executed at the same time.



Next, go to [Actions](actions.html)