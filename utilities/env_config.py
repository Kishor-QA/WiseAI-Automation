"""Environment-driven test settings.

Keeps the `os.getenv` parsing in one place so every test reads its settings the
same way, and so a typo in a variable fails loudly at collection time instead of
silently falling back to a default.
"""

import os

from utilities.custom_logger import Log_Maker

logger = Log_Maker.log_gen(__name__)

# Values that mean "no limit - use every row in the source file"
UNLIMITED_VALUES = ("all", "none", "0")


def get_row_limit(name: str, default: int | None = None) -> int | None:
    """How many rows of a test-data file to use, read from environment `name`.

    Returns None for "use every row": either because `default` is None and the
    variable is unset, or because it is explicitly set to 'all', 'none' or '0'.

    Raises ValueError on a non-numeric or negative value - a limit that cannot
    be parsed must not quietly turn into a different sized test run.
    """
    raw = os.getenv(name, "").strip()

    if not raw:
        logger.debug(f"{name} not set; using the default row limit of {default or 'all rows'}")
        return default

    if raw.lower() in UNLIMITED_VALUES:
        logger.info(f"{name}={raw}; using every row of the source file")
        return None

    try:
        limit = int(raw)
    except ValueError:
        logger.error(f"{name}='{raw}' is not a number; expected an integer or one of {UNLIMITED_VALUES}")
        raise ValueError(
            f"{name} must be an integer or one of {UNLIMITED_VALUES}, got '{raw}'"
        ) from None

    if limit < 0:
        logger.error(f"{name}={limit} is negative; a row limit cannot be below zero")
        raise ValueError(f"{name} must not be negative, got {limit}")

    logger.info(f"{name}={limit}; limiting the run to {limit} row(s)")
    return limit
