from golem.core import utils, core

import sys, os


def execute_from_command_line():

    #set global variable values
    action = sys.argv[0]
    name = sys.argv[1]
    
     if action == 'create':
        if test == 'demo':
            print 'create demo'
            utils.create('demo')
            sys.exit()
        elif test != '':
            print 'create', test
            utils.create(test)
            sys.exit()
        else:   
            print 'Select new project name'
            sys.exit()

            

if __name__ == "__main__":

    execute_from_command_line()
