from pages.read_aloud import ReadAloud

class TestReadAloud:
    def test_tts_audio(self, read_aloud):
        read_aloud.navigate_to_readalout()
        read_aloud.input_text("Hello i am kishor")

        job_id = read_aloud.generate_tts_and_get_job()

        assert read_aloud.audio_status() is True

        result = read_aloud.poll_tts_result(job_id)
        read_aloud.validate_audio_url(result["audio_url"])

         
