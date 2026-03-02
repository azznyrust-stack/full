from functools import lru_cache

import easyocr


@lru_cache(maxsize=1)
def get_easyocr_reader():
    """Create a single EasyOCR reader instance for low-latency frame processing."""
    return easyocr.Reader(["de", "en"], gpu=False, verbose=False)
