import datetime
import os
import pytest
import pandas as pd
from utilities.custom_logger import Log_Maker
from utilities.text_utils import similarity_ratio

logger = Log_Maker.log_gen()

pytestmark = pytest.mark.ui

# A response counts as correct when it is at least this similar (0.0-1.0)
# to the expected response after whitespace/case normalization
SIMILARITY_THRESHOLD = 0.85
# The test fails when overall accuracy drops below this percentage
MIN_ACCURACY_PERCENT = 80.0


@pytest.mark.regression
def test_chatbot_response_accuracy(user_login):
    logger.info("Starting chatbot expected-vs-actual accuracy test")
    chatbot_user = user_login

    chatbot_user.navigate_chatbot()
    logger.info("Navigated to chatbot page")

    # Queries + expected responses come from the same source file;
    # it stays read-only, results are written to reports/
    df = pd.read_excel("test_data/Query.xlsx", dtype=str).fillna("")
    assert "Queries" in df.columns, "Query.xlsx must have a 'Queries' column"
    assert "Response" in df.columns, "Query.xlsx must have a 'Response' column with expected answers"

    os.makedirs("reports", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"reports/chatbot_accuracy_{timestamp}.xlsx"

    results = []
    for idx, row in df.iterrows():
        query = row["Queries"].strip()
        expected = row["Response"].strip()

        if not query or not expected:
            logger.warning(f"Skipping row {idx + 1}: missing query or expected response")
            continue

        logger.info(f"Processing Query #{idx + 1}: {query}")

        previous_count = chatbot_user.count_responses()
        chatbot_user.type_query(query)

        actual = chatbot_user.get_response_message(previous_count, timeout=30000)
        assert actual, f"Empty chatbot response for query #{idx + 1}: {query}"

        score = similarity_ratio(expected, actual)
        matched = score >= SIMILARITY_THRESHOLD
        logger.info(
            f"Query #{idx + 1} similarity={score:.2%} -> {'MATCH' if matched else 'MISMATCH'}"
        )

        results.append({
            "Query": query,
            "Expected_Response": expected,
            "Actual_Response": actual,
            "Similarity_%": round(score * 100, 2),
            "Result": "PASS" if matched else "FAIL",
        })

        # Save after every query so a crash still leaves a usable report
        pd.DataFrame(results).to_excel(results_file, index=False)

    assert results, "No usable query/expected-response rows found in Query.xlsx"

    total = len(results)
    matched_count = sum(1 for r in results if r["Result"] == "PASS")
    accuracy = matched_count / total * 100

    # Append a summary row so the report carries the final score
    summary = {
        "Query": "OVERALL ACCURACY",
        "Expected_Response": f"{matched_count}/{total} matched",
        "Actual_Response": f"threshold {SIMILARITY_THRESHOLD:.0%} per response",
        "Similarity_%": round(accuracy, 2),
        "Result": "PASS" if accuracy >= MIN_ACCURACY_PERCENT else "FAIL",
    }
    pd.DataFrame(results + [summary]).to_excel(results_file, index=False)

    logger.info(f"Chatbot accuracy: {matched_count}/{total} = {accuracy:.2f}% (report: {results_file})")

    assert accuracy >= MIN_ACCURACY_PERCENT, (
        f"Chatbot accuracy {accuracy:.2f}% is below the required "
        f"{MIN_ACCURACY_PERCENT:.2f}% ({matched_count}/{total} matched). "
        f"See {results_file} for per-query details."
    )
