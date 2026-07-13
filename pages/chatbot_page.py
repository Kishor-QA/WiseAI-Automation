from utilities.read_properties import ChatbotConfig
from pages.base_page import BasePage

from playwright.sync_api import expect

class Chatbot(BasePage):

    Navigate_Chatbot = ChatbotConfig.get_locator("Navigate_Chatbot")
    Type_Query = ChatbotConfig.get_locator("Type_Query")
    Send_Button = ChatbotConfig.get_locator("Send_Button")
    Response_Message = ChatbotConfig.get_locator("Response_Message")
    Language_Dropdown = ChatbotConfig.get_locator("Language_Dropdown")
    Select_Language = ChatbotConfig.get_locator("Select_Language")

    def navigate_chatbot(self):
        self.click(self.Navigate_Chatbot)

    def type_query(self, query):
        input_box = self.get_locator(self.Type_Query)
        input_box.fill(query)
        input_box.press("Enter")

    def select_language(self, language):
        dropdown = self.get_locator(self.Language_Dropdown)
        dropdown.click()

        option = self.get_locator(self.Select_Language, language).nth(2)
        option.click()
    
    def count_responses(self):
        return self.get_locator(self.Response_Message).count()

    def get_response_message(self, previous_count=0, timeout=100000):
        responses = self.get_locator(self.Response_Message)
        expect(responses).not_to_have_count(previous_count, timeout=timeout)
        element = responses.last
        expect(element).to_be_visible(timeout=timeout)
        return self.wait_for_stable_text(element)
