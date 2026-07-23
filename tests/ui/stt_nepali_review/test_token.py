import pytest
from pytest_html import extras as extras_api
from utilities.custom_logger import Log_Maker

logger = Log_Maker.log_gen()

pytestmark = pytest.mark.ui

# Safety cap so the loop can never spin forever if the list keeps refilling
MAX_PICKS = 1000


class TestPickAnnotatedTasks:
    @pytest.mark.smoke
    def test_pick_all_available_tasks(self, stt_review, extras, record_property):
        logger.info("Starting pick-all loop for the Annotated Tasks list")

        stt_review.navigate_to_stt_review()
        logger.info("Navigated to STT - Nepali Review")

        stt_review.open_annotated_tasks()
        logger.info("Opened Annotated Tasks")

        picked_count = 0
        while picked_count < MAX_PICKS:
            if not stt_review.has_pickable_task():
                logger.info("No more tasks available to pick")
                break

            if not stt_review.pick_first_task():
                logger.info("Remaining Pick buttons are disabled, stopping the loop")
                break

            picked_count += 1
            logger.info(f"Picked task {picked_count}")

        record_property("tasks_processed", picked_count)
        extras.append(extras_api.html(f"<div><b>Tasks picked: {picked_count}</b></div>"))

        assert picked_count >= 1, "Expected at least one task available to pick"
        logger.info(f"Pick loop finished after picking {picked_count} task(s)")
