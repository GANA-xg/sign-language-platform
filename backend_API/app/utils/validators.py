import re

SCRIPT_TAG_PATTERN = re.compile(r"<\s*script|javascript:|onerror\s*=|onload\s*=", re.IGNORECASE)
SQL_INJECTION_PATTERN = re.compile(
    r"(\bunion\b|\bselect\b|\bdrop\b|\binsert\b|\bdelete\b|--|;|\bor\b\s+1\s*=\s*1)",
    re.IGNORECASE,
)


def sanitize_text_field(value: str, field_name: str = "field", max_length: int = 1000) -> str:
    """Raises ValueError if the input looks malicious or is too long."""
    if value is None:
        return value

    if len(value) > max_length:
        raise ValueError(f"{field_name} exceeds maximum length of {max_length} characters")

    if SCRIPT_TAG_PATTERN.search(value):
        raise ValueError(f"{field_name} contains disallowed script-like content")

    if SQL_INJECTION_PATTERN.search(value):
        raise ValueError(f"{field_name} contains disallowed SQL-like content")

    return value.strip()