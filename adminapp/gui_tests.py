import unittest

from selenium import webdriver
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import NoSuchElementException


class GUI(unittest.TestCase):
    def setUp(self):
        # drivers path here
        self.driver = webdriver.Chrome("/chromedriver")
        self.driver.implicitly_wait(30)
        self.base_url = "https://www.katalon.com/"
        self.verificationErrors = []
        self.accept_next_alert = True

    def test_admin_login(self):
        driver = self.driver
        driver.get("http://127.0.0.1:8000/")
        driver.find_element_by_id("home-login").click()
        driver.find_element_by_id("email").click()
        driver.find_element_by_id("email").clear()
        #superuser username
        driver.find_element_by_id("email").send_keys("melis")
        driver.find_element_by_id("password").click()
        driver.find_element_by_id("password").clear()
        #superuser password
        driver.find_element_by_id("password").send_keys("123456")
        driver.find_element_by_id("login").click()

        assert 'Home' in self.driver.title

    def test_user_login(self):
        driver = self.driver
        driver.get("http://127.0.0.1:8000/")
        driver.find_element_by_id("home-login").click()
        driver.find_element_by_id("email").click()
        driver.find_element_by_id("email").clear()
        # test user username
        driver.find_element_by_id("email").send_keys("test")
        driver.find_element_by_id("password").click()
        driver.find_element_by_id("password").clear()
        # test user password
        driver.find_element_by_id("password").send_keys("123Ab123")
        driver.find_element_by_id("login").click()

        assert 'Home' in self.driver.title

    def test_admin_see_datasets_list(self):
        driver = self.driver
        self.test_admin_login()

        driver.find_element_by_id("list_dataset").click()
        assert 'Datasets List' in self.driver.title

    def test_admin_see_setups_list(self):
        driver = self.driver
        self.test_admin_login()

        driver.find_element_by_id("list_setup").click()
        assert 'Setups List' in self.driver.title

    def test_admin_see_experiments_list(self):
        driver = self.driver
        self.test_admin_login()

        driver.find_element_by_id("list_experiment").click()
        assert 'Experiments List' in self.driver.title

    def test_admin_see_setup_profile(self):
        driver = self.driver
        self.test_admin_see_setups_list()

        driver.find_element_by_id("setup_profile").click()
        assert 'Setup Profile' in self.driver.title

    def test_admin_see_session_profile(self):
        driver = self.driver
        self.test_admin_see_experiments_list()
        driver.find_element_by_id("session_profile").click()

        assert 'Session Profile' in self.driver.title

    def test_admin_see_dataset_profile(self):
        driver = self.driver
        self.test_admin_see_datasets_list()

        driver.find_element_by_id("dataset_profile").click()
        assert 'Dataset Profile' in self.driver.title

    def test_user_see_invitations_list(self):
        driver = self.driver
        self.test_user_login()

        driver.find_element_by_id("list_invitations").click()

        assert 'Invitations' in self.driver.title

    def is_element_present(self, how, what):
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e:
            return False
        return True

    def is_alert_present(self):
        try:
            self.driver.switch_to_alert()
        except NoAlertPresentException as e:
            return False
        return True

    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally:
            self.accept_next_alert = True

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)


if __name__ == "__main__":
    unittest.main()