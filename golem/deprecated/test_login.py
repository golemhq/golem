from selenium import webdriver

class Login_page(object):
	
	def email(self, driver):
		mail = driver.find_element_by_id("email")
		return mail




driver = webdriver.Firefox()
driver.implicitly_wait(10) # seconds
driver.get("http://argenrapp21/Emerios/ES3/RetrieveDocument/login.html")
assert "ES3 Login" in driver.title


#mail = driver.find_element_by_id("email")


login_page = Login_page()

login_page.email(driver).send_keys("manager.test@vmbc.com")

#mail.send_keys("manager.test@vmbc.com")

password = driver.find_element_by_id("password")

password.send_keys("vmbc2013")

login = driver.find_element_by_id("login")

login.click()

new_btn = driver.find_element_by_id("newWI")

new_btn.click()

create_bug_menu = driver.find_element_by_id("create-bug")

create_bug_menu.click()

cancel_btn = driver.find_element_by_xpath("//span[contains(text(), 'Cancel')]")

cancel_btn.click()