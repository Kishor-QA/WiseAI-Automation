import pytest
from pages.chatbot_page import Chatbot


@pytest.fixture(scope="function")
def user_login(dashboard):
    return Chatbot(dashboard.page)
