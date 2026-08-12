import datetime
import os
import platform
import shutil
import pytest
import pandas as pd
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from utilities.custom_logger import Log_Maker
from utilities.read_properties import ReadConfig
from utilities.screenshot_helper import attach_failure_screenshot
from pages.login_page import LoginPage
from pages.home_page import Home
from pages.read_aloud import ReadAloud
from pages.stt_nepali_review import STTNepaliReview

load_dotenv()

logger = Log_Maker.log_gen(__name__)

# Lets the failure hook reach the Playwright page of the test that just failed,
# whichever fixture opened it
PAGE_STASH_KEY = pytest.StashKey()


# -----------------------------
# CLI OPTIONS
# -----------------------------
# -----------------------------

def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default="chromium")
    parser.addoption("--url", action="store", default=None)


# Headless Chromium falls back to a 800x600 window, which is narrow enough for
# the app's responsive sidebar to collapse and hide its navigation links, so
# headless runs get an explicit desktop viewport instead of the window size.
HEADLESS_VIEWPORT = {"width": 1920, "height": 1080}


def is_headless():
    return os.getenv("HEADLESS", "true").lower() not in ("0", "false", "no")


def get_target_url(config):
    cli_url = config.getoption("--url")
    if cli_url:
        logger.debug(f"Target URL taken from the --url flag: {cli_url}")
        return cli_url

    env_name = os.getenv("ENV", "stage").strip().lower()
    url_key_map = {
        "dev": "DEV_URL",
        "stage": "STAGE_URL",
        "prod": "PROD_URL",
    }
    env_url = os.getenv(url_key_map.get(env_name, "")) or os.getenv("URL")
    if env_url:
        logger.debug(f"Target URL taken from the '{env_name}' environment: {env_url}")
        return env_url

    fallback_url = ReadConfig.get_page_url()
    logger.debug(f"Target URL taken from config.ini: {fallback_url}")
    return fallback_url


# -----------------------------
# BROWSER SETUP
# -----------------------------
@pytest.fixture(scope="session")
def browser(request):
    browser_name = request.config.getoption("--browser")
    headless = is_headless()
    launch_args = ["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"]
    if not headless:
        launch_args.append("--start-maximized")

    logger.info(f"Launching {browser_name} (headless={headless})")
    with sync_playwright() as p:
        browser_type = getattr(p, browser_name, None)
        if browser_type is None:
            logger.error(f"Unknown browser '{browser_name}'; expected chromium, firefox or webkit")
            raise ValueError(f"Unsupported browser '{browser_name}'")

        browser = browser_type.launch(headless=headless, args=launch_args)
        logger.info(f"{browser_name} {browser.version} launched")

        yield browser

        logger.info(f"Closing {browser_name}")
        browser.close()


# -----------------------------
# PAGE SETUP
# -----------------------------
@pytest.fixture(scope="function")
def context(browser):
    # Headed: no_viewport=True makes the page use the real window size, so a
    # maximized window is actually full screen (viewport=None only keeps
    # Playwright's 1280x720 default).
    # Headless: there is no maximized window to inherit - Chromium would hand
    # over its 800x600 default and collapse the app's responsive sidebar - so
    # a desktop viewport is set explicitly.
    if is_headless():
        context = browser.new_context(viewport=HEADLESS_VIEWPORT)
        logger.debug(
            f"Opened a fresh browser context at {HEADLESS_VIEWPORT['width']}x"
            f"{HEADLESS_VIEWPORT['height']} (isolated cookies and storage)"
        )
    else:
        context = browser.new_context(no_viewport=True)
        logger.debug("Opened a fresh browser context at window size (isolated cookies and storage)")

    yield context

    logger.debug("Closing the browser context")
    context.close()


@pytest.fixture(scope="function")
def page(context, request):
    url = get_target_url(request.config)

    page = context.new_page()
    # Stashed so the failure hook can screenshot the browser even when the crash
    # happened inside a fixture and the test body never ran
    request.node.stash[PAGE_STASH_KEY] = page

    logger.info(f"Opening page {url}")
    try:
        page.goto(url)
    except Exception as error:
        logger.error(f"Could not open {url}: {error}")
        raise
    logger.info(f"Page loaded: {page.url}")

    yield page

    logger.debug(f"Closing page {page.url}")
    page.close()

# -----------------------------
# TEST DATA
# -----------------------------
@pytest.fixture(scope="function")
def get_test_data():
    df = pd.read_csv("./test_data/login_info.csv")
    logger.debug(f"Loaded {len(df)} login test data row(s)")
    return df.to_dict(orient="records")


@pytest.fixture(scope="class")
def get_valid_credentials(file_path="./test_data/login_info.csv"):
    df = pd.read_csv(file_path)
    valid_row = df[df['case_type'] == 'valid'].iloc[0]
    logger.debug(f"Using the valid login credentials of '{valid_row['username']}'")
    return valid_row['username'], valid_row['password']


@pytest.fixture(scope="session")
def get_user_credentials():
    """System-login credentials shared by every page fixture.
    login_info.csv stays reserved for the login test cases themselves;
    this file holds the accounts used to get into the app, one per role."""
    df = pd.read_csv("./test_data/user_credentials.csv")
    logger.debug(f"Loaded system credentials for role(s): {sorted(df['role'].unique())}")

    def _by_role(role):
        matches = df[df["role"] == role]
        if matches.empty:
            logger.error(
                f"No '{role}' account in test_data/user_credentials.csv; "
                f"available roles: {sorted(df['role'].unique())}"
            )
            raise KeyError(f"No credentials configured for role '{role}'")

        row = matches.iloc[0]
        logger.debug(f"Using the '{role}' account '{row['username']}'")
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
    logger.info(f"Setting up the dashboard fixture as admin '{username}'")

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
        logger.warning("Token not found by the storage scan; retrying the known localStorage keys")
        token = page.evaluate("() => localStorage.getItem('access_token')")
        if not token:
            token = page.evaluate("() => localStorage.getItem('token')")
        home.token = token

    if home.token is None:
        logger.error(f"Login as '{username}' succeeded but no auth token could be extracted")
    assert home.token is not None, "Unable to extract auth token from browser storage after login"

    logger.info(f"Dashboard fixture ready for '{username}'")
    return home


