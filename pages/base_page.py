from playwright.sync_api import expect
import time
import json
import requests

from utilities.custom_logger import Log_Maker, mask_secret
from utilities.screenshot_helper import attach_to_allure, capture_screenshot

logger = Log_Maker.log_gen(__name__)


class BasePage:
    def __init__(self, page, base_url=None):
        self.page = page
        self.token = None
        self.base_url= base_url # 🔥 shared for UI + API
        logger.debug(f"Initialised {type(self).__name__} (base_url={base_url})")

    # -------------------------
    # LOCATORS (UNCHANGED)
    # -------------------------
    def get_locator(self, locator, value=None):

        if value is not None:
            locator = list(locator)

            # Replace placeholder with actual value
            locator = [value if item == "{value}" else item for item in locator]

        logger.trace(f"Resolving locator {tuple(locator)}")

        if locator[0] == "role":
            if len(locator) == 3:
                return self.page.get_by_role(locator[1], name=locator[2])
            return self.page.get_by_role(locator[1])

        elif locator[0] == "link":
            return self.page.get_by_role("link", name=locator[1])

        elif locator[0] == "css":
            return self.page.locator(locator[1])

        elif locator[0] == "locator":
            return self.page.locator(locator[1])

        elif locator[0] == "text":
            return self.page.get_by_text(locator[1], exact=False)

        elif locator[0] == "placeholder":
            return self.page.get_by_placeholder(locator[1])

        elif locator[0] == "role_nth":
            return self.page.get_by_role(locator[1]).nth(int(locator[2]))

        elif locator[0] == "role_exact":
            return self.page.get_by_role(locator[1], name=locator[2], exact=True)

        # Without this the caller received None and failed later with a
        # confusing "NoneType has no attribute click"
        logger.error(f"Unsupported locator type '{locator[0]}' in {tuple(locator)}")
        raise ValueError(f"Unsupported locator type '{locator[0]}' in {tuple(locator)}")

    def click(self, locator):
        logger.debug(f"Clicking {tuple(locator)}")
        try:
            self.get_locator(locator).click()
        except Exception as error:
            logger.error(f"Failed to click {tuple(locator)}: {error}")
            raise

    def pause(self, seconds: float = 1.5):
        """Deliberate short delay between UI steps where the app needs
        breathing room (uses Playwright's clock, works headless too)."""
        logger.trace(f"Pausing for {seconds}s")
        self.page.wait_for_timeout(int(seconds * 1000))

    def fill(self, locator, text, mask=False):
        """Set `mask=True` for passwords and other secrets so the value is
        never written to the log file - only its length is."""
        logger.debug(f"Filling {tuple(locator)} with {mask_secret(text) if mask else repr(text)}")
        try:
            self.get_locator(locator).fill(text)
        except Exception as error:
            logger.error(f"Failed to fill {tuple(locator)}: {error}")
            raise

    def is_visible(self, locator):
        visible = self.get_locator(locator).is_visible()
        logger.debug(f"Visibility of {tuple(locator)}: {visible}")
        return visible

    def verify_text_visible(self, locator):
        logger.debug(f"Waiting for {tuple(locator)} to become visible")
        try:
            expect(self.get_locator(locator)).to_be_visible(timeout=50000)
        except AssertionError as error:
            logger.error(f"Element {tuple(locator)} never became visible: {error}")
            raise
        logger.debug(f"Element {tuple(locator)} is visible")

    # Text shown by chatbot-style UIs while a response is still being generated
    # (the real string is "Thinking …" - a Unicode ellipsis, not "...");
    # matched with startswith so trailing punctuation/whitespace can't slip through.
    LOADING_TEXT_PREFIXES = ("thinking",)

    def wait_for_stable_text(self, element, stable_checks=3, poll_interval_ms=1000, timeout_ms=60000):
        """
        Wait until an element's text stops changing (needed for streamed/typed-out
        responses where visibility alone does not mean the text is complete).
        Placeholder/loading text (e.g. "Thinking …") is never treated as stable.
        """
        logger.debug(
            f"Waiting for text to stabilise (stable_checks={stable_checks}, timeout={timeout_ms}ms)"
        )
        previous_text = None
        stable = 0
        elapsed = 0
        while elapsed <= timeout_ms:
            current = (element.text_content() or "").strip()
            is_loading = current and current.lower().startswith(self.LOADING_TEXT_PREFIXES)
            if is_loading:
                logger.trace(f"Still loading after {elapsed}ms: '{current}'")
                stable = 0
            elif current and current == previous_text:
                stable += 1
                logger.trace(f"Text unchanged ({stable}/{stable_checks}) after {elapsed}ms")
                if stable >= stable_checks:
                    logger.debug(f"Text stabilised after {elapsed}ms ({len(current)} chars)")
                    return current
            else:
                stable = 0
            previous_text = current
            self.page.wait_for_timeout(poll_interval_ms)
            elapsed += poll_interval_ms

        logger.warning(
            f"Text did not stabilise within {timeout_ms}ms; returning the last value seen "
            f"({len(previous_text or '')} chars)"
        )
        return previous_text or ""

    def take_screenshot(self, name="screenshot"):
        """Save a screenshot under screenshots/ and attach it to the Allure report.

        Failures are captured automatically by the conftest hook - use this only
        when a page action needs extra evidence on a passing run (e.g. the state
        of a queue before an approval loop starts).
        """
        path = capture_screenshot(self.page, name)
        if path:
            logger.info(f"Screenshot saved to {path}")
            attach_to_allure(path, name=name)
        else:
            logger.warning(f"Screenshot '{name}' skipped - the page is already closed")
        return path

    def get_frame(self, locator):
        locator_type, locator_value = locator

        if locator_type != "css":
            logger.error(f"Iframe locator must be CSS type, got '{locator_type}'")
            raise ValueError("Iframe locator must be CSS type")

        logger.debug(f"Switching to iframe '{locator_value}'")
        return self.page.frame_locator(locator_value)
