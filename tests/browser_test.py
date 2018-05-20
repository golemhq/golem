import os


class Test_get_browser:

    def test_driver_path_is_not_defined(self, project_function_clean, test_utils):
        # Setup
        testdir = project_function_clean['testdir']
        project = project_function_clean['name']
        settings_path = os.path.join(testdir, 'settings.json')
        content = '{}'
        with open(settings_path, 'w') as f:
            f.write(content)
        test_content = ('def test(data):\n'
                        '    open_browser()')
        test_path = os.path.join(testdir, 'projects', project, 'tests', 'test_one.py')
        with open(test_path, 'w') as f:
            f.write(test_content)
        # Test
        drivers = [
            ('chromedriver_path', 'chrome'),
            ('chromedriver_path', 'chrome-headless'),
            ('edgedriver_path', 'edge'),
            ('geckodriver_path', 'firefox'),
            ('iedriver_path', 'ie'),
            ('operadriver_path', 'opera'),
        ]
        for setting_path, browser_name in drivers:
            result = test_utils.run_command('golem run {} test_one -b {}'.format(project, browser_name))
            assert 'Exception: {} setting is not defined'.format(setting_path) in result

    def test_executable_not_present(self, project_function_clean, test_utils):
        # Setup
        testdir = project_function_clean['testdir']
        project = project_function_clean['name']
        test_content = ('def test(data):\n'
                        '    open_browser()')
        test_path = os.path.join(testdir, 'projects', project, 'tests', 'test_one.py')
        with open(test_path, 'w') as f:
            f.write(test_content)
        # Test
        drivers = [
            ('./drivers/chromedriver*', 'chrome'),
            ('./drivers/chromedriver*', 'chrome-headless'),
            ('./drivers/edgedriver*', 'edge'),
            ('./drivers/geckodriver*', 'firefox'),
            ('./drivers/iedriver*', 'ie'),
            ('./drivers/operadriver*', 'opera'),
        ]
        for setting_path, browser_name in drivers:
            result = test_utils.run_command('golem run {} test_one -b {}'.format(project, browser_name))
            msg = 'No executable file found using path {}'.format(setting_path)
            assert msg in result
