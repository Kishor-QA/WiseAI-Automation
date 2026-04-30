import requests
import pytest

base_url = "https://back.wiseai.wiseyak.com/"

@pytest.fixture
def token():
    url = f"{base_url}auth/login"

    payload = {
        "username": "org@test.com",
        "password": "Password1@"
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    print("Login Status Code:", response.status_code)
    print("Login Response:", response.text)

    assert response.status_code == 200, "Login failed"

    data = response.json()
    token = data.get("access_token")

    assert token is not None, "Token not found in response"

    return token


def test_api_call(token):
    tts_url = f"{base_url}audio/tts_results/4538d93f-b642-40b5-9e65-043b8905472b"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.get(tts_url, headers=headers)
    tts_data = response.json()

    print("TTS Status Code:", response.status_code)
    print("TTS Response:", response.text)

    assert response.status_code == 200
    tts_audio = tts_data.get("audio_url")
    print("TTS Audio is: ", tts_audio)