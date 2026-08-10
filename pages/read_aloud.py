from utilities.custom_logger import Log_Maker
from utilities.read_properties import ReadAloudCofing
from pages.base_page import BasePage
from playwright.sync_api import expect

logger = Log_Maker.log_gen(__name__)


class ReadAloud(BasePage):
    ReadAloud_URL = ReadAloudCofing.get_page_url()
    Base_URL = ReadAloudCofing.get_page_url("Base_URL")
    Navigate_to_ReadAloud = ReadAloudCofing.get_locator("Navigate_Read_Aloud")
    Language_Dropdown = ReadAloudCofing.get_locator("Language_Dropdown")
    Select_Language = ReadAloudCofing.get_locator("Select_Language")
    Click_Input_Box = ReadAloudCofing.get_locator("CLick_Input_Box")
    Input_Text = ReadAloudCofing.get_locator("Input_Text")
    Generate_Audio_Button = ReadAloudCofing.get_locator("Generate_Audio")
    Uploading_Status = ReadAloudCofing.get_locator("Uploading_Status")
    Uploaded_Status = ReadAloudCofing.get_locator("Uploaded_Status")

    def __init__(self, page, base_url=None):
        super().__init__(page, base_url=base_url or self.Base_URL)

    def navigate_to_readalout(self):
        logger.info("Navigating to the Read Aloud page")
        self.click(self.Navigate_to_ReadAloud)
        logger.info(f"Read Aloud page opened at {self.page.url}")

    def select_language(self, language):
        logger.info(f"Selecting Read Aloud language '{language}'")
        dropdown = self.get_locator(self.Language_Dropdown)
        dropdown.click()

        option = self.get_locator(self.Select_Language, language)
        option.click()
        logger.info(f"Read Aloud language set to '{language}'")

    def input_text(self, input_text):
        logger.info(f"Entering {len(input_text)} characters of text to synthesise")
        self.click(self.Click_Input_Box)
        self.fill(self.Input_Text, input_text)
        logger.debug(f"Text entered: '{input_text[:200]}'")

    def generate_tts_and_get_job(self):
        logger.info("Requesting audio generation and waiting for the text_to_speech response")
        locator = self.get_locator(self.Generate_Audio_Button)

        with self.page.expect_response("**/text_to_speech**") as res:
            locator.click()

        response = res.value
        logger.info(f"text_to_speech responded {response.status} for {response.url}")

        try:
            data = response.json()
        except Exception as error:
            logger.error(f"Could not parse the text_to_speech response as JSON: {error}")
            raise Exception("Failed to parse TTS response JSON")

        job_id = data.get("job_id") or data.get("data", {}).get("job_id")
        if job_id is None:
            logger.error(f"No job_id in the text_to_speech response: {data}")
        assert job_id is not None, f"job_id not found in response: {data}"

        logger.info(f"TTS job accepted with job_id={job_id}")
        return job_id

    def audio_status(self):
        logger.debug("Waiting for the audio upload status to appear")
        locator = self.get_locator(self.Uploading_Status)
        try:
            expect(locator).to_be_visible(timeout=50000)
        except AssertionError:
            logger.error("Audio upload status never appeared within 50s")
            raise
        logger.info("Audio upload status is visible")
        return True
