

class Testclass:

    def __init__(self, driver_instance, data):
        driver = driver_instance
        self.run(driver, data)

    def run(self, driver, data):
        #setup
        from ..pages import login, dashboard
        login = login.Login(driver)
        dashboard = dashboard.Dashboard(driver)
        driver.get("http://argenrapp21/Emerios/ES3/RetrieveDocument/login.html")

        #steps
        login.do_login('lala', 'lala')
        dashboard.new_dropdown.click()
        dashboard.create_story_menu_option.click()
        dashboard.current_project_radio.click()
        dashboard.story_name.send_keys('test automation')
        dashboard.story_description.send_keys('test automation')
        dashboard.story_assignee.send_keys('Luciano Feo')
        dashboard.story_saveclose_button.click()
        #/steps
