"""This module contains a function for checking the validity of a proxy server."""
import requests
from loguru import logger


def check_proxy(proxies):
    """Check the validity of a proxy server.

    Args:
    ----
        proxies (dict): A dictionary containing the proxy server information.

    Returns:
    -------
        None
    """

    proxies_https = None if proxies is None else proxies.get("https")

    try:
        response = requests.get("https://ipapi.co/json/", proxies=proxies, timeout=4)
        response.raise_for_status()
        data = response.json()
        if "country_name" in data:
            country = data["country_name"]
            logger.info(f"Proxy server {proxies_https} is located in {country}")
        elif "error" in data:
            logger.warn(
                f"Proxy configuration {proxies_https}, Proxy location: unknown, IP query frequency limited"
            )
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred: {e}")