# TOKEN HANDLING (NEW)
    # -------------------------
    def init_token(self):
        """
        Extract token from UI session safely using localStorage or sessionStorage.
        """
        logger.debug("Reading auth token from browser local/session storage")
        storage = self.page.evaluate(
            "() => ({ ...Object.fromEntries(Object.entries(window.localStorage)), ...Object.fromEntries(Object.entries(window.sessionStorage)) })"
        )
        logger.trace(f"Browser storage keys: {sorted(storage.keys())}")

        token_keys = [
            'access_token', 'accessToken', 'token', 'auth_token', 'authToken',
            'jwt', 'id_token', 'authorization', 'Authorization'
        ]

        for key in token_keys:
            token = storage.get(key)
            if token:
                self.token = token
                logger.info(f"Auth token found under storage key '{key}' {mask_secret(token)}")
                return token

        # fallback when the token is stored inside a JSON string value
        for value in storage.values():
            if isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
                try:
                    obj = json.loads(value)
                except Exception:
                    continue

                if isinstance(obj, dict):
                    for key in token_keys:
                        token = obj.get(key)
                        if token:
                            self.token = token
                            logger.info(
                                f"Auth token found nested under JSON key '{key}' {mask_secret(token)}"
                            )
                            return token

        logger.error(
            f"No auth token in browser storage; keys present: {sorted(storage.keys())}"
        )
        raise AssertionError("Token not found in browser storage")

    def _get_auth_cookies(self):
        cookies = self.page.context.cookies()
        logger.trace(f"Session carries {len(cookies)} cookie(s): {[c['name'] for c in cookies]}")
        return {cookie['name']: cookie['value'] for cookie in cookies}

    # -------------------------
    # API: AUTHENTICATED GET
    # -------------------------
    def api_get(self, path, timeout=10):
        """
        Authenticated GET against base_url, reusing the UI session's token and cookies.
        """
        if not self.base_url:
            logger.error("API GET attempted without a base_url configured")
            raise AssertionError("base_url must be configured for API calls")

        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

        headers = {
            "Content-Type": "application/json"
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        # The Authorization value is deliberately never logged
        logger.info(f"API request: GET {url} (authenticated={bool(self.token)}, timeout={timeout}s)")

        try:
            response = requests.get(
                url, headers=headers, cookies=self._get_auth_cookies(), timeout=timeout
            )
        except requests.RequestException as error:
            logger.error(f"API request failed: GET {url}: {error}")
            raise

        elapsed = response.elapsed.total_seconds()
        log = logger.info if response.ok else logger.error
        log(f"API response: GET {url} -> {response.status_code} in {elapsed:.2f}s "
            f"({len(response.content)} bytes)")
        logger.debug(f"API response body: {response.text[:1000]}")

        return response

    # -------------------------
    # API: TTS POLLING (FIXED)
    # -------------------------
    def poll_tts_result(self, job_id, timeout=120):
        last_status = None
        last_body = None
        attempts = timeout // 2

        logger.info(f"Polling TTS result for job_id={job_id} (up to {attempts} attempts / {timeout}s)")

        for attempt in range(1, attempts + 1):
            res = self.api_get(f"audio/tts_results/{job_id}")
            last_status = res.status_code
            last_body = res.text

            try:
                data = res.json()
            except Exception as error:
                logger.debug(f"Attempt {attempt}: response was not valid JSON ({error})")
                data = {}

            audio_url = data.get("audio_url") or (data.get("data", {}) or {}).get("audio_url")

            if res.status_code == 200 and audio_url:
                logger.info(f"TTS job {job_id} ready after {attempt} attempt(s): {audio_url}")
                return data

            if res.status_code == 401:
                logger.error(
                    f"Unauthorized polling TTS job {job_id} - token or cookies rejected: {res.text}"
                )
                raise Exception(
                    f"Unauthorized polling TTS result. Check token/cookies. status=401, body={res.text}"
                )

            logger.debug(f"Attempt {attempt}/{attempts}: job {job_id} not ready (status={last_status})")
            time.sleep(2)

        logger.error(
            f"TTS job {job_id} never produced an audio_url within {timeout}s "
            f"(last_status={last_status})"
        )
        raise Exception(
            f"TTS result not available after {timeout}s. last_status={last_status}, last_body={last_body}"
        )
        # -------------------------
    # AUDIO VALIDATION (UNCHANGED)
    # -------------------------
    def validate_audio_url(self, audio_url):
        logger.info(f"Validating generated audio at {audio_url}")
        res = requests.get(audio_url)

        content_type = res.headers.get("content-type", "")
        logger.info(
            f"Audio response: {res.status_code}, {len(res.content)} bytes, content-type='{content_type}'"
        )

        if res.status_code != 200:
            logger.error(f"Audio file not accessible: status={res.status_code}")
        assert res.status_code == 200, "Audio file not accessible"

        if not res.content:
            logger.error(f"Audio file at {audio_url} is empty")
        assert len(res.content) > 0, "Empty audio file"

        if "audio" not in content_type and "octet-stream" not in content_type:
            logger.error(f"Unexpected audio content-type '{content_type}' for {audio_url}")
        assert "audio" in content_type or "octet-stream" in content_type

    # -------------------------
    # REMOVED api_call() ❌
    # -------------------------