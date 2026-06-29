import datetime
import os
import pytest
import pandas as pd
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from utilities.read_properties import ReadConfig
from pages.login_page import LoginPage
from pages.home_page import Home
from pages.read_aloud import ReadAloud

load_dotenv()


# -----------------------------
# CLI OPTIONS
# -----------------------------
# -----------------------------

def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default="chromium")
    parser.addoption("--url", action="store", default=None)


def get_target_url(request):
    cli_url = request.config.getoption("--url")
    if cli_url:
        return cli_url

    env_name = os.getenv("ENV", "stage").strip().lower()
    url_key_map = {
        "dev": "DEV_URL",
        "stage": "STAGE_URL",
        "prod": "PROD_URL",
    }
    env_url = os.getenv(url_key_map.get(env_name, "")) or os.getenv("URL")
    if env_url:
        return env_url

    return ReadConfig.get_page_url()


# -----------------------------
# BROWSER SETUP
# -----------------------------
@pytest.fixture(scope="session")
def browser(request):
    browser_name = request.config.getoption("--browser")
    headless = os.getenv("HEADLESS", "true").lower() not in ("0", "false", "no")
    launch_args = ["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"]
    if not headless:
        launch_args.append("--start-maximized")

    with sync_playwright() as p:
        browser_type = getattr(p, browser_name)
        browser = browser_type.launch(headless=headless, args=launch_args)
        yield browser
        browser.close()


# -----------------------------
# PAGE SETUP
# -----------------------------
@pytest.fixture(scope="function")
def context(browser):
    # Use viewport=None so the browser opens at the native maximized window size
    context = browser.new_context(viewport=None)
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context, request):
    url = get_target_url(request)

    page = context.new_page()
    page.goto(url)

    yield page
    page.close()

# -----------------------------
# TEST DATA
# -----------------------------
@pytest.fixture(scope="function")
def get_test_data():
    df = pd.read_csv("./test_data/login_info.csv")
    return df.to_dict(orient="records")


@pytest.fixture(scope="class")
def get_valid_credentials(file_path="./test_data/login_info.csv"):
    df = pd.read_csv(file_path)
    valid_row = df[df['case_type'] == 'valid'].iloc[0]
    return valid_row['username'], valid_row['password']


# -----------------------------
# DASHBOARD (UI LOGIN + TOKEN)
# -----------------------------
@pytest.fixture(scope="function")
def dashboard(page, get_valid_credentials):
    """
    Logs in via UI and returns Home page object
    Also extracts access token for API usage
    """
    username, password = get_valid_credentials

    login = LoginPage(page)
    login.login(username, password)

    home = Home(page)

    # 🔥 Extract token from browser storage
    try:
        home.init_token()
    except AssertionError:
        token = page.evaluate("() => localStorage.getItem('access_token')")
        if not token:
            token = page.evaluate("() => localStorage.getItem('token')")
        home.token = token

    assert home.token is not None, "Unable to extract auth token from browser storage after login"
    return home


@pytest.fixture(scope="function")
def read_aloud(dashboard):
    read_aloud_page = ReadAloud(dashboard.page)
    read_aloud_page.token = dashboard.token
    return read_aloud_page


# -----------------------------
# OPTIONAL: DIRECT TOKEN FIXTURE (for API-heavy tests)
# -----------------------------
@pytest.fixture(scope="function")
def auth_token(dashboard):
    """
    Returns token only (for API tests)
    """
    token = getattr(dashboard, "token", None)
    assert token is not None, "Token not found after login"
    return token


# -----------------------------
# SCREENSHOT ON FAILURE
# -----------------------------
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page = item.funcargs.get("page", None)
        if page:
            page.screenshot(path=f"screenshots/{item.name}.png")

# -----------------------------
# TIMELINED HTML REPORTS
# -----------------------------
def pytest_configure(config):
    htmlpath = getattr(config.option, "htmlpath", None)
    if htmlpath and os.path.basename(htmlpath) == "report.html":
        folder = os.path.dirname(htmlpath) or "reports"
        os.makedirs(folder, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        config.option.htmlpath = os.path.join(folder, f"report_{timestamp}.html")


def pytest_report_header(config):
    htmlpath = getattr(config.option, "htmlpath", None)
    if htmlpath:
        return f"HTML report will be saved to: {htmlpath}"
