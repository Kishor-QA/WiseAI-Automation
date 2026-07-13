import pytest
from pages.read_aloud import ReadAloud
from utilities.custom_logger import Log_Maker

logger = Log_Maker.log_gen()

pytestmark = pytest.mark.ui


class TestReadAloud:
    @pytest.mark.smoke
    def test_tts_audio(self, read_aloud):
        logger.info("Starting text-to-speech audio test")
        read_aloud.navigate_to_readalout()
        logger.info("Navigated to read aloud page")

        read_aloud.select_language("ENGLISH")
        read_aloud.input_text( "Hello i am kishor")
        logger.info("Entered text for TTS generation")

        job_id = read_aloud.generate_tts_and_get_job()
        logger.info(f"The job id is {job_id}")
        assert read_aloud.audio_status() is True
        logger.info("Audio status check passed")

        result = read_aloud.poll_tts_result(job_id)
        logger.info(f"Polled TTS result: {result}")
        read_aloud.validate_audio_url(result["audio_url"])
        logger.info("Audio URL validation completed")

         
