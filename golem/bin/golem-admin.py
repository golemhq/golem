from golem.core import utils, core

import sys, os


def execute_from_command_line():

    #set global variable values
   
    
    destination = os.getcwd()

    import golem as a
    source = os.path.dirname(a.__file__) + '\\demo\\.'

    action = sys.argv[1]
    name = sys.argv[2]
    
    if action == 'create':
        if name != '':
            if name == 'demo':
                print 'Creating project: demo'
                utils.create('demo', source, destination)
                sys.exit()
            else:
                print 'Creating project:', name
                utils.create(name, source, destination)
                sys.exit()
        else:   
            print 'Select new project name'
            sys.exit()

            

if __name__ == "__main__":

    execute_from_command_line()
