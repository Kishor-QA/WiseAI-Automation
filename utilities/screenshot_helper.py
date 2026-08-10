"""Failure evidence helpers.

Captures a Playwright screenshot and publishes it to both reports (Allure and
pytest-html). Used by the failure hook in conftest.py for every UI test and by
page objects through BasePage.take_screenshot().
"""

import base64
import os
import re
from datetime import datetime

import allure
from pytest_html import extras as extras_api

from utilities.custom_logger import Log_Maker

logger = Log_Maker.log_gen(__name__)

SCREENSHOT_DIR = "screenshots"
DEFAULT_ATTACHMENT_NAME = "Failure Screenshot"

# Windows rejects : * ? " < > | / \ in filenames, and parametrised test ids are
# full of them (e.g. "test_login[user@mail.com-invalid]")
_UNSAFE_FILENAME_CHARS = re.compile(r"[^A-Za-z0-9_.-]+")


def build_screenshot_path(name: str, directory: str = SCREENSHOT_DIR) -> str:
    """screenshots/<test-name>_<timestamp>.png

    The timestamp keeps a re-run from overwriting the evidence of the previous
    failure and keeps parallel workers from colliding on the same file.
    """
    safe_name = _UNSAFE_FILENAME_CHARS.sub("_", str(name)).strip("_") or "screenshot"
    os.makedirs(directory, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    return os.path.join(directory, f"{safe_name}_{timestamp}.png")


def capture_screenshot(page, name: str, directory: str = SCREENSHOT_DIR, full_page: bool = True):
    """Save a screenshot of `page`.

    Returns the file path, or None when there is nothing left to capture - no
    page at all (API tests) or a page the fixture teardown already closed.
    """
    if page is None:
        logger.debug(f"No page available for screenshot '{name}' - nothing to capture")
        return None

    if page.is_closed():
        logger.debug(f"Page already closed for screenshot '{name}' - nothing to capture")
        return None

    path = build_screenshot_path(name, directory)
    page.screenshot(path=path, full_page=full_page)
    logger.debug(f"Captured screenshot of {page.url} to {path}")
    return path


def attach_to_allure(path: str, name: str = DEFAULT_ATTACHMENT_NAME) -> None:
    """Attach a saved screenshot to the Allure result of the running test."""
    allure.attach.file(path, name=name, attachment_type=allure.attachment_type.PNG)


def attach_to_html_report(report, path: str, name: str = DEFAULT_ATTACHMENT_NAME) -> None:
    """Attach a saved screenshot to the pytest-html row of the running test.

    --self-contained-html only embeds images handed over as base64, so the file
    is read back instead of passing the path (which would become a broken link).
    """
    with open(path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("ascii")

    report.extras = getattr(report, "extras", []) + [extras_api.png(encoded, name=name)]


def attach_failure_screenshot(page, name: str, report=None):
    """Capture the failure screenshot and publish it to both reports.

    Returns the file path, or None when no screenshot could be taken. Nothing is
    raised from here: a reporting problem must never replace or mask the real
    test failure, so every issue is logged instead.
    """
    try:
        path = capture_screenshot(page, name)
    except Exception as error:
        logger.error(f"Could not capture failure screenshot for '{name}': {error}")
        return None

    if path is None:
        return None

    logger.error(f"Test '{name}' failed - screenshot saved to {path}")

    try:
        attach_to_allure(path, name=f"{DEFAULT_ATTACHMENT_NAME} - {name}")
        if report is not None:
            attach_to_html_report(report, path)
    except Exception as error:
        logger.error(f"Screenshot saved to {path} but could not be attached to the reports: {error}")

    return path
