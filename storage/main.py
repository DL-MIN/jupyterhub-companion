"""
This module provides the factory function to create new storage instances based on configuration.
It parses environment variables and instantiates the appropriate storage backend.
"""

import os

from .storage import Storage
from .posix import StoragePosix
from .zfs import StorageZFS

backends = {
    "posix": StoragePosix,
    "zfs": StorageZFS
}


def new(base_path: str = os.getenv("STORAGE_BASE_PATH", ""),
        uid: int = int(os.getenv("STORAGE_UID", "1000")),
        gid: int = int(os.getenv("STORAGE_GID", "1000")),
        backend_name: str = os.getenv("STORAGE_BACKEND", "posix").lower()) -> Storage:
    """
    Retrieves the storage backend based on environment variables.

    :param base_path: The base path for storage operations.
                      Defaults to the value of the STORAGE_BASE_PATH environment variable
                      or an empty string if not set.
    :param uid: The user ID for storage operations. Defaults to the integer value
                of the STORAGE_UID environment variable or 1000 if not set.
    :param gid: The group ID for storage operations. defaults to the integer value
                of the STORAGE_GID environment variable or 1000 if not set.
    :param backend_name: The name of the storage backend to use. Defaults to the lowercase value
                         of the STORAGE_BACKEND environment variable or 'posix' if not set.
    :return A new Storage instance configured with the provided parameters.
    :rtype: Storage
    :raises ValueError: If any of the environment variables are invalid.
    """

    if not base_path or base_path.endswith("/"):
        raise ValueError(f"Invalid base path: '{base_path}'. "
                         "Base path must be a non-empty string without trailing slash.")

    if uid <= 0 or gid <= 0:
        raise ValueError(f"Invalid UID/GID pair: '{uid}:{gid}'. Both must be positive integers.")

    backend_class = backends.get(backend_name)
    if backend_class is None:
        raise ValueError(f"Invalid storage backend: '{backend_name}'. "
                         "Supported backends are {list(backends.keys())}.")

    return backend_class(base_path, uid, gid)
