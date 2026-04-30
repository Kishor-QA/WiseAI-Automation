from pages.base_page import BasePage
from utilities.read_properties import ReadConfig
from playwright.sync_api import expect


class Home(BasePage):

    def is_dashboard_loaded(self):
        locator = self.get_locator(ReadConfig.get_locator("Valid_Login"))
        expect(locator).to_be_visible(timeout=10000)
        return True

    def get_clients(self):
        locator = ReadConfig.get_locator("Client_Item")
        return self.page.locator(locator[1]).all()

    def select_client(self, client_name):
        clients = self.get_clients()

        for client in clients:
            if client.inner_text().strip() == client_name:
                client.click()
                return True

        raise Exception(f"Client '{client_name}' not found")