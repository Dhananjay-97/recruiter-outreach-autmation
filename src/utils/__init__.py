# This file is intentionally left blank.
import logging
import os
import time

from dotenv import load_dotenv


class ConfigLoader:
    """
    ConfigLoader is a utility class for loading environment variables from a .env file.
    Attributes:
        dotenv_path (str): Path to the .env file. Defaults to ".env".
    Methods:
        get(key, default=None):
            Retrieves the value of the specified environment variable.
            Args:
                key (str): The name of the environment variable.
                default (Any, optional): The default value to return if the variable is not found. Defaults to None.
            Returns:
                str or Any: The value of the environment variable, or the default value if not found.
    """
    def __init__(self, dotenv_path=".env"):
        load_dotenv(dotenv_path)

    def get(self, key, default=None):
        """
        Retrieve the value of an environment variable.

        Args:
            key (str): The name of the environment variable to retrieve.
            default (Any, optional): The value to return if the environment variable is not set. Defaults to None.

        Returns:
            Any: The value of the environment variable if set, otherwise the default value.
        """
        return os.getenv(key, default)

class Logger:
    def __init__(self, name=__name__, level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        # Add handler to print to console
        ch = logging.StreamHandler()
        ch.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

class RateLimiter:
    def __init__(self, calls_per_period, period):
        self.calls_per_period = calls_per_period
        self.period = period
        self.timestamps = []

    def wait(self):
        now = time.time()
        self.timestamps = [t for t in self.timestamps if t > now - self.period]
        if len(self.timestamps) >= self.calls_per_period:
            sleep_time = self.period - (now - self.timestamps[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
        self.timestamps.append(time.time())