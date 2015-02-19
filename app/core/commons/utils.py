from datetime import datetime


def utcnow():
    """
    Returns the current (naive) UTC datetime.
    """
    return datetime.utcnow()