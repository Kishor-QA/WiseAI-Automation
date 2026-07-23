import datetime
import os
import pytest
import pandas as pd
from utilities.custom_logger import Log_Maker

logger = Log_Maker.log_gen()

pytestmark = pytest.mark.ui

# Just enough queries to confirm the chatbot is responding at all;
# full expected-vs-actual coverage lives in test_chatbot_accuracy.py
SMOKE_QUERY_COUNT = 24


@pytest.mark.smoke
def test_chatbot_responds(user_login):
    logger.info("Starting chatbot smoke test")
    chatbot_user = user_login

    chatbot_user.navigate_chatbot()
    logger.info("Navigated to chatbot page")

    df = pd.read_excel("test_data/Query.xlsx", dtype=str).fillna("")
    query_list = df["Queries"].tolist()[:SMOKE_QUERY_COUNT]

    os.makedirs("reports", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"reports/chatbot_smoke_{timestamp}.xlsx"

    results = []
    for idx, query in enumerate(query_list):
        logger.info(f"Processing Query #{idx + 1}: {query}")

        previous_count = chatbot_user.count_responses()
        chatbot_user.type_query(query)

        response_text = chatbot_user.get_response_message(previous_count, timeout=40000)
        logger.info(f"Received Response for query #{idx + 1}: {response_text}")

        assert response_text, f"Empty chatbot response for query #{idx + 1}: {query}"

        results.append({
            "Query": query,
            "Response": response_text,
        })

        # Save after every query so a crash still leaves a usable report
        pd.DataFrame(results).to_excel(results_file, index=False)

    logger.info(f"Chatbot responded to all smoke queries (report: {results_file})")
