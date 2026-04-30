from pages.base_page import BasePage
from utilities.read_properties import ReadConfig
from playwright.sync_api import expect


class LoginPage(BasePage):

    def login(self, username, password):
        self.fill(ReadConfig.get_locator("Username_Input"), username)
        self.fill(ReadConfig.get_locator("Password_Input"), password)
        self.click(ReadConfig.get_locator("Login_Button"))
        self.page.wait_for_load_state('networkidle')

    def forgot_password(self, email):
        self.click(ReadConfig.get_locator("Forgot_Password_Link"))
        self.fill(ReadConfig.get_locator("Email_Input"), email)
        self.click(ReadConfig.get_locator("Send_Reset_Button"))

    def is_invalid_login_error_visible(self):
        locator = self.get_locator(ReadConfig.get_locator("Invalid_Login_Error"))
        expect(locator).to_be_visible(timeout=10000)
        return True

    def is_empty_username_error_visible(self):
        locator = self.get_locator(ReadConfig.get_locator("Empty_Username"))
        expect(locator).to_be_visible(timeout=10000)
        return True

    def is_empty_password_error_visible(self):
        locator = self.get_locator(ReadConfig.get_locator("Empty_Password"))
        expect(locator).to_be_visible(timeout=10000)
        return True