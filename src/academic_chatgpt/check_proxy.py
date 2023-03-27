"""This module contains a function for checking the validity of a proxy server."""
from loguru import logger
import requests


def check_proxy(proxies):
    """Check the validity of a proxy server.

    Args:
    ----
        proxies (dict): A dictionary containing the proxy server information.

    Returns:
    -------
        None
    """
    proxies.get("https")

    try:
        response = requests.get("https://ipapi.co/json/", proxies=proxies, timeout=4)
        response.raise_for_status()
        data = response.json()

        data["country_name"]

    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred: {e}")


if __name__ == "__main__":
    try:
        from config_private import (
            proxies,
        )
    except ModuleNotFoundError:
        from config import proxies

    check_proxy(proxies)
