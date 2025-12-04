import time
import requests as r
from typing import Optional, Dict, Any
from .config import OMDB_API_URL, OMDB_API_KEY

__all__ = ("call_omdb_api",)


class OMDBAPIError(Exception):
    """Custom exception for OMDB API errors"""

    pass


def call_omdb_api(
    params: dict, max_retries: int = 3, retry_delay: float = 1.0
) -> Optional[Dict[str, Any]]:
    """
    Call OMDB API with error handling and retry logic.

    Args:
        params: Dictionary of query parameters for OMDB API
        max_retries: Maximum number of retry attempts for rate limiting
        retry_delay: Delay in seconds between retries

    Returns:
        JSON response from OMDB API or None if request failed

    Raises:
        OMDBAPIError: If API returns an error or request fails after retries
    """
    if not OMDB_API_KEY:
        raise OMDBAPIError(
            "OMDB API key is not configured. Please set OMDB_API_KEY in .env file"
        )

    _params = {"apikey": OMDB_API_KEY, **params}

    for attempt in range(max_retries):
        try:
            response = r.get(OMDB_API_URL, params=_params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Check if OMDB API returned an error
            if data.get("Response") == "False":
                error_message = data.get("Error", "Unknown error")

                # Handle specific error cases
                if "limit" in error_message.lower() or "quota" in error_message.lower():
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay * (attempt + 1))
                        continue
                    raise OMDBAPIError(f"Rate limit exceeded: {error_message}")

                if "not found" in error_message.lower():
                    return None

                raise OMDBAPIError(f"OMDB API error: {error_message}")

            return data

        except r.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            raise OMDBAPIError("Request timeout: OMDB API did not respond in time")

        except r.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            raise OMDBAPIError(f"Network error: {str(e)}")

    raise OMDBAPIError("Failed to connect to OMDB API after multiple retries")
