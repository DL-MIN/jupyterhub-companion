"""
Utility functions for running commands and caching results.
"""

import subprocess
import time
from functools import wraps

from .logger import logger


def run_cmd(args: list[str], check_rc: bool = False, timeout: int = 60) -> tuple[int, str, str]:
    """
    Runs a command with the given arguments and returns the return code and output.

    :param args: List of command line arguments to execute.
    :param check_rc: If True, raises an exception if the return code is non-zero.
    :param timeout: Timeout duration for the subprocess execution.
    :return: Tuple containing the return code, standard output, and standard error of the command.
    :rtype: (int, str, str)
    :raises subprocess.CalledProcessError: If check_rc is True and the return code is non-zero.
    :raises subprocess.TimeoutExpired: If timeout expired.
    :raises Exception: For any other errors during subprocess execution.
    """

    try:
        logger.debug("Running command %s", args)
        process = subprocess.run(args,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True,
                                 check=check_rc,
                                 timeout=timeout)
        return process.returncode, process.stdout, process.stderr
    except subprocess.CalledProcessError as e:
        logger.error("Command %s failed with return code %d: %s", args, e.returncode, e.stderr)
        raise e
    except subprocess.TimeoutExpired as e:
        logger.error("Command %s timed out after %d seconds", args, timeout)
        raise e
    except Exception as e:
        logger.error("An error occurred while executing command %s: %s", args, e)
        raise e


def ttl_cache(seconds: int):
    """
    Decorator to cache function results with a TTL (Time To Live).

    :param seconds: Time in seconds for which the cache is valid.
    """

    def decorator(func):
        cache = {}

        @wraps(func)
        def wrapper(*args, **kwargs):
            key = args + tuple(kwargs.items())
            current_time = time.time()

            if key in cache:
                cached_time, result = cache[key]
                if current_time - cached_time < seconds:
                    return result

            result = func(*args, **kwargs)
            cache[key] = (current_time, result)
            return result

        return wrapper

    return decorator
