"""Environment-driven test settings.

Keeps the `os.getenv` parsing in one place so every test reads its settings the
same way, and so a typo in a variable fails loudly at collection time instead of
silently falling back to a default.
"""

import os

from utilities.custom_logger import Log_Maker
from utilities.read_properties import ReadAloudCofing

logger = Log_Maker.log_gen(__name__)

# Values that mean "no limit - use every row in the source file"
UNLIMITED_VALUES = ("all", "none", "0")

DEFAULT_ENV = "stage"

# Per-environment backend overrides, mirroring the {DEV,STAGE,PROD}_URL
# variables that select the UI host
API_URL_VARS = {
    "dev": "DEV_API_URL",
    "stage": "STAGE_API_URL",
    "prod": "PROD_API_URL",
}


def get_environment() -> str:
    """The environment under test, as selected by ENV."""
    return os.getenv("ENV", DEFAULT_ENV).strip().lower()


def get_api_base_url() -> str:
    """Resolve the backend API base URL for the environment under test.

    The API host has to follow the UI host: a TTS job created through the prod
    UI is unknown to the stage backend, which shows up as a job_id that polls
    404 until it times out. Resolution mirrors conftest.get_target_url() - an
    explicit API_BASE_URL wins, then the per-environment variable, then the
    matching entry in config.ini.

    Call this at runtime rather than at class-definition time: .env is loaded
    after the page modules are imported, so an import-time read would miss it.
    """
    override = os.getenv("API_BASE_URL", "").strip()
    if override:
        logger.debug(f"API base URL taken from the API_BASE_URL flag: {override}")
        return override

    env_name = get_environment()

    env_url = os.getenv(API_URL_VARS.get(env_name, ""), "").strip()
    if env_url:
        logger.debug(f"API base URL taken from the '{env_name}' environment: {env_url}")
        return env_url

    config_url = ReadAloudCofing.get_api_base_url(env_name)
    logger.debug(f"API base URL for '{env_name}' taken from config.ini: {config_url}")
    return config_url


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
