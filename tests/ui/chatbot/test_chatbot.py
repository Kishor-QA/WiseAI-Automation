import datetime
import os
from pages.chatbot_page import Chatbot
import pytest
import pandas as pd
from utilities.custom_logger import Log_Maker

logger = Log_Maker.log_gen()

pytestmark = pytest.mark.ui


@pytest.fixture(scope="function")
def user_login(dashboard):
    return Chatbot(dashboard.page)


@pytest.mark.regression
def test_chatbot(user_login):
    logger.info("Starting chatbot query validation test")
    chatbot_user = user_login

    chatbot_user.navigate_chatbot()
    logger.info("Navigated to chatbot page")

    # Read queries (source test data stays read-only)
    df = pd.read_excel("test_data/Query.xlsx", dtype=str).fillna("")
    if "Response" not in df.columns:
        df["Response"] = ""

    # Responses are written to reports/ so the test data is never mutated
    os.makedirs("reports", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"reports/chatbot_responses_{timestamp}.xlsx"

    query_list = df["Queries"].tolist()
    # chatbot_user.select_language("मैथिली")
    for idx, query in enumerate(query_list):
        logger.info(f"Processing Query #{idx + 1}: {query}")

        previous_count = chatbot_user.count_responses()
        chatbot_user.type_query(query)

        response_text = chatbot_user.get_response_message(previous_count, timeout=30000)
        logger.info(f"Received Response for query #{idx + 1}: {response_text}")

        assert response_text, f"Empty chatbot response for query #{idx + 1}: {query}"

        # Save response into dataframe
        df.at[idx, "Response"] = response_text

        # Save after every query
        df.to_excel(results_file, index=False)
        logger.info(f"Saved response for query #{idx + 1} to {results_file}")

    logger.info(f"All chatbot responses saved successfully to {results_file}")
