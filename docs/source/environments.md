Managing Environments
==================================================


### Defining Envionments

If the tests should run in different environments, these can be defined in the *environments.json* file. For example, consider the following:

**environments.json**
```
{
    "test": {
        "url": "http://1.1.1.1:5000/"
    },
    "stage": {
        "url": "http://2.2.2.2:5000/"
    }
    "production": {
        "url": "http://production.com/"
    }
}
```

### Using Environment Data Inside Tests

Instead of defining the url in every test, just point to the envinment url like so:

**some_test.py**
```
def test(data):
    navigate(data.env.url)
    ...
```

### Using Environments in Suites

**some_suite.py**
```

browsers = ['chrome']

environments = ['test', 'stage', 'production']

tests = ['some_test', '...']

```

### Selecting an Environment in the Command Line

To select which environment to use when running a test from the command line use the -e --environments flag:

```
golem run project test --environments test stage
```

