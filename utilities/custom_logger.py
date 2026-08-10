"""Framework-wide logging.

A single "Wiseyak" logger tree writes to logs/wiseyak.log. Every module takes a
child logger so each line names where it came from. Records deliberately
propagate to the root logger: that is how pytest captures them into the
"Captured log" section of the HTML report and into the Allure attachment of the
failing test.

Levels used across the framework:

    TRACE    locator resolution and other per-element noise - off by default
    DEBUG    single UI interactions (click, fill, wait) and raw API payloads
    INFO     business actions and API calls (login, navigation, request/status)
    WARNING  recoverable problems - a retry, a fallback path, a slow response
    ERROR    failures, always logged just before the exception is raised

Set the level with LOG_LEVEL in .env (TRACE, DEBUG, INFO, WARNING, ERROR).
Credentials, tokens and other secrets are never logged - log the username, the
token length, never the value.
"""

import logging
import os

# Finer than DEBUG: logging every locator lookup is useful when a selector
# breaks, but far too noisy to keep on for a normal run
TRACE = 5

LOGGER_NAME = "Wiseyak"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_LEVEL = "INFO"


def _trace(self, message, *args, **kwargs):
    """logger.trace(...) - the TRACE counterpart of logger.debug()."""
    if self.isEnabledFor(TRACE):
        self._log(TRACE, message, args, **kwargs)


logging.addLevelName(TRACE, "TRACE")
logging.Logger.trace = _trace


def _configured_level():
    """Resolve LOG_LEVEL, falling back to INFO for an unset or unknown value."""
    level = logging.getLevelName(os.getenv("LOG_LEVEL", DEFAULT_LEVEL).strip().upper())
    return level if isinstance(level, int) else logging.INFO


class Log_Maker:
    @staticmethod
    def log_gen(name=None):
        """Return the framework logger, or a named child of it.

        Modules pass __name__ so their lines are attributable; the no-argument
        form is kept for the callers that already use it.
        """
        logger = logging.getLogger(LOGGER_NAME)

        if not logger.handlers:
            logs_dir = os.path.join(os.getcwd(), "logs")
            os.makedirs(logs_dir, exist_ok=True)

            file_handler = logging.FileHandler(
                os.path.join(logs_dir, "wiseyak.log"),
                mode='a',
                encoding='utf-8'
            )
            formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        logger.setLevel(_configured_level())

        return logger if name is None else logger.getChild(name)


def mask_secret(value):
    """Render a secret safe to log: its length only, never its characters."""
    if not value:
        return "<empty>"
    return f"<{len(str(value))} chars>"
