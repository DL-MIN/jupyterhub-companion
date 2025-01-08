"""
POSIX-based storage implementation.
"""

import glob
import os
import shutil
from dataclasses import dataclass

from fastapi import HTTPException, status

from .storage import Storage
from .logger import logger
from .utils import run_cmd, ttl_cache


@dataclass
class StoragePosix(Storage):
    """
    POSIX-based storage implementation.

    This class provides methods to create, delete, and retrieve information about directories
    in a file system. It also lists the contents of the base directory with their disk usage.
    """

    def __post_init__(self):
        """
        Initialize the StoragePosix instance.

        Checks if the base path is a valid directory and raises an exception if not.

        :raises NotADirectoryError: If the base path is not a directory.
        """

        if not os.path.isdir(self.base_path):
            raise NotADirectoryError(f"{self.base_path} is not a directory")

    def create_dir(self, *path: str, quota: int = 0) -> None:
        """
        Create a new directory with the specified path.

        :param quota: Optional quota value (not used in this implementation).
        :param path: Path components to create the directory.
        :raises OSError: If the directory creation fails.
        """

        super().create_dir(*path, quota=quota)
        abs_path = os.path.join(self.base_path, *path)

        try:
            logger.info("Creating storage at %s", abs_path)
            os.makedirs(abs_path, mode=0o770, exist_ok=True)
            os.chown(abs_path, self.uid, self.gid)
        except OSError as e:
            logger.error("Failed to create storage at %s: %s", abs_path, e)
            raise

    def delete_dir(self, *path: str) -> None:
        """
        Delete a directory at the specified path.

        :param path: Path components to delete the directory.
        :raises HTTPException: If the directory is not found or deletion fails.
        :raises Exception: For any other errors during directory deletion.
        """

        super().delete_dir(*path)
        abs_path = os.path.join(self.base_path, *path)

        try:
            logger.info("Deleting storage at %s", abs_path)
            shutil.rmtree(abs_path)
        except FileNotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e
        except PermissionError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN) from e
        except Exception as e:
            logger.error("Failed to delete directory %s: %s", abs_path, e)
            raise

    def get_dir(self, *path: str) -> tuple[int, int]:
        """
        Retrieve information about the directory with the specified path.

        :param path: Path components to get the directory.
        :return: Quota and used space.
        :rtype: tuple[int, int]
        :raises HTTPException: If the directory is not found.
        :raises Exception: For any other errors during retrieval.
        """

        super().get_dir(*path)
        abs_path = os.path.join(self.base_path, *path)

        logger.info("Retrieve information about the storage at %s", abs_path)
        if not os.path.isdir(abs_path):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        try:
            _, quota, used = self._get_disk_usage(*path)[-1]
            return quota, used
        except Exception as e:
            logger.error("Failed to retrieve disk usage for directory %s: %s", abs_path, e)
            raise

    def list_dir(self) -> list[tuple[str, int, int]]:
        """
        List directories and their quota and used space.

        :return: List of tuples containing directory name, quota, and used space.
        :rtype: list[tuple[str, int, int]]
        """

        return self._get_disk_usage()

    @ttl_cache(60)
    def _get_disk_usage(self, path: str = "") -> list[tuple[str, int, int]]:
        """
        Retrieve disk usage for the specified path or all directories if no path is provided.

        :param path: Path to retrieve disk usage for.
        :return: A list of tuples containing directory name, quota (always 0), and used space.
        :rtype: list[tuple[str, int, int]]
        :raises HTTPException: If acquiring the semaphore times out.
        """

        disk_usage_paths = [os.path.join(self.base_path, path)]
        if not path:
            disk_usage_paths = glob.glob(os.path.join(self.base_path, "*"))

        _, stdout, _ = run_cmd(["du", "-sb"] + disk_usage_paths, True)
        lines = stdout.strip().split("\n")
        return [(os.path.basename(parts[1]), 0, int(parts[0])) for line in lines if
                len((parts := line.split())) == 2]
