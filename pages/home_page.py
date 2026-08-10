from pages.base_page import BasePage
from utilities.custom_logger import Log_Maker
from utilities.read_properties import ReadConfig
from playwright.sync_api import expect

logger = Log_Maker.log_gen(__name__)


class Home(BasePage):

    def is_dashboard_loaded(self):
        logger.debug("Waiting for the dashboard to load")
        locator = self.get_locator(ReadConfig.get_locator("Valid_Login"))
        try:
            expect(locator).to_be_visible(timeout=10000)
        except AssertionError:
            logger.error(f"Dashboard did not load; current URL is {self.page.url}")
            raise
        logger.info(f"Dashboard loaded at {self.page.url}")
        return True

    def get_clients(self):
        locator = ReadConfig.get_locator("Client_Item")
        clients = self.page.locator(locator[1]).all()
        logger.debug(f"Found {len(clients)} client(s) on the dashboard")
        return clients

    def select_client(self, client_name):
        logger.info(f"Selecting client '{client_name}'")
        clients = self.get_clients()

        for client in clients:
            if client.inner_text().strip() == client_name:
                client.click()
                logger.info(f"Client '{client_name}' selected")
                return True

        available = [client.inner_text().strip() for client in clients]
        logger.error(f"Client '{client_name}' not found; available clients: {available}")
        raise Exception(f"Client '{client_name}' not found")
