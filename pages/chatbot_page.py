from utilities.read_properties import ChatbotConfig
from pages.base_page import BasePage

from playwright.sync_api import expect

class Chatbot(BasePage):

    Navigate_Chatbot = ChatbotConfig.get_locator("Navigate_Chatbot")
    Type_Query = ChatbotConfig.get_locator("Type_Query")
    Send_Button = ChatbotConfig.get_locator("Send_Button")
    Response_Message = ChatbotConfig.get_locator("Response_Message")
    Language_Dropdown = ChatbotConfig.get_locator("Language_Dropdown")

    def navigate_chatbot(self):
        self.click(self.Navigate_Chatbot)

    def type_query(self, query):
        input_box = self.get_locator(self.Type_Query)
        input_box.fill(query)

    def select_language(self, language):
        dropdown = self.get_locator(self.Language_Dropdown)
        dropdown.click()
        dropdown.fill(language)  
        dropdown.press("Enter")

    def get_response_message(self, timeout=30000):
        element = self.get_locator(self.Response_Message).last
        expect(element).to_be_visible(timeout=timeout)
        return element.text_content().strip()
