"""
This module defines an abstract base class `Storage` for managing storage directories.
It includes methods to create, delete, and retrieve information about directories,
as well as listing all directories with their quota and used space. The class ensures
that directory paths only contain allowed characters.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from fastapi import HTTPException, status

allowed_path_chars = set(
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789"
    "-_"
    "àáâäæãåāçćčèéêëēėęîïíīįìłñńôöòóœøōõßśšûüùúūÿžźż"
    "ÀÁÂÄÆÃÅĀÇĆČÈÉÊËĒĖĘÎÏÍĪĮÌŁÑŃÔÖÒÓŒØŌÕŚŠÛÜÙÚŪŸŽŹŻ"
)


@dataclass
class Storage(ABC):
    """
    Abstract base class for managing storage directories.

    It provides a template for creating, deleting, and retrieving information about storages.
    It also includes functionality to list all directories with their quota and used space.
    The class ensures that directory paths only contain allowed characters.
    """

    base_path: str
    uid: int
    gid: int

    @abstractmethod
    def create_dir(self, *path: str, quota: int = 0) -> None:
        """
        Create a directory with optional quota and path.

        :param quota: Optional quota value.
        :param path: Path components to create the directory.
        """

        self._check_paths(*path)

    @abstractmethod
    def delete_dir(self, *path: str) -> None:
        """
        Delete a directory at the specified path.

        :param path: Path components to delete the directory.
        """

        self._check_paths(*path)

    @abstractmethod
    def get_dir(self, *path: str) -> tuple[int, int]:
        """
        Retrieve information about the directory with the specified path.

        :param path: Path components to get the directory.
        :return: Quota and used space.
        :rtype: tuple[int, int]
        """

        self._check_paths(*path)
        return 0, 0

    @abstractmethod
    def list_dir(self) -> list[tuple[str, int, int]]:
        """
        List directories and their quota and current use.

        :return: List of tuples containing directory name, quota, and used space.
        :rtype: list[tuple[str, int, int]]
        """


    @staticmethod
    def _check_path(path: str) -> bool:
        """
        Check if the path contains only allowed characters.

        :param path: Path components to check.
        :return: True if the path contains only allowed characters.
        :rtype: bool
        """

        return set(path).issubset(allowed_path_chars)

    @staticmethod
    def _check_paths(*path: str) -> None:
        """
        Validate multiple paths for allowed characters

        :param path: Path components to check.
        :raises HTTPException: If any path contains forbidden characters.
        """

        for p in path:
            if not Storage._check_path(p):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Path '{p}' contains forbidden characters",
                )
