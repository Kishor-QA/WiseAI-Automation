from pages.base_page import BasePage
from utilities.custom_logger import Log_Maker, mask_secret
from utilities.read_properties import ReadConfig
from playwright.sync_api import expect

logger = Log_Maker.log_gen(__name__)


class LoginPage(BasePage):

    def login(self, username, password):
        logger.info(f"Logging in as '{username}' (password {mask_secret(password)})")

        self.fill(ReadConfig.get_locator("Username_Input"), username)
        self.fill(ReadConfig.get_locator("Password_Input"), password, mask=True)
        self.click(ReadConfig.get_locator("Login_Button"))
        self.page.wait_for_load_state('networkidle')

        logger.info(f"Login form submitted for '{username}'; landed on {self.page.url}")

    def forgot_password(self, email):
        logger.info(f"Starting password reset for '{email}'")
        self.click(ReadConfig.get_locator("Forgot_Password_Link"))
        self.fill(ReadConfig.get_locator("Email_Input"), email)
        self.click(ReadConfig.get_locator("Send_Reset_Button"))
        logger.info(f"Password reset requested for '{email}'")

    def is_invalid_login_error_visible(self):
        logger.debug("Checking for the invalid-credentials error")
        locator = self.get_locator(ReadConfig.get_locator("Invalid_Login_Error"))
        expect(locator).to_be_visible(timeout=10000)
        logger.info("Invalid login error is displayed as expected")
        return True

    def is_empty_username_error_visible(self):
        logger.debug("Checking for the empty-username error")
        locator = self.get_locator(ReadConfig.get_locator("Empty_Username"))
        expect(locator).to_be_visible(timeout=10000)
        logger.info("Empty username error is displayed as expected")
        return True

    def is_empty_password_error_visible(self):
        logger.debug("Checking for the empty-password error")
        locator = self.get_locator(ReadConfig.get_locator("Empty_Password"))
        expect(locator).to_be_visible(timeout=10000)
        logger.info("Empty password error is displayed as expected")
        return True
