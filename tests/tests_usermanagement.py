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
    user_m.create_new_user(
        "John",      # first_name
        "Doe",       # middle_name  
        "Smith",     # last_name
        "john.doe1",  # email
        "@yopmail.com",  # domain
        "ANNOTATOR_MT_TTT_MAI_TO_NEP"  # roles
    )
