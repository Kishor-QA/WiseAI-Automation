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
    Yopmail_URL =UserManagamentConfig.get_locator("Yopmail_URL")
    Email_Box =UserManagamentConfig.get_locator("Email_Box")

    def navigate_to_user_management(self):
        print("I am here")
        self.click(self.Navigate_User_Management)
        print("I am here")

    def create_new_user(self, first_name,middle_name, last_name, email, domain, roles):
        print("<>/create button")
        self.click(self.Create_New_User)
        print("<>/create button")
        self.fill(self.First_Name, first_name)
        print("<>/create button")
        self.fill(self.Last_Name, last_name)
        self.fill(self.Middle_Name, middle_name)
        print("<>/create button")
        self.fill(self.Email, email)
        self.click(self.Domain_Dropdown)
        self.click(self.Select_Domain)  # Click the option instead of filling it
        self.click(self.Role_Button)
        print("<<<<<<<<<Roles >>>>>>>>>")
        self.click(self.Select_Roles)  # Click the role button instead of filling it
        self.click(self.Create_User)
        


