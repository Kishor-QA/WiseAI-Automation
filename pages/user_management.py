from utilities.custom_logger import Log_Maker, mask_secret
from utilities.read_properties import UserManagamentConfig
from pages.base_page import BasePage
from playwright.sync_api import expect
from pages.login_page import LoginPage


logger = Log_Maker.log_gen(__name__)


class UserManagement(BasePage):

    Page_URL = UserManagamentConfig.get_page_url()
    Navigate_User_Management= UserManagamentConfig.get_locator("Navigate_User_Management")
    Create_New_User= UserManagamentConfig.get_locator("Create_New_User")
    First_Name=UserManagamentConfig.get_locator("First_Name")
    Middle_Name=UserManagamentConfig.get_locator("Middle_Name")
    Last_Name=UserManagamentConfig.get_locator("Last_Name")
    Email=UserManagamentConfig.get_locator("Email")
    Domain_Dropdown=UserManagamentConfig.get_locator("Domain_Dropdown")
    Select_Domain=UserManagamentConfig.get_locator("Select_Domain")
    Role_Button=UserManagamentConfig.get_locator("Role_Button")
    Select_Roles =UserManagamentConfig.get_locator("Select_Roles")
    Create_User=UserManagamentConfig.get_locator("Create_User")
    Yopmail_URL =UserManagamentConfig.get_page_url("Yopmail_URL")
    Email_Box =UserManagamentConfig.get_locator("Email_Box")
    Successful_Message= UserManagamentConfig.get_locator("Successful_Message")
    Already_Exists_Message = UserManagamentConfig.get_locator("Already_Exist_Message")
    Inbox_Frame = UserManagamentConfig.get_locator("Inbox_Frame")
    Mail_Frame = UserManagamentConfig.get_locator("Mail_Frame")
    Email_Item = UserManagamentConfig.get_locator("Email_Item")
    Redirect_Link= UserManagamentConfig.get_locator("Redirect_Link")
    Update_Password_Redirect=UserManagamentConfig.get_locator("Update_Password_Redirect")
    New_Password=UserManagamentConfig.get_locator("New_Password")
    Confirm_Password=UserManagamentConfig.get_locator("Confirm_Password")
    Reset_Password=UserManagamentConfig.get_locator("Reset_Password")
    Success_Toast=UserManagamentConfig.get_locator("Success_Toast")
    Status=UserManagamentConfig.get_locator("Status")
    User_Dashboard=UserManagamentConfig.get_locator("User_Dashboard")

    def navigate_to_user_management(self):
        logger.info("Navigating to the User Management page")
        self.click(self.Navigate_User_Management)
        logger.info(f"User Management page opened at {self.page.url}")

    def create_new_user(self, first_name,middle_name, last_name, email):
        logger.info(f"Creating user '{first_name} {middle_name} {last_name}' with email '{email}'")
        self.click(self.Create_New_User)
        self.fill(self.First_Name, first_name)
        self.fill(self.Last_Name, last_name)
        self.fill(self.Middle_Name, middle_name)
        self.fill(self.Email, email)
        self.click(self.Domain_Dropdown)
        self.click(self.Select_Domain)
        # Domain is fixed (@aloi.com) and a default USER role is pre-assigned
        # on the current UI, so no dropdown interaction is needed
        self.click(self.Create_User)
        logger.info(f"Create user form submitted for '{email}'")

    def successful_message(self):
        self.verify_text_visible(self.Successful_Message)
        logger.info("User creation succeeded - confirmation message displayed")
        return True

    def already_exist_message(self):
        self.verify_text_visible(self.Already_Exists_Message)
        logger.info("User already exists - duplicate message displayed")
        return True

    def open_new_tab(self, new_url):
        logger.info(f"Opening a new browser tab at {new_url}")
        new_page = self.page.context.new_page()
        new_page.goto(new_url)
        new_page.wait_for_load_state()
        logger.debug(f"New tab loaded at {new_page.url}")
        return new_page

    def verify_email(self, email):
        logger.info(f"Opening the Yopmail inbox for '{email}'")
        locator = self.get_locator(self.Email_Box)
        locator.fill(email)
        locator.press("Enter")
        self.page.wait_for_selector(self.Inbox_Frame[1], timeout=20000)
        logger.debug(f"Inbox frame loaded for '{email}'")

    def wait_for_verification_email(self, retries=6):
        """
        Yopmail delivery can lag behind user creation, so reload the inbox
        until the verification email appears.
        """
        logger.info(f"Waiting for the verification email (up to {retries} inbox checks)")
        for attempt in range(1, retries + 1):
            inbox_frame = self.get_frame(self.Inbox_Frame)
            email_item = inbox_frame.get_by_role(self.Email_Item[1], name=self.Email_Item[2]).first
            try:
                expect(email_item).to_be_visible(timeout=10000)
                logger.info(f"Verification email arrived on inbox check {attempt}")
                return
            except AssertionError:
                logger.warning(f"Inbox check {attempt}/{retries}: no verification email yet, reloading")
                self.page.reload()
                self.page.wait_for_selector(self.Inbox_Frame[1], timeout=20000)

        logger.error(f"Verification email never arrived after {retries} inbox checks")
        raise AssertionError(f"Verification email not received after {retries} inbox checks")


    def password_change(self, new_password, confirm_password ):
        logger.info(f"Setting the new account password ({mask_secret(new_password)})")
       # self.verify_text_visible(self.Update_Password_Redirect)
        #self.click(self.Update_Password_Redirect)
        self.fill(self.New_Password, new_password, mask=True)
        self.fill(self.Confirm_Password, confirm_password, mask=True)
        self.click(self.Reset_Password)
        logger.info("New password submitted")
        self.verify_text_visible(self.Success_Toast)
        logger.info("Password change Successful")
        
    def click_redirect_link(self):
        logger.info("Opening the verification email and following its redirect link")
        inbox_frame = self.get_frame(self.Inbox_Frame)
        inbox_frame.get_by_role(self.Email_Item[1], name=self.Email_Item[2]).click()

        mail_frame = self.get_frame(self.Mail_Frame)
        with self.page.expect_popup() as popup_info:
            mail_frame.get_by_role(self.Redirect_Link[1], name=self.Redirect_Link[2]).click()
        new_page = popup_info.value
        new_page.wait_for_load_state()

        reset_url = new_page.url
        logger.info(f"Redirect link resolved to {reset_url}")
        new_page.close()

        # Open the reset link in a brand-new, unauthenticated context so the
        # app can't find an existing session and bounce to the dashboard.
        fresh_context = self.page.context.browser.new_context()#create a brand new,separate profile to solve the problem of redirecting to dashboard
        self.page = fresh_context.new_page() #with no cookies, no session, nothing carried over from the previous page
        self.page.goto(reset_url)
        self.page.wait_for_load_state()
        logger.info(f"Reset link reopened in a fresh context at {self.page.url}")

        #context (BrowserContext) is an isolated environment inside a running browser that has its own:cookies ,localStorage / sessionStorage,cache,login/session state
        
    def new_user_login(self, email, password):
        logger.info(f"Logging in as newly created user '{email}'")
        login = LoginPage(self.page)
        login.login(email, password)

        
        expect(self.get_locator(self.User_Dashboard)).to_be_visible(timeout=10000)
        logger.info(f"Dashboard confirmed loaded for '{email}'")

   