@pytest.fixture(scope="function")
def read_aloud(dashboard):
    read_aloud_page = ReadAloud(dashboard.page)
    read_aloud_page.token = dashboard.token
    logger.debug(f"Read Aloud page object ready (base_url={read_aloud_page.base_url})")
    return read_aloud_page


@pytest.fixture(scope="function")
def stt_review(page, get_user_credentials):
    """The review queue belongs to the reviewer role, not the admin."""
    username, password = get_user_credentials("reviewer")
    logger.info(f"Setting up the STT review fixture as reviewer '{username}'")

    login = LoginPage(page)
    login.login(username, password)

    logger.info(f"STT review fixture ready for '{username}'")
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
def _resolve_page(item):
    """Find the Playwright page behind a failing test.

    Every UI fixture is built on the `page` fixture, which stashes the page on
    the node; the funcargs scan is the fallback for a fixture that opens its own
    page or exposes it as a page-object attribute. API tests return None.
    """
    funcargs = getattr(item, "funcargs", None) or {}

    page = item.stash.get(PAGE_STASH_KEY, None) or funcargs.get("page")
    if page is not None:
        return page

    for value in funcargs.values():
        candidate = getattr(value, "page", None)
        if candidate is not None:
            return candidate

    return None


# -----------------------------
# RUN + TEST LIFECYCLE LOGGING
# -----------------------------
def pytest_sessionstart(session):
    logger.info("=" * 70)
    logger.info(
        f"Test run started | env={os.getenv('ENV', 'stage')} "
        f"| browser={session.config.getoption('--browser')} "
        f"| headless={os.getenv('HEADLESS', 'true')} "
        f"| log_level={os.getenv('LOG_LEVEL', 'INFO')}"
    )


def pytest_collection_finish(session):
    logger.info(f"Collected {len(session.items)} test(s) to run")


def pytest_runtest_logstart(nodeid, location):
    logger.info(f"--- START {nodeid}")


def pytest_runtest_logfinish(nodeid, location):
    logger.info(f"--- END {nodeid}")


def pytest_sessionfinish(session, exitstatus):
    logger.info(
        f"Test run finished | collected={session.testscollected} "
        f"| failed={session.testsfailed} | exit status={exitstatus}"
    )
    logger.info("=" * 70)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        if report.passed:
            logger.info(f"PASSED {item.nodeid} in {report.duration:.2f}s")
        elif report.skipped:
            logger.info(f"SKIPPED {item.nodeid}")

    # Setup failures matter as much as call failures: a login or navigation
    # fixture that breaks never reaches the test body, and the screenshot of the
    # browser at that moment is the only evidence of what the app was showing.
    if not report.failed or report.when not in ("setup", "call"):
        return

    stage = "during setup" if report.when == "setup" else "during execution"
    logger.error(f"FAILED {item.nodeid} {stage}\n{report.longreprtext}")

    attach_failure_screenshot(_resolve_page(item), item.name, report)


# -----------------------------
# TIMELINED HTML REPORTS + ALLURE
# -----------------------------
def pytest_configure(config):
    _timestamp_html_report(config)
    _prepare_allure_results(config)


def _timestamp_html_report(config):
    htmlpath = getattr(config.option, "htmlpath", None)
    if htmlpath and os.path.basename(htmlpath) == "report.html":
        folder = os.path.dirname(htmlpath) or "reports"
        os.makedirs(folder, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        config.option.htmlpath = os.path.join(folder, f"report_{timestamp}.html")


def _prepare_allure_results(config):
    """Start each run from an empty results folder and record the environment
    that Allure shows on the report overview.

    Only the xdist controller does this - `--clean-alluredir` runs on every
    worker, so under `-n auto` the workers would wipe each other's results.
    """
    allure_dir = getattr(config.option, "allure_report_dir", None)
    if not allure_dir or config.option.collectonly or hasattr(config, "workerinput"):
        return

    shutil.rmtree(allure_dir, ignore_errors=True)
    os.makedirs(allure_dir, exist_ok=True)
    logger.debug(f"Cleared previous Allure results in {allure_dir}")

    environment = {
        "Environment": os.getenv("ENV", "stage"),
        "Base.URL": get_target_url(config),
        "Browser": config.getoption("--browser"),
        "Headless": os.getenv("HEADLESS", "true"),
        "Python": platform.python_version(),
        "Platform": platform.platform(),
    }

    with open(os.path.join(allure_dir, "environment.properties"), "w", encoding="utf-8") as env_file:
        for key, value in environment.items():
            env_file.write(f"{key}={value}\n")

    logger.debug(f"Wrote Allure environment details: {environment}")


def pytest_report_header(config):
    header = []

    htmlpath = getattr(config.option, "htmlpath", None)
    if htmlpath:
        header.append(f"HTML report will be saved to: {htmlpath}")

    allure_dir = getattr(config.option, "allure_report_dir", None)
    if allure_dir:
        header.append(f"Allure results will be saved to: {allure_dir}")

    return header


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
