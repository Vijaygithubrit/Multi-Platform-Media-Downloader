from src.validators import validate_url


def test_valid_https_url():
    valid, error = validate_url("https://example.com")

    assert valid is True
    assert error == ""


def test_valid_http_url():
    valid, error = validate_url("http://example.com")

    assert valid is True
    assert error == ""


def test_empty_url():
    valid, error = validate_url("")

    assert valid is False
    assert error is not None


def test_missing_scheme():
    valid, error = validate_url("example.com")

    assert valid is False
    assert error is not None


def test_unsupported_scheme():
    valid, error = validate_url("ftp://example.com")

    assert valid is False
    assert error is not None