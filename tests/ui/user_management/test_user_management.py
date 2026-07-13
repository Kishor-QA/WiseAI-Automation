from datetime import datetime
from pages.user_management import UserManagement
import pytest
from utilities.custom_logger import Log_Maker


logger = Log_Maker.log_gen()

pytestmark = pytest.mark.ui

@pytest.fixture(scope="function")
def user_login(dashboard):
    user_m = UserManagement(dashboard.page)
    return user_m


def unique_email_prefix():
    """Dynamic email keeps the test repeatable across runs."""
    return f"autouser{datetime.now().strftime('%Y%m%d%H%M%S')}"


@pytest.mark.smoke
def test_create_user(user_login):
    user_m = user_login
    email_prefix = unique_email_prefix()

    user_m.navigate_to_user_management()
    logger.info(f"Creating new user with email prefix {email_prefix}")
    user_m.create_new_user("Auto", "Test", "User", email_prefix)
    assert user_m.successful_message() is True
    logger.info("User created successfully")


@pytest.mark.regression
@pytest.mark.skip(reason="Stage creates users under the fixed @aloi.com domain; "
                         "Yopmail inbox verification is impossible until a public email domain option returns")
def test_new_user_email_verification(user_login):
    user_m = user_login
    email_prefix = unique_email_prefix()
    email = f"{email_prefix}@yopmail.com"

    user_m.navigate_to_user_management()
    logger.info(f"Creating new user with email {email}")
    user_m.create_new_user("Auto", "Test", "User", email_prefix)
    assert user_m.successful_message() is True

    email_page = user_m.open_new_tab(user_m.Yopmail_URL)
    logger.info("Opened Yopmail in new tab")
    user_m.page = email_page
    user_m.verify_email(email)
    user_m.wait_for_verification_email()
    logger.info("Verification email received on Yopmail")

    user_m.click_redirect_link()
    logger.info("Clicked redirect link")
    user_m.password_change("Password1@", "Password1@")
    logger.info("Completed password change flow")
