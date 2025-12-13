# Text related util functions goes here

# Text sanitizer function
def sanitize_text(text: str) -> str:
    allowed_symbols = set(" .,!?-_:;@#()[]{}")

    # Remove non-printable characters
    clean_text = "".join(ch for ch in text if ch.isprintable())

    # Keep only alphanumeric characters and allowed symbols
    clean_text = "".join(ch for ch in clean_text if ch.isalnum() or ch in allowed_symbols)

    return clean_text.strip()


# Text truncate function
def truncate_text(text: str, max_length: int) -> str:
    # Truncate text to a maximum length.
    return text[:max_length]
