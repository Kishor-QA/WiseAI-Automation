from utilities.custom_logger import Log_Maker
from utilities.read_properties import ChatbotConfig
from pages.base_page import BasePage

from playwright.sync_api import expect

logger = Log_Maker.log_gen(__name__)


class Chatbot(BasePage):

    Navigate_Chatbot = ChatbotConfig.get_locator("Navigate_Chatbot")
    Type_Query = ChatbotConfig.get_locator("Type_Query")
    Send_Button = ChatbotConfig.get_locator("Send_Button")
    Response_Message = ChatbotConfig.get_locator("Response_Message")
    Language_Dropdown = ChatbotConfig.get_locator("Language_Dropdown")
    Select_Language = ChatbotConfig.get_locator("Select_Language")

    def navigate_chatbot(self):
        logger.info("Navigating to the Chatbot page")
        self.click(self.Navigate_Chatbot)
        logger.info(f"Chatbot page opened at {self.page.url}")

    def type_query(self, query):
        logger.info(f"Sending chatbot query: '{query}'")
        input_box = self.get_locator(self.Type_Query)
        input_box.fill(query)
        input_box.press("Enter")
        logger.debug("Query submitted with Enter")

    def select_language(self, language):
        logger.info(f"Switching chatbot language to '{language}'")
        dropdown = self.get_locator(self.Language_Dropdown)
        dropdown.click()

        option = self.get_locator(self.Select_Language, language)
        option.click()
        logger.info(f"Chatbot language set to '{language}'")

    def count_responses(self):
        count = self.get_locator(self.Response_Message).count()
        logger.debug(f"Chatbot currently shows {count} response message(s)")
        return count

    def get_response_message(self, previous_count=0, timeout=100000):
        logger.debug(f"Waiting for a new chatbot response (previous_count={previous_count})")
        responses = self.get_locator(self.Response_Message)

        try:
            expect(responses).not_to_have_count(previous_count, timeout=timeout)
        except AssertionError:
            logger.error(
                f"No new chatbot response arrived within {timeout}ms "
                f"(still {previous_count} message(s))"
            )
            raise

        element = responses.last
        expect(element).to_be_visible(timeout=timeout)

        message = self.wait_for_stable_text(element)
        logger.info(f"Chatbot response received ({len(message)} chars): '{message[:200]}'")
        return message
