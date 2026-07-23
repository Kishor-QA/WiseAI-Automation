import pytest
from pytest_html import extras as extras_api
from utilities.custom_logger import Log_Maker

logger = Log_Maker.log_gen()

pytestmark = pytest.mark.ui

# Safety cap so the loop can never spin forever if the queue keeps refilling
MAX_APPROVALS = 1000


class TestSTTNepaliReview:
    @pytest.mark.smoke
    def test_approve_all_pending_tasks(self, stt_review, extras, record_property):
        logger.info("Starting STT Nepali review approval loop for all pending tasks")

        stt_review.navigate_to_stt_review()
        logger.info("Navigated to STT - Nepali Review")

        approved_tasks = []
        while len(approved_tasks) < MAX_APPROVALS:
            stt_review.open_my_tasks()
            logger.info("Opened My Tasks")

            stt_review.filter_pending_tasks()
            logger.info("Applied the Pending filter")

            if not stt_review.has_pending_task():
                logger.info("No pending tasks left in the queue, stopping the loop")
                break

            task_name = stt_review.select_first_task()
            if task_name is None:
                logger.error("Task detail did not open after clicking the row")
                record_property("tasks_processed", len(approved_tasks))
                extras.append(extras_api.html(
                    "<div><b>Tasks approved: {}</b><ul>{}</ul></div>".format(
                        len(approved_tasks),
                        "".join(f"<li>{name}</li>" for name in approved_tasks) or "<li>None</li>",
                    )
                ))
                pytest.fail(
                    f"Task detail did not open after {len(approved_tasks)} approval(s); "
                    "a pending task row is visible but not clickable/openable"
                )
            logger.info(f"Selected top pending task: '{task_name}'")

            stt_review.approve_task()
            approved_tasks.append(task_name)
            logger.info(f"Approved task {len(approved_tasks)}: '{task_name}'")

            stt_review.close_task()
            logger.info("Dismissed the post-approval dialog")

            stt_review.go_back_to_task_list()
            logger.info("Went back to the My Tasks list")

        approved_count = len(approved_tasks)
        record_property("tasks_processed", approved_count)

        summary_html = "<div><b>Tasks approved: {}</b><ul>{}</ul></div>".format(
            approved_count,
            "".join(f"<li>{name}</li>" for name in approved_tasks) or "<li>None</li>",
        )
        extras.append(extras_api.html(summary_html))

        assert approved_count >= 1, "Expected at least one pending task to approve"
        logger.info(f"Review loop finished after approving {approved_count} task(s)")

        # Pick Another Task flow is disabled for now — re-enable once the
        # button-driven flow is back in scope.
        # assert stt_review.pick_another_task_visible() is True
        # stt_review.pick_another_task()
        # if not stt_review.wait_for_task_loaded():
        #     logger.info("No more tasks available in the queue")
