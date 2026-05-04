import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://dev.wiseai.wiseyak.com/login")
    page.get_by_role("textbox", name="Enter your username").click()
    page.get_by_role("textbox", name="Enter your username").fill("org@test.com")
    page.get_by_role("textbox", name="Enter your password").click()
    page.get_by_role("textbox", name="Enter your password").fill("Password1@")
    page.get_by_role("textbox", name="Enter your password").press("Shift+Enter")
    page.get_by_role("button", name="Login").click()
    page.get_by_role("link", name="User Management").click()
    page.get_by_role("button", name="Create New User").click()
    page.get_by_role("textbox", name="Enter first name").click()
    page.get_by_role("textbox", name="Enter first name").fill("Testing ")
    page.get_by_role("textbox", name="Enter last name").click()
    page.get_by_role("textbox", name="Enter last name").fill("User")
    page.get_by_role("textbox", name="Enter email prefix").click()
    page.get_by_role("textbox", name="Enter email prefix").fill("testinguser")
    page.get_by_role("combobox").click()
    page.get_by_role("option", name="@yopmail.com").click()
    page.get_by_role("button", name="Select roles").click()
    page.get_by_role("button", name="ANNOTATOR_MT_TTT_MAI_TO_NEP").click()
    page.get_by_text("CancelCreate User").click()
    page.get_by_role("button", name="Create User").click()
    page.get_by_role("textbox", name="Enter first name").fill("Testing ")
    page.get_by_role("button", name="Create User").click()
    page.get_by_role("textbox", name="Enter first name").fill("Testing")
    page.get_by_role("button", name="Create User").click()
    page.goto("https://dev.wiseai.wiseyak.com/user-management")
    page1 = context.new_page()
    page1.goto("https://yopmail.com/")
    page1.get_by_role("textbox", name="Login").click()
    page1.get_by_role("textbox", name="Login").fill("testinguser")
    page1.get_by_title("Check Inbox @yopmail.com").click()
    page1.locator("iframe[name=\"ifinbox\"]").content_frame.get_by_role("button", name="10:46 WiseAI Support Update").click()
    with page1.expect_popup() as page2_info:
        page1.locator("iframe[name=\"ifmail\"]").content_frame.get_by_role("link", name="Link to account update").click()
    page2 = page2_info.value
    page2.get_by_role("link", name="» Click here to proceed").click()
    page2.get_by_role("textbox", name="New Password").click()
    page2.get_by_text("You need to change your").click()
    page2.get_by_text("Update password").click()
    page2.get_by_role("textbox", name="New Password").click()
    page2.get_by_role("textbox", name="New Password").fill("Password1@")
    page2.get_by_role("button", name="Show password").first.click()
    page2.get_by_role("textbox", name="Confirm password").click()
    page2.get_by_role("textbox", name="Confirm password").fill("Password1@")
    page2.get_by_role("button", name="Submit").click()
    page2.get_by_role("link", name="« Back to Application").click()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
