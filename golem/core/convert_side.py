import argparse
import json,os,re
from golem.actions import get_window_index

def format_indentation(command, indentation_num):
    return " " * (indentation_num) + command

#Manage the indentation_level
def manage_indentation(structured_command,current_indentation):
    global indentation_level,next_indentation
    if structured_command in ['if','for','do','while','elseIf','else','times','forEach']:
       if indentation_level == 0:
        next_indentation = current_indentation + 4
        indentation_level = +1
       elif structured_command in ['elseIf','else'] :
           current_indentation = next_indentation -4
           next_indentation = current_indentation +4
       else:
           current_indentation = next_indentation
           next_indentation = current_indentation +4
           indentation_level = +1         
    elif structured_command not in 'end' :
     if indentation_level != 0:
      current_indentation = next_indentation
     else:
      current_indentation = 4
    else:
      current_indentation = next_indentation -4 
      next_indentation = current_indentation 
      indentation_level = -1
    return current_indentation
    
# convert the selenium cmd to golem cmd
def golem_converter(cmd,targets,values,url):  
    selenium_to_golem={
  'addSelection': 'select_option_by_value({target}, "{value}")' if 'label='  not in values else  'select_option_by_text({target}, "{value}")'.format(target=targets,value = values.split('=')[1]),
  'answerOnNextPrompt': 'submit_prompt_alert("{target}")',
  'assert': 'assert data.{target} == "{value}"',
  'assertAlert': 'assert_alert_text("{target}")',
  'assertChecked':  'assert_element_checked({target})',
  'assertConfirmation': 'assert_alert_text("{target}")',
  'assertEditable': 'assert_element_enabled({target})',
  'assertElementPresent': 'assert_element_present({target})',
  'assertElementNotPresent': 'assert_element_not_present({target})',
  'assertNotChecked': 'assert_element_not_checked({target})',
  'assertNotEditable': 'assert_element_not_enabled({target})',
  'assertNotSelectedValue': 'assert_element_attribute({target}, "value", "{value}")',
  'assertNotText': 'assert_element_text_is_not({target}, "{value}")',
  'assertPrompt': 'assert_alert_text("{target}")',
  'assertSelectedLabel': 'assert_element_attribute({target}, "value", "{value}")',
  'assertSelectedValue': 'assert_element_attribute({target}, "value", "{value}")',
  'assertNotSelectedValue' : 'assert_element_attribute_is_not({target}, "value", "{value}")',
  'assertValue': 'assert_element_attribute({target}, "value", "{value}")',
  'assertText': 'assert_element_text({target}, "{value}")',
  'assertTitle': 'assert_title("{target}")',
  'check': 'check_element({target})',
  'chooseCancelOnNextConfirmation': 'skip',
  'chooseCancelOnNextPrompt': 'skip',
  'chooseOkOnNextConfirmation': 'skip',
  'click': 'click({target})',
  'clickAt': 'click({target})',
  'close': 'close_window()',
  'debugger': 'skip',
  'do': 'do',
  'doubleClick': 'double_click({target})',
  'doubleClickAt': 'double_click({target})',
  'dragAndDropToObject': 'drag_and_drop({value}, {target})',
  'echo': 'log("{target}")',
  #'editContent': 'emitEditContent',
  'else': 'else :',
  'elseIf': 'elif {target} :',
  'end': '#end',
  'executeScript': "execute_javascript('{target}')" if len(values) == 0 else  "data.{value} = execute_javascript('{target}')",
  'executeAsyncScript': "execute_javascript('{target}')" if len(values) == 0 else  "data.{value} = execute_javascript('{target}')",
  'forEach': 'for {value} in {target} :',
  'if': 'if {target} :',
  'mouseDown': 'skip',
  'mouseDownAt': 'skip',
  'mouseMove': 'skip',
  'mouseMoveAt': 'skip',
  'mouseOver': 'skip',
  'mouseOut': 'skip',
  'mouseUp': 'skip',
  'mouseUpAt': 'skip',
  'open': 'get("{url}{target}")'.format(target=targets,url = '') if 'http' in targets or 'https' in targets else 'get("{url}{target}")'.format(target=targets,url = url),
  'opensWindow': 'store("{windowHandleName}", {value})',
  'removeSelection': 'select_option_by_value({target}, "{value}")' if 'label='  not in values else  'select_option_by_text({target}, "{value}")'.format(target=targets,value = str(values.split('=')[1])),
  'pause': 'wait({value})' if len(values) !=0 else 'wait({target})',
  #'repeatIf': 'emitControlFlowRepeatIf',
  'run': '{target}.test(data)',
  'runScript': "execute_javascript('{target}')",
  'select': 'select_option_by_value({target}, "{value}")' if 'label='  not in values else  'select_option_by_text({target}, "{value}")'.format(target=targets,value = str(values.split('=')[1])),
  'selectWindow': 'switch_to_window_by_index({target})',
  'sendKeys': 'send_keys({target}, "{value}")' if 'KEY' not in values else  'press_key({target}, "{value}")'.format(target=targets,value=values.replace('${KEY_','').replace("}",'')),
  'setSpeed': 'skip',
  'setWindowSize': 'set_window_size({target})'.format(target=','.join(str(targets).split('x'))),
  'selectFrame': 'switch_to_frame({target})' if 'parent'not in targets else 'switch_to_parent_frame()',
  'store': 'store("{value}", "{target}")',
  'storeAttribute': 'store("{value}", get_element_attribute({target}))',
  'storeJson': 'skip',
  'storeText': 'store("{value}", get_element_text({target}))',
  'storeTitle': 'store("{value}", "{target}")',
  'storeValue': 'store("{value}", get_element_value({target}))',
  'storeWindowHandle': 'store("{target}", get_window_index())',
  'storeXpathCount': 'store("{value}", len(get_browser().find_all({target})))',
  'submit': 'submit_form({target})',
  'times': 'for i in range(0, {target}):',
  'type': 'send_keys({target}, "{value}")',
  'uncheck': 'uncheck_element({target})',
  'verify': 'assert {target} == "{value}"',
  'verifyChecked': 'verify_element_checked({target})',
  'verifyEditable': 'verify_element_enabled({target})',
  'verifyElementPresent': 'verify_element_present({target})',
  'verifyElementNotPresent': 'verify_element_not_present({target})',
  'verifyNotChecked': 'verify_element_not_checked({target})',
  'verifyNotEditable': 'verify_element_not_enabled({target})',
  'verifyNotSelectedValue': 'verify_element_attribute_is_not({target}, "value", "{value}")',
  'verifyNotText': 'verify_element_text_is_not({target}, "{value}")',
  'verifySelectedLabel': 'verify_selected_option_by_text({target}, "{value}")',
  'verifySelectedValue': 'verify_selected_option_by_value({target}, "{value}")',
  'verifyText': 'verify_element_text({target}, "{value}")',
  'verifyTitle': 'verify_title("{target}")',
  'verifyValue': 'verify_element_value({target}, "{value}")',
  'waitForElementEditable': 'wait_for_element_enabled({target}, {value})',
  'waitForElementPresent': 'wait_for_element_present({target}, {value})',
  'waitForElementVisible': 'wait_for_element_displayed({target}, {value})',
  'waitForElementNotEditable': 'wait_for_element_not_enabled({target}, {value})',
  'waitForElementNotPresent': 'wait_for_element_not_present({target}, {value})',
  'waitForElementNotVisible': 'wait_for_element_not_displayed({target}, {value})',
  'waitForText': 'wait_for_element_text({target}, "{value}")',
  'webdriverAnswerOnVisiblePrompt': 'submit_prompt_alert("{target}")',
  'webdriverChooseCancelOnVisibleConfirmation': 'dismiss_alert(ignore_not_present=False)',
  'webdriverChooseCancelOnVisiblePrompt': 'dismiss_alert(ignore_not_present=False)',
  'webdriverChooseOkOnVisibleConfirmation': 'accept_alert(ignore_not_present=False)',
  'while': 'while {target}:',
  '': 'skip'
    }
    
    if cmd in selenium_to_golem.keys():
     return selenium_to_golem[cmd]
    else:
     return 'skip'
     
