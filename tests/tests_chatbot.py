from pages.chatbot_page import Chatbot
import pytest
import pandas as pd
import time
from utilities.custom_logger import Log_Maker

logger = Log_Maker.log_gen()


@pytest.fixture(scope="function")
def user_login(dashboard):
    return Chatbot(dashboard.page)


def test_chatbot(user_login):
    logger.info("Starting chatbot query validation test")
    chatbot_user = user_login

    chatbot_user.navigate_chatbot()
    logger.info("Navigated to chatbot page")

    time.sleep(3)

    excel_file = "test_data/Query.xlsx"

    # Read excel and convert all columns to string
    df = pd.read_excel(excel_file, dtype=str).fillna("")

    # Create Response column if not present
    if "Response" not in df.columns:
        df["Response"] = ""

    query_list = df["Queries"].tolist()
    chatbot_user.select_language("मैथिली")
    for idx, query in enumerate(query_list):
        logger.info(f"Processing Query #{idx + 1}: {query}")

        chatbot_user.type_query(query)

        # Wait for chatbot response generation
        time.sleep(7)

        response_text = chatbot_user.get_response_message(timeout=30000)
        logger.info(f"Received Response for query #{idx + 1}: {response_text}")

        # Save response into dataframe
        df.at[idx, "Response"] = response_text

        # Save after every query
        df.to_excel(excel_file, index=False)
        logger.info(f"Saved response for query #{idx + 1} to {excel_file}")

    logger.info("All chatbot responses saved successfully.")