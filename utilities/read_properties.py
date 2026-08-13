import configparser
import csv
import os

from utilities.custom_logger import Log_Maker

logger = Log_Maker.log_gen(__name__)

CONFIG_PATH = "./config/config.ini"

config = configparser.ConfigParser()
_loaded = config.read(CONFIG_PATH)

if _loaded:
    logger.debug(f"Loaded configuration from {CONFIG_PATH}: sections={config.sections()}")
else:
    # Every page object reads its locators at import time, so a missing config
    # file must be obvious here instead of surfacing as NoSectionError later
    logger.error(f"Configuration file not found at {CONFIG_PATH} (cwd={os.getcwd()})")

# Locator prefixes BasePage.get_locator() knows how to resolve
SUPPORTED_LOCATOR_TYPES = (
    "role", "role_exact", "role_nth", "link", "locator", "text", "css", "placeholder",
)

# These carry a second value after the type: the role plus its name or index
_TWO_VALUE_TYPES = ("role", "role_exact", "role_nth")


def _parse_locator(section, name):
    """Read one locator from config.ini and split it into the tuple BasePage expects.

    Shared by every config class - the parsing rules are identical, only the
    section differs, so the logging and error handling live here once.
    """
    try:
        raw = config.get(section, name)
    except (configparser.NoSectionError, configparser.NoOptionError) as error:
        logger.error(f"Locator '{name}' is missing from section [{section}] in {CONFIG_PATH}: {error}")
        raise

    parts = [part.strip() for part in raw.split(',')]
    locator_type = parts[0]

    if locator_type not in SUPPORTED_LOCATOR_TYPES:
        # Previously this fell through and returned None, which surfaced much
        # later as "NoneType has no attribute click" on an unrelated line
        logger.error(
            f"Locator '{name}' in section [{section}] uses unsupported type "
            f"'{locator_type}'; expected one of {SUPPORTED_LOCATOR_TYPES}"
        )
        raise ValueError(f"Unsupported locator type '{locator_type}' for '{name}' in [{section}]")

    if locator_type in _TWO_VALUE_TYPES and len(parts) >= 3:
        parsed = (locator_type, parts[1], parts[2])
    else:
        parsed = (locator_type, parts[1])

    logger.trace(f"Resolved locator [{section}] {name} -> {parsed}")
    return parsed


def _read_page_url(section, key):
    """Read a URL from config.ini, logging which one was used."""
    try:
        url = config.get(section, key)
    except (configparser.NoSectionError, configparser.NoOptionError) as error:
        logger.error(f"URL '{key}' is missing from section [{section}] in {CONFIG_PATH}: {error}")
        raise

    logger.trace(f"Resolved URL [{section}] {key} -> {url}")
    return url


class ReadConfig:

    SECTION = "login info"

    @staticmethod
    def get_page_url():
        return _read_page_url(ReadConfig.SECTION, "Page_URL")

    @staticmethod
    def get_locator(name):
        return _parse_locator(ReadConfig.SECTION, name)

    @staticmethod
    def get_test_data(csv_file):
        path = f"./test_data/{csv_file}"
        logger.info(f"Reading test data from {path}")

        data = []
        try:
            with open(path, mode='r') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    data.append(row)
        except OSError as error:
            logger.error(f"Could not read test data file {path}: {error}")
            raise

        logger.info(f"Loaded {len(data)} row(s) of test data from {path}")
        return data


class ReadAloudCofing:

    SECTION = "Read Aloud"

    @staticmethod
    def get_page_url(key="Page_URL"):
        return _read_page_url(ReadAloudCofing.SECTION, key)

    @staticmethod
    def get_api_base_url(env_name):
        """Backend URL configured for `env_name` (dev, stage, prod).

        Falls back to the plain Base_URL when an environment has no entry of
        its own, so an unrecognised ENV still resolves to something.
        """
        key = f"{env_name}_Base_URL"
        if config.has_option(ReadAloudCofing.SECTION, key):
            return _read_page_url(ReadAloudCofing.SECTION, key)

        logger.warning(
            f"No '{key}' in section [{ReadAloudCofing.SECTION}] of {CONFIG_PATH}; "
            f"falling back to Base_URL"
        )
        return _read_page_url(ReadAloudCofing.SECTION, "Base_URL")

    @staticmethod
    def get_locator(name):
        return _parse_locator(ReadAloudCofing.SECTION, name)


class UserManagamentConfig:

    SECTION = "User Management"

    @staticmethod
    def get_page_url(key="Page_URL"):
        return _read_page_url(UserManagamentConfig.SECTION, key)

    @staticmethod
    def get_locator(name):
        return _parse_locator(UserManagamentConfig.SECTION, name)


class STTNepaliReviewConfig:

    SECTION = "STT Nepali Review"

    @staticmethod
    def get_page_url(key="Page_URL"):
        return _read_page_url(STTNepaliReviewConfig.SECTION, key)

    @staticmethod
    def get_locator(name):
        return _parse_locator(STTNepaliReviewConfig.SECTION, name)


class ChatbotConfig:

    SECTION = "Chatbot"

    @staticmethod
    def get_page_url(key="Page_URL"):
        return _read_page_url(ChatbotConfig.SECTION, key)

    @staticmethod
    def get_locator(name):
        return _parse_locator(ChatbotConfig.SECTION, name)
