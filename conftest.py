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
from pages.stt_nepali_review import STTNepaliReview

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
    # no_viewport=True makes the page use the real window size, so a
    # maximized window is actually full screen (viewport=None only
    # keeps Playwright's 1280x720 default)
    context = browser.new_context(no_viewport=True)
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


@pytest.fixture(scope="session")
def get_user_credentials():
    """System-login credentials shared by every page fixture.
    login_info.csv stays reserved for the login test cases themselves;
    this file holds the accounts used to get into the app, one per role."""
    df = pd.read_csv("./test_data/user_credentials.csv")

    def _by_role(role):
        row = df[df["role"] == role].iloc[0]
        return row["username"], row["password"]

    return _by_role


# -----------------------------
# DASHBOARD (UI LOGIN + TOKEN)
# -----------------------------
@pytest.fixture(scope="function")
def dashboard(page, get_user_credentials):
    """
    Logs in via UI and returns Home page object
    Also extracts access token for API usage
    """
    username, password = get_user_credentials("admin")

    login = LoginPage(page)
    login.login(username, password)

    home = Home(page)
    # Wait for the dashboard before reading the token from browser storage,
    # otherwise the app may not have stored it yet
    assert home.is_dashboard_loaded()

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


@pytest.fixture(scope="function")
def stt_review(page, get_user_credentials):
    """The review queue belongs to the reviewer role, not the admin."""
    username, password = get_user_credentials("reviewer")

    login = LoginPage(page)
    login.login(username, password)

    return STTNepaliReview(page)


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


# -----------------------------
# "TASKS PROCESSED" COLUMN
# -----------------------------
# Loop-style tests (e.g. approve-all-pending) run many business actions
# inside a single pytest test, so the pass/fail row alone hides how much
# work actually happened. Tests report their count via
# record_property("tasks_processed", n) and it renders as its own column.
def pytest_html_results_table_header(cells):
    cells.insert(2, "<th>Tasks Processed</th>")


def pytest_html_results_table_row(report, cells):
    tasks_processed = next(
        (value for name, value in getattr(report, "user_properties", []) if name == "tasks_processed"),
        "",
    )
    cells.insert(2, f"<td>{tasks_processed}</td>")