def convert_commands(testsdata,url,testname,project_name):
    golem_scripts = []
    errors=[]
    test_import=[]
    target_match = ['id=','name=','xpath=','linkText=','link=','partialLinkText=','css=']
    window_match = ['handle=','index=']
    test_step_match= ['{target}','{value}','{url}']
    current_indentation = 4
    global indentation_level
    indentation_level = 0
    url = url
    for testdata in testsdata:
      comments = False
      try:  
            # if command start with "//" means it's commented cmd.
            if testdata['command'].startswith('//'):
              cmd = testdata['command'].replace('//','')
              comments = True
            else:
             cmd = testdata['command'] 
            target = str(testdata['target'])
            comment = testdata['comment']
            values = testdata['value']
            # split the command if start with target match value            
            if len([ele for ele in target_match if(ele in target)]) !=0:
             target=tuple(target.split('='))
             if 'linkText' in target or 'partialLinkText' in target:
                 target = str(target).replace('linkText','link_text')
            elif len([ele for ele in window_match if(ele in target)]) !=0:
              target=str(target.split('=')[1])
            # if other test imported in test 
            elif 'run' == cmd:
                test_import.append('from projects.' +  project_name + '.tests' + ' import ' + target)             
            structured_command = golem_converter(cmd,target,values,url)
            # some of the selenium command which not supported currently have make it skip.            
            if structured_command != 'skip':
             if 'opensWindow' in testdata.keys():
                 command_with_argument1 = structured_command.format(target= target,value=values)
                 command_with_argument2 = golem_converter('opensWindow',target,values,url).format(windowHandleName = testdata['windowHandleName'],value = 'get_window_index() + 1')
                 command_with_argument = command_with_argument1 + '\n'+ " "*(current_indentation) + command_with_argument2 
             elif len([ele for ele in test_step_match if(ele in structured_command)]) ==0:
               command_with_argument= structured_command
             else:             
              command_with_argument= structured_command.format(target=target,value=values,url=url)  
             # convert ${variable} to data.variable              
             if re.search('\${(\w*)\}',command_with_argument):
              match = re.findall('\${(\w*)\}',command_with_argument)
              match2 = re.findall('\${[\w]*\}',command_with_argument)
              # convert variable into argument value
              if 'execute_javascript(' in command_with_argument:
               argument_value = []
               for m in range(0, len(match)):
                if 'data.' + match[m] not in argument_value:
                 argument_value.append('data.' + match[m])
                command_with_argument = command_with_argument.replace(match2[m], 'arguments[' + str(m) + ']')
               command_with_argument = command_with_argument[:-1] + ','+ ','.join(argument_value) + command_with_argument[-1:]
              else:
               match2 = re.findall('\"+\${[\w]*\}\"+',command_with_argument) or re.findall('\${[\w]*\}',command_with_argument)
               for m in range(0, len(match)):
                command_with_argument = command_with_argument.replace(match2[m], 'data.' + match[m])
             current_indentation = manage_indentation(cmd,current_indentation)
             if len(comment) != 0:
              golem_scripts.append(format_indentation(f'#{comment}', current_indentation))
             if comments == True:
              golem_scripts.append(format_indentation(f'#{command_with_argument}', current_indentation))
              comments = False
             else:
              golem_scripts.append(format_indentation(f'{command_with_argument}', current_indentation))
            else:
             pass
      except Exception as e:
          error = 'Test ' + "'" + testname + "'" +' has a problem: '  + 'Incomplete command ' + "'" + str(e) +"'" + ' Missing expected ' + structured_command + ' argument'
          print(error)
          errors.append(error)
    return golem_scripts,errors,test_import
            
def create_test_script(testdata,url,testname,project_name):
           errors= []
        # Convert commands for test.
           if len(testdata) > 1:
            converted_commands,errors,test_import = convert_commands(testdata,url,testname,project_name)
            test_content =('from golem.actions import *'
        '\n'
        '{}\n'
        '\ndef test(data):\n'
        '{}\n'.format('\n'.join(test_import),'\n'.join(converted_commands))
    )
           else:
            test_content = (
        '\n'
        'def test(data):\n'
        '\tpass\n'
    )
           return test_content,errors

# Create Suite based on test          
def create_suite_script(test_list):
 if len(test_list) != 0:
           suite_content = ('\n'
                     'browsers = []\n'
                     '\nenvironments = []\n'
                     '\nprocesses = 1\n'
                     '\ntests = {}\n'.format(test_list))
           return suite_content
 else:
    no_suite_content = ('\n'
                     'browsers = []\n'
                     '\nenvironments = []\n'
                     '\nprocesses = 1\n'
                     '\ntests = []\n')
    return no_suite_content