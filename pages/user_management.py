from utilities.read_properties import UserManagamentConfig
from pages.base_page import BasePage
from playwright.sync_api import expect

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

    def navigate_to_user_management(self):
        self.click(self.Navigate_User_Management)

    def create_new_user(self, first_name,middle_name, last_name, email):
        self.click(self.Create_New_User)
        self.fill(self.First_Name, first_name)
        self.fill(self.Last_Name, last_name)
        self.fill(self.Middle_Name, middle_name)
        self.fill(self.Email, email)
        # Domain is fixed (@aloi.com) and a default USER role is pre-assigned
        # on the current UI, so no dropdown interaction is needed
        self.click(self.Create_User)
    
    def successful_message(self):
        self.verify_text_visible(self.Successful_Message)
        return True
    
    def already_exist_message(self):
        self.verify_text_visible(self.Already_Exists_Message)
        return True
    
    def open_new_tab(self, new_url):
        new_page = self.page.context.new_page()
        new_page.goto(new_url)
        new_page.wait_for_load_state()
        return new_page
    
    def verify_email(self, email):
        locator = self.get_locator(self.Email_Box)
        locator.fill(email)
        locator.press("Enter")
        self.page.wait_for_selector(self.Inbox_Frame[1], timeout=20000)

    def wait_for_verification_email(self, retries=6):
        """
        Yopmail delivery can lag behind user creation, so reload the inbox
        until the verification email appears.
        """
        for attempt in range(retries):
            inbox_frame = self.get_frame(self.Inbox_Frame)
            email_item = inbox_frame.get_by_role(self.Email_Item[1], name=self.Email_Item[2]).first
            try:
                expect(email_item).to_be_visible(timeout=10000)
                return
            except AssertionError:
                self.page.reload()
                self.page.wait_for_selector(self.Inbox_Frame[1], timeout=20000)
        raise AssertionError(f"Verification email not received after {retries} inbox checks")

    def click_redirect_link(self):
        inbox_frame = self.get_frame(self.Inbox_Frame)
        inbox_frame.get_by_role(self.Email_Item[1], name=self.Email_Item[2]).click()

        mail_frame = self.get_frame(self.Mail_Frame)
        with self.page.expect_popup() as popup_info:
            mail_frame.get_by_role(self.Redirect_Link[1], name=self.Redirect_Link[2]).click()
        new_page = popup_info.value
        self.page = new_page
        self.page.wait_for_load_state()

    def password_change(self, new_password, confirm_password ):
        self.verify_text_visible(self.Update_Password_Redirect)
        self.click(self.Update_Password_Redirect)
        self.fill(self.New_Password, new_password)
        self.fill(self.Confirm_Password, confirm_password)
        


