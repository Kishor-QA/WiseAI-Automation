from utilities.read_properties import ReadAloudCofing
from pages.base_page import BasePage
from playwright.sync_api import expect

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
        self.click(self.Navigate_to_ReadAloud)

    def input_text(self, input_text):
        print("<<<<<moved to audio>>>>>")
        self.click(self.Language_Dropdown)
        print("<<<<<<<Passed Language Dropdown>>>>>>>")
        self.click(self.Select_Language)
        print("<<<<<Passed Select Language>>>>>")
        self.click(self.Click_Input_Box)
        print("<<<<Input Clicked>>>>")
        self.fill(self.Input_Text, input_text)
        print(f"inputed text is {input_text}")

    def generate_tts_and_get_job(self):
        locator = self.get_locator(self.Generate_Audio_Button)

        with self.page.expect_response("**/text_to_speech**") as res:
            locator.click()

        response = res.value

        try:
            data = response.json()
        except Exception:
            raise Exception("Failed to parse TTS response JSON")

        job_id = data.get("job_id") or data.get("data", {}).get("job_id")
        assert job_id is not None, f"job_id not found in response: {data}"
        return job_id

    def audio_status(self):
        locator = self.get_locator(self.Uploading_Status)
        expect(locator).to_be_visible(timeout=50000)
        return True
    
