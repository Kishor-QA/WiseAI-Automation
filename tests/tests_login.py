import pytest
import csv
from pages.login_page import LoginPage
from pages.home_page import Home


def load_test_data():
    with open('test_data/test_login.csv') as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


@pytest.mark.parametrize("data", load_test_data())
def test_login(page, data):
    login = LoginPage(page)

    login.login(data["username"], data["password"])
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

    if data["case_type"] == "both_invalid":
        assert login.is_invalid_login_error_visible()