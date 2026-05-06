from pages.user_management import UserManagement
from pages.home_page import Home
import pytest

@pytest.fixture(scope="function")
def user_login(dashboard):
    user_m = UserManagement(dashboard.page)
    return user_m

def test_create_user(user_login):
    user_m = user_login

    user_m.navigate_to_user_management()
    # user_m.create_new_user(
    #     "John",      # first_name
    #     "Doe",       # middle_name  
    #     "Smith",     # last_name
    #     "john.doe4",  # email
    #     "@yopmail.com",  # domain
    #     "ANNOTATOR_MT_TTT_MAI_TO_NEP"  # roles
    # )
    # # assert user_m.already_exist_message() is True
    # assert user_m.successful_message() is True

    email_page =user_m.open_new_tab("https://yopmail.com/en/")
    print ("Went to Yopmail")
    user_m.page = email_page
    user_m.verify_email("john.doe5@yopmail.com")

    print("we went to this")
    user_m.click_redirect_link()
    print("Click Redirect Link")
    user_m.password_change("Password1@", "Password1@")