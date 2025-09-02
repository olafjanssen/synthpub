"""
Utility functions for handling rate limit errors in LLM calls.
"""

import re
import time
from functools import wraps
from typing import Callable


class RateLimitError(Exception):
    """Custom exception for rate limit errors that should stop the publishing chain."""

    def __init__(
        self, message: str, retry_after: int = 60, original_exception: Exception = None
    ):
        super().__init__(message)
        self.retry_after = retry_after
        self.original_exception = original_exception


def is_rate_limit_error(exception: Exception) -> bool:
    """
    Check if an exception is a rate limit error.

    Args:
        exception: The exception to check

    Returns:
        True if the exception is a rate limit error, False otherwise
    """
    # Check exception type name
    exception_name = type(exception).__name__.lower()
    if any(
        keyword in exception_name
        for keyword in ["ratelimit", "rate_limit", "toomanyrequests"]
    ):
        return True

    # Check exception message for rate limit indicators
    error_message = str(exception).lower()
    rate_limit_indicators = [
        "rate limit",
        "rate_limit",
        "too many requests",
        "quota exceeded",
        "requests per minute",
        "requests per second",
        "429",
        "ratelimit",
        "throttle",
        "throttled",
    ]

    return any(indicator in error_message for indicator in rate_limit_indicators)


def is_retryable_error(exception: Exception) -> bool:
    """
    Check if an exception is retryable (rate limit or temporary errors).

    Args:
        exception: The exception to check

    Returns:
        True if the exception is retryable, False otherwise
    """
    if is_rate_limit_error(exception):
        return True

    # Check for other retryable errors
    error_message = str(exception).lower()
    retryable_indicators = [
        "timeout",
        "connection",
        "network",
        "temporary",
        "service unavailable",
        "503",
        "502",
        "504",
    ]

    return any(indicator in error_message for indicator in retryable_indicators)


def extract_retry_after_seconds(exception: Exception) -> int:
    """
    Extract retry-after seconds from rate limit error message.

    Args:
        exception: The rate limit exception

    Returns:
        Number of seconds to wait before retry, default 60 if not found
    """
    error_message = str(exception)

    # Look for retry-after header value
    retry_after_match = re.search(
        r"retry[_-]?after[:\s]*(\d+)", error_message, re.IGNORECASE
    )
    if retry_after_match:
        return int(retry_after_match.group(1))

    # Look for "wait X seconds" patterns
    wait_match = re.search(
        r"wait[:\s]*(\d+)[:\s]*seconds?", error_message, re.IGNORECASE
    )
    if wait_match:
        return int(wait_match.group(1))

    # Look for "try again in X seconds" patterns
    try_again_match = re.search(
        r"try[:\s]*again[:\s]*in[:\s]*(\d+)[:\s]*seconds?", error_message, re.IGNORECASE
    )
    if try_again_match:
        return int(try_again_match.group(1))

    # Default retry delay
    return 60


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
):
    """
    Decorator to retry functions with exponential backoff on rate limit errors.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds for the first retry
        max_delay: Maximum delay in seconds between retries
        exponential_base: Base for exponential backoff calculation
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    # Only retry on rate limit or retryable errors
                    if not is_retryable_error(e):
                        raise e

                    # Don't retry on the last attempt
                    if attempt == max_retries:
                        break

                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (exponential_base**attempt), max_delay)

                    # If it's a rate limit error, try to extract retry-after time
                    if is_rate_limit_error(e):
                        retry_after = extract_retry_after_seconds(e)
                        delay = max(delay, retry_after)

                    print(
                        f"Rate limit error in {func.__name__}, retrying in {delay:.1f} seconds (attempt {attempt + 1}/{max_retries + 1})"
                    )
                    time.sleep(delay)

            # If we get here, all retries failed
            raise last_exception

        return wrapper

    return decorator
