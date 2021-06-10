Running Tests with Jenkins
==================================================

In this guide let's see how Golem tests can be run in jenkins.

## Pre-requisites

- Jenkins is installed.
- Python 3.5+ is installed in the Jenkins machine.
- A Golem directory with tests is stored in a git repository.

## Steps

In Jenkins go to Dashboard > Manage Jenkins > Global Tool Configuration

In Python > Python installations section add a Python version with the path to the executable:

![](https://raw.githubusercontent.com/golemhq/resources/master/img/jenkins-guide/jenkins-python-installation.jpg)

We will be using ShiningPanda to manage the virtual environments in the Jenkins job:
[https://plugins.jenkins.io/shiningpanda/](https://plugins.jenkins.io/shiningpanda/).

In Jenkins go to Dashboard > Manage Jenkins > Manage Plugins.
Install the ShiningPanda plugin and restart Jenkins.

Create a new Jenkins job of type "Freestyle project"

Define the location of the tests in the Source Code Management section:

![](https://raw.githubusercontent.com/golemhq/resources/master/img/jenkins-guide/jenkins-define-source-repo.jpg)

Add a build step of type "Virtualenv Builder":

![](https://raw.githubusercontent.com/golemhq/resources/master/img/jenkins-guide/jenkins-build-step.jpg)

Add a post-build action that collects the generated JUnit XML report:

![](https://raw.githubusercontent.com/golemhq/resources/master/img/jenkins-guide/jenkins-post-build-action.jpg)

Run!

![](https://raw.githubusercontent.com/golemhq/resources/master/img/jenkins-guide/jenkins-final-result.jpg)


