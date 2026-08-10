import re
from difflib import SequenceMatcher

from utilities.custom_logger import Log_Maker

logger = Log_Maker.log_gen(__name__)


def normalize_text(text: str) -> str:
    """Collapse whitespace and lowercase so cosmetic differences
    (extra spaces, line breaks, casing) don't affect comparison."""
    return re.sub(r"\s+", " ", (text or "").strip()).casefold()


def similarity_ratio(expected: str, actual: str) -> float:
    """Similarity between two texts from 0.0 (nothing in common)
    to 1.0 (identical after normalization)."""
    ratio = SequenceMatcher(None, normalize_text(expected), normalize_text(actual)).ratio()
    logger.debug(
        f"Similarity {ratio:.3f} between expected ({len(expected or '')} chars) "
        f"and actual ({len(actual or '')} chars)"
    )
    return ratio
