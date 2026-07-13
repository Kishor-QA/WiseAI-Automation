import pytest
import requests
from utilities.read_properties import ReadAloudCofing
from utilities.custom_logger import Log_Maker

logger = Log_Maker.log_gen()

pytestmark = pytest.mark.api

BASE_URL = ReadAloudCofing.get_page_url("Base_URL").rstrip("/")


class TestTTSApiHealth:

    @pytest.mark.smoke
    def test_api_service_reachable(self):
        """Critical health check: backend responds and is not erroring."""
        logger.info(f"Checking API service availability at {BASE_URL}")
        res = requests.get(BASE_URL, timeout=10)
        logger.info(f"API health check status={res.status_code} time={res.elapsed.total_seconds():.2f}s")

        assert res.status_code < 500, f"API service returned server error: {res.status_code}"
        assert res.elapsed.total_seconds() < 5, f"API response too slow: {res.elapsed.total_seconds():.2f}s"

    @pytest.mark.smoke
    def test_tts_results_endpoint_authenticated(self, read_aloud):
        """The UI-session token is accepted by the TTS results endpoint."""
        logger.info("Checking authenticated access to TTS results endpoint")
        res = read_aloud.api_get("audio/tts_results/smoke-health-check")
        logger.info(f"TTS results endpoint status={res.status_code}")

        assert res.status_code not in (401, 403), f"Auth token rejected by API: {res.status_code}"
        assert res.status_code < 500, f"TTS results endpoint server error: {res.status_code}"
