"""
This module initializes the storage components for the jupyterhub-companion project.
It provides various storage implementations and a factory function to create new storage instances.

Classes:
    - Storage: An abstract base class for storage implementations.
    - StoragePosix: A concrete implementation of Storage using POSIX file system.
    - StorageZFS: A concrete implementation of Storage using ZFS file system.

Functions:
    - new: A factory function to create new storage instances based on configuration.
"""

from .storage import Storage
from .main import new
from .posix import StoragePosix
from .zfs import StorageZFS

__all__ = ["new", "Storage", "StoragePosix", "StorageZFS"]
