from urllib.parse import urlparse


def validate_url(url: str) -> tuple[bool, str]:
    """
    Validate whether the supplied text looks like a usable HTTP/HTTPS URL.

    Returns:
        (True, "") if valid
        (False, error_message) if invalid
    """

    if not url:
        return False, "URL cannot be empty."

    url = url.strip()

    if not url:
        return False, "URL cannot be empty."

    if len(url) > 4096:
        return False, "URL is too long."

    parsed = urlparse(url)

    if parsed.scheme.lower() not in {"http", "https"}:
        return False, "Only HTTP and HTTPS URLs are supported."

    if not parsed.netloc:
        return False, "The URL is missing a domain name."

    return True, ""