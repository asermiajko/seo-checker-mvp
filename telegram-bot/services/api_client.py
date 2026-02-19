"""API client for backend communication."""

import logging
from typing import Any
import httpx

logger = logging.getLogger(__name__)


class APIClient:
    """Client for communicating with SEO Checker backend API."""

    def __init__(self, api_url: str, timeout: float = 150.0):
        """Initialize API client.

        Args:
            api_url: Base URL of the backend API (e.g., http://localhost:8000)
            timeout: Request timeout in seconds (default: 150s for long checks)
        """
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout

    async def check_site(self, site_url: str, telegram_id: int, session_id: str | None = None) -> dict[str, Any]:
        """Call backend API to check site SEO.

        Args:
            site_url: URL of the site to check
            telegram_id: Telegram user ID for rate limiting
            session_id: Optional session ID from web form

        Returns:
            dict: API response with report data or error information
        """
        endpoint = f"{self.api_url}/api/check"
        payload = {
            "site_url": site_url,
            "telegram_id": telegram_id,
        }
        
        if session_id:
            payload["session_id"] = session_id

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(endpoint, json=payload)

                if response.status_code == 200:
                    return response.json()

                elif response.status_code == 429:
                    error_data = response.json().get("error", {})
                    return {"error": error_data}

                elif response.status_code == 422:
                    return {
                        "error": {
                            "code": "validation_error",
                            "message": "Некорректный URL. Проверьте адрес сайта.",
                        }
                    }

                elif response.status_code >= 500:
                    return {
                        "error": {
                            "code": "server_error",
                            "message": "Ошибка сервера. Попробуйте позже.",
                        }
                    }

                else:
                    logger.warning(f"Unexpected status code: {response.status_code}")
                    return {
                        "error": {
                            "code": "unknown_error",
                            "message": "Произошла ошибка. Попробуйте позже.",
                        }
                    }

        except httpx.TimeoutException:
            logger.error(f"API timeout for site: {site_url}")
            return {
                "error": {
                    "code": "timeout",
                    "message": (
                        "Проверка заняла слишком много времени. "
                        "Попробуйте позже или проверьте доступность сайта."
                    ),
                }
            }

        except httpx.ConnectError as e:
            logger.error(f"API connection error: {e}")
            return {
                "error": {
                    "code": "connection_error",
                    "message": "Не удалось связаться с сервером. Попробуйте позже.",
                }
            }

        except Exception as e:
            logger.error(f"Unexpected API error: {e}", exc_info=True)
            return {
                "error": {
                    "code": "unknown_error",
                    "message": "Произошла непредвиденная ошибка. Попробуйте позже.",
                }
            }
