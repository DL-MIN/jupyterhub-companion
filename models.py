"""
This module defines Pydantic models for representing users and groups,
including their basic information and resource usage tracking.
"""

from pydantic import BaseModel


class User(BaseModel):
    """
    User model representing a user with basic information and resource usage tracking.

    Attributes:
        name (str): The name of the user.
        quota (int): The storage quota allocated to the user. Defaults to 0.
        disk_usage (int): The current disk usage by the user. Defaults to 0.
    """

    name: str
    quota: int = 0
    disk_usage: int = 0


class Group(BaseModel):
    """
    Group model representing a group with group-level quotas and resources.

    Attributes:
        name (str): The name of the group.
        quota (int): The storage quota allocated to the group. Defaults to 0.
        disk_usage (int): The current disk usage by the group. Defaults to 0.
    """

    name: str
    quota: int = 0
    disk_usage: int = 0
