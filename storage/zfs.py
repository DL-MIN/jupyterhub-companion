"""
ZFS-based storage implementation.
"""

import os
from dataclasses import dataclass
from threading import Semaphore

from fastapi import HTTPException, status

from .storage import Storage
from .logger import logger
from .utils import run_cmd


def _exists(path: str) -> bool:
    """
    Check if a ZFS dataset exists.

    :param path: Path to the ZFS dataset.
    :return: True if the dataset exists.
    :rtype: bool
    """

    return run_cmd(["zfs", "list", "-t", "all", path])[0] == 0


def _create(path: str) -> None:
    """
    Create a new ZFS dataset.

    :param path: Path to the ZFS dataset.
    """

    run_cmd(["zfs", "create", path], True)


def _destroy(path: str) -> None:
    """
    Recursively destroy a ZFS dataset.

    :param path: Path to the ZFS dataset.
    """

    run_cmd(["zfs", "destroy", "-R", path], True)


def _set_quota(path: str, quota: int) -> None:
    """
    Set the quota for a ZFS dataset.

    :param path: Path to the ZFS dataset.
    :param quota: Quota in bytes to set.
    """

    run_cmd(["zfs", "set", f"quota={quota}", path], True)


def _list(path: str) -> str:
    """
    List details of a ZFS dataset including name, quota, and used space.

    :param path: Path to the ZFS dataset.
    """

    return run_cmd(["zfs", "list", "-Hpro", "name,quota,used", path], True)[1]


@dataclass
class StorageZFS(Storage):
    """
    ZFS-based storage implementation.

    This class provides methods to create, delete, and retrieve information about datasets
    in a file system. It also lists the contents of the base dataset with their disk usage.
    """

    disk_usage_sema: Semaphore = Semaphore()

    def __post_init__(self):
        if not _exists(self.base_path):
            raise NotADirectoryError(f"{self.base_path} is not a directory")

    def create_dir(self, *path: str, quota: int = 0) -> None:
        """
        Create a new dataset with the specified path.

        :param quota: Optional quota value.
        :param path: Path components to create the dataset.
        """

        super().create_dir(*path, quota=quota)
        abs_path = os.path.join(self.base_path, *path)

        logger.info("Creating storage at %s", abs_path)
        if not _exists(abs_path):
            _create(abs_path)
        if quota > 0:
            logger.info("Setting quota at %s to %d", abs_path, quota)
            _set_quota(abs_path, quota)

    def delete_dir(self, *path: str) -> None:
        """
        Delete a dataset at the specified path.

        :param path: Path components to delete the dataset.
        :raises HTTPException: If the dataset is not found.
        """

        super().delete_dir(*path)
        abs_path = os.path.join(self.base_path, *path)

        logger.info("Deleting storage at %s", abs_path)
        if not _exists(abs_path):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        _destroy(abs_path)

    def get_dir(self, *path: str) -> tuple[int, int]:
        """
        Retrieve information about the dataset with the specified path.

        :param path: Path components to get the dataset.
        :return: Quota and used space.
        :rtype: tuple[int, int]
        :raises HTTPException: If the dataset is not found.
        """

        super().get_dir(*path)
        abs_path = os.path.join(self.base_path, *path)

        logger.info("Retrieve information about the storage at %s", abs_path)
        if not _exists(abs_path):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        _, quota, used = self._get_disk_usage(*path)[-1]
        return quota, used

    def list_dir(self) -> list[tuple[str, int, int]]:
        """
        List datasets and their quota and used space.

        :return: List of tuples containing dataset name, quota, and used space.
        :rtype: list[tuple[str, int, int]]
        """

        return self._get_disk_usage()[1:]

    def _get_disk_usage(self, path: str = "") -> list[tuple[str, int, int]]:
        """
        Retrieve disk usage for the specified path or all datasets if no path is provided.

        :param path: Path to retrieve disk usage for.
        :return: A list of tuples containing dataset name, quota, and used space.
        :rtype: list[tuple[str, int, int]]
        """

        line = _list(os.path.join(self.base_path, path).rstrip("/"))
        lines = line.strip().split("\n")
        return [(os.path.basename(parts[0]), int(parts[1]), int(parts[2])) for line in lines if
                len((parts := line.split("\t"))) == 3]
