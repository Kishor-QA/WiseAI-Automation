from playwright.sync_api import expect
import time
import json
import requests


class BasePage:
    def __init__(self, page, base_url=None):
        self.page = page
        self.token = None 
        self.base_url= base_url # 🔥 shared for UI + API

    # -------------------------
    # LOCATORS (UNCHANGED)
    # -------------------------
    def get_locator(self, locator, value=None):

        if value is not None:
            locator = list(locator)

            # Replace placeholder with actual value
            locator = [value if item == "{value}" else item for item in locator]

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

    def click(self, locator):
        self.get_locator(locator).click()

    def pause(self, seconds: float = 1.5):
        """Deliberate short delay between UI steps where the app needs
        breathing room (uses Playwright's clock, works headless too)."""
        self.page.wait_for_timeout(int(seconds * 1000))

    def fill(self, locator, text):
        self.get_locator(locator).fill(text)

    def is_visible(self, locator):
        return self.get_locator(locator).is_visible()

    def verify_text_visible(self, locator):
        expect(self.get_locator(locator)).to_be_visible(timeout=50000)
    
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
        previous_text = None
        stable = 0
        elapsed = 0
        while elapsed <= timeout_ms:
            current = (element.text_content() or "").strip()
            is_loading = current and current.lower().startswith(self.LOADING_TEXT_PREFIXES)
            if is_loading:
                stable = 0
            elif current and current == previous_text:
                stable += 1
                if stable >= stable_checks:
                    return current
            else:
                stable = 0
            previous_text = current
            self.page.wait_for_timeout(poll_interval_ms)
            elapsed += poll_interval_ms
        return previous_text or ""

    def get_frame(self, locator):
        locator_type, locator_value = locator

        if locator_type != "css":
            raise ValueError("Iframe locator must be CSS type")

        return self.page.frame_locator(locator_value)
# TOKEN HANDLING (NEW)
    # -------------------------
    def init_token(self):
        """
        Extract token from UI session safely using localStorage or sessionStorage.
        """
        storage = self.page.evaluate(
            "() => ({ ...Object.fromEntries(Object.entries(window.localStorage)), ...Object.fromEntries(Object.entries(window.sessionStorage)) })"
        )

        token_keys = [
            'access_token', 'accessToken', 'token', 'auth_token', 'authToken',
            'jwt', 'id_token', 'authorization', 'Authorization'
        ]

        for key in token_keys:
            token = storage.get(key)
            if token:
                self.token = token
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
                            return token

        raise AssertionError("Token not found in browser storage")

    def _get_auth_cookies(self):
        cookies = self.page.context.cookies()
        return {cookie['name']: cookie['value'] for cookie in cookies}

    # -------------------------
    # API: AUTHENTICATED GET
    # -------------------------
    def api_get(self, path, timeout=10):
        """
        Authenticated GET against base_url, reusing the UI session's token and cookies.
        """
        assert self.base_url, "base_url must be configured for API calls"

        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

        headers = {
            "Content-Type": "application/json"
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        return requests.get(url, headers=headers, cookies=self._get_auth_cookies(), timeout=timeout)

    # -------------------------
    # API: TTS POLLING (FIXED)
    # -------------------------
    def poll_tts_result(self, job_id, timeout=120):
        last_status = None
        last_body = None

        for _ in range(timeout // 2):
            res = self.api_get(f"audio/tts_results/{job_id}")
            last_status = res.status_code
            last_body = res.text

            try:
                data = res.json()
            except Exception:
                data = {}

            audio_url = data.get("audio_url") or (data.get("data", {}) or {}).get("audio_url")

            if res.status_code == 200 and audio_url:
                return data

            if res.status_code == 401:
                raise Exception(
                    f"Unauthorized polling TTS result. Check token/cookies. status=401, body={res.text}"
                )

            time.sleep(2)

        raise Exception(
            f"TTS result not available after {timeout}s. last_status={last_status}, last_body={last_body}"
        )
        # -------------------------
    # AUDIO VALIDATION (UNCHANGED)
    # -------------------------
    def validate_audio_url(self, audio_url):
        res = requests.get(audio_url)

        assert res.status_code == 200, "Audio file not accessible"
        assert len(res.content) > 0, "Empty audio file"

        content_type = res.headers.get("content-type", "")
        assert "audio" in content_type or "octet-stream" in content_type

    # -------------------------
    # REMOVED api_call() ❌
    # -------------------------