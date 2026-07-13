import pytest
import csv
from pages.login_page import LoginPage
from pages.home_page import Home
from utilities.custom_logger import Log_Maker

logger = Log_Maker.log_gen()

pytestmark = pytest.mark.ui


def load_test_data():
    with open('test_data/login_info.csv') as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


def load_login_params():
    """Valid login is business-critical (smoke); all other cases are regression."""
    params = []
    for row in load_test_data():
        suite_mark = pytest.mark.smoke if row["case_type"] == "valid" else pytest.mark.regression
        params.append(pytest.param(row, marks=suite_mark, id=row["case_type"]))
    return params


@pytest.mark.parametrize("data", load_login_params())
def test_login(page, data):
    logger.info(f"Starting login test: case_type={data['case_type']} username={data['username']}")
    login = LoginPage(page)

    login.login(data["username"], data["password"])
    logger.info("Submitted login form")
    # page.screenshot(path=f"screenshots/screenshot_{data['case_type']}.png")
    if data["case_type"] == "valid":
        home = Home(page)
        assert home.is_dashboard_loaded()

    if data["case_type"] == "invalid":
        assert login.is_invalid_login_error_visible()

    if data["case_type"] == "empty":
        assert login.is_empty_username_error_visible()

    if data["case_type"] == "username_empty":
        assert login.is_empty_username_error_visible()

    if data["case_type"] == "password_empty":
        assert login.is_empty_password_error_visible()

    if data["case_type"] == "username_invalid":
        assert login.is_invalid_login_error_visible()

    if data["case_type"] == "password_invalid":
        assert login.is_invalid_login_error_visible()
        logger.info("Invalid password login error displayed")

    if data["case_type"] == "both_invalid":
        assert login.is_invalid_login_error_visible()
        logger.info("Both credentials invalid login error displayed")

    logger.info(f"Completed login test: case_type={data['case_type']}")