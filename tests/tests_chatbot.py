from pathlib import Path

from pages.chatbot_page import Chatbot
import pytest
import pandas as pd
import time

@pytest.fixture(scope="function")
def user_login(dashboard):
    return Chatbot(dashboard.page)


def test_chatbot(user_login):
    chatbot_user = user_login
    chatbot_user.navigate_chatbot()

    excel_file = Path("test_data") / "Query.xlsx"
    df = pd.read_excel(excel_file)

    if "Response" not in df.columns:
        df["Response"] = ""

    query_list = df["Queries"].tolist()
    responses = []

    for idx, query in enumerate(query_list):
        print(f"Processing query #{idx + 1}: {query}")
        chatbot_user.type_query(query)
        time.sleep(3)
        response_text = chatbot_user.get_response_message(timeout=30000)
        print(f"Received response: {response_text}")
        responses.append(response_text)

 

        

