from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from utilities.read_properties import STTNepaliReviewConfig
from pages.base_page import BasePage


class STTNepaliReview(BasePage):

    Navigate_STT_Review = STTNepaliReviewConfig.get_locator("Navigate_STT_Review")
    My_Tasks = STTNepaliReviewConfig.get_locator("My_Tasks")
    Annotated_Tasks = STTNepaliReviewConfig.get_locator("Annotated_Tasks")
    Pick_Button = STTNepaliReviewConfig.get_locator("Pick_Button")
    Show_Filters = STTNepaliReviewConfig.get_locator("Show_Filters")
    Pending_Filter = STTNepaliReviewConfig.get_locator("Pending_Filter")
    First_Task_Row = STTNepaliReviewConfig.get_locator("First_Task_Row")
    Approve_Button = STTNepaliReviewConfig.get_locator("Approve_Button")
    Close_Task = STTNepaliReviewConfig.get_locator("Close_Task")
    Cancel_Task_Prompt = STTNepaliReviewConfig.get_locator("Cancel_Task_Prompt")
    Go_Back = STTNepaliReviewConfig.get_locator("Go_Back")
    # Pick_Another_Task = STTNepaliReviewConfig.get_locator("Pick_Another_Task")

    def navigate_to_stt_review(self):
        # The link exists in both the sidebar and the dashboard cards,
        # so pick the first match to avoid a strict-mode violation
        self.get_locator(self.Navigate_STT_Review).first.click()

    def open_my_tasks(self):
        self.click(self.My_Tasks)
        self.pause(1)

    def open_annotated_tasks(self):
        self.click(self.Annotated_Tasks)

    def _enabled_pick_button(self):
        """Once the reviewer's task limit is reached the remaining Pick
        buttons stay visible but disabled, so only enabled ones count."""
        return self.get_locator(self.Pick_Button).and_(self.page.locator("button:enabled")).first

    def has_pickable_task(self, timeout: int = 30000) -> bool:
        """Non-failing check so the pick loop can stop cleanly
        once no enabled Pick buttons are left in the list."""
        try:
            self._enabled_pick_button().wait_for(state="visible", timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            return False

    def pick_first_task(self, timeout: int = 30000) -> bool:
        """Pick the first enabled task. Returns False instead of failing
        when the last enabled button got disabled while the list refreshed."""
        try:
            self._enabled_pick_button().click(timeout=timeout)
            self.pause(1)
            return True
        except PlaywrightTimeoutError:
            return False

    def filter_pending_tasks(self):
        """Filters reset after each approval, so re-apply Pending every pass."""
        self.click(self.Show_Filters)
        self.pause(1)
        self.click(self.Pending_Filter)
        self.pause(1.5)

    def has_pending_task(self, timeout: int = 30000) -> bool:
        """Non-failing check so the approval loop can stop cleanly
        once the pending queue is empty. A real task row carries a status
        badge; the empty-state row shown when the queue is done does not."""
        try:
            first_row = self.get_locator(self.First_Task_Row).first
            first_row.get_by_role("status").first.wait_for(state="visible", timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            return False

    def is_task_open(self, timeout: int = 30000) -> bool:
        """The task detail is considered open once its Approve button shows."""
        try:
            self.get_locator(self.Approve_Button).wait_for(state="visible", timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            return False

    def select_first_task(self, attempts: int = 3):
        """Open the first available task so the test stays repeatable
        regardless of which tasks are currently in the queue.
        Returns the task name, or None when the detail never opened.

        The list can still be repainting right after the Pending filter is
        (re)applied, so a row/status badge found one instant can detach
        before the click lands. Re-resolving the locator on each attempt
        avoids racing a stale element instead of waiting the full timeout
        on a row that no longer exists."""
        for attempt in range(1, attempts + 1):
            first_row = self.get_locator(self.First_Task_Row).first
            status_badge = first_row.get_by_role("status").first
            try:
                status_badge.wait_for(state="visible", timeout=30000)
            except PlaywrightTimeoutError:
                continue

            task_name = (first_row.text_content() or "").strip()
            try:
                # Clicking the row body does not open the task — the status
                # badge is the reliable click target (matches codegen flow)
                status_badge.click(timeout=30000)
            except PlaywrightTimeoutError:
                continue

            if self.is_task_open():
                self.pause(1.5)
                return task_name

        return None

    def approve_task(self):
        self.click(self.Approve_Button)
        self.pause(1.5)
        # A confirmation dialog re-asks before the approval is submitted
        self.click(self.Approve_Button)
        self.pause(1.5)

    def close_task(self, timeout: int = 30000):
        """Dismiss whichever post-approval dialog the app shows — it is not
        consistent: usually the 'Pick Another Task?' prompt (dismissed with
        Cancel), otherwise the approval summary with its Close cross.
        Either way this lands on the task detail, not back on the list."""
        cancel = self.get_locator(self.Cancel_Task_Prompt)
        try:
            cancel.wait_for(state="visible", timeout=timeout)
            cancel.click()
        except PlaywrightTimeoutError:
            self.click(self.Close_Task)
        self.pause(1.5)

    def go_back_to_task_list(self):
        """The detail view renders inside the active My Tasks tab, so the
        tab link is a no-op there — Go Back is the way to the list."""
        self.click(self.Go_Back)
        self.pause(1.5)

    # Pick Another Task flow is disabled for now — the loop goes back
    # through My Tasks + Pending filter instead.
    # def pick_another_task_visible(self):
    #     self.verify_text_visible(self.Pick_Another_Task)
    #     return True
    #
    # def pick_another_task(self):
    #     self.click(self.Pick_Another_Task)
    #
    # def wait_for_task_loaded(self, timeout: int = 30000) -> bool:
    #     """After Pick Another Task, wait for the next task's Approve button.
    #     Returns False instead of raising when the queue has no more tasks."""
    #     try:
    #         self.get_locator(self.Approve_Button).wait_for(state="visible", timeout=timeout)
    #         return True
    #     except PlaywrightTimeoutError:
    #         return False
