"""
JupyterHub Companion API

This module defines the FastAPI application for managing storages in a JupyterHub environment.
It includes endpoints for users, groups, and storages.
The application uses dependency injection for authentication and interacts
with a storage backend through the `storage` module.

Endpoints:
    Users: Create, retrieve, and delete users with associated disk quotas.
    Groups: Create, retrieve, and delete groups with associated disk quotas.
    Storages: List all available storage directories with their quotas and usage.
"""

from fastapi import APIRouter, Depends, FastAPI, status

import storage
from auth import api_auth
from models import Group, User

storage = storage.new()
app = FastAPI(root_path="/api/v1",
              title="JupyterHub Companion",
              description="This is a utility service designed to manage"
                          "storage backends for JupyterHub environments.",
              version="1.0.0")
api_v1 = APIRouter(dependencies=[Depends(api_auth)])
api_v1_users = APIRouter(prefix="/users")
api_v1_groups = APIRouter(prefix="/groups")
api_v1_storages = APIRouter(prefix="/storages")


@api_v1_users.get("/{name}",
                  response_model=User,
                  summary="Get user details",
                  description="Retrieve details of a specific user by name.")
async def get_user(name: str) -> User:
    """
    Retrieve details of a specific user by name.

    :param name: The name of the user to retrieve.
    :return: An object containing the user's details including quota and disk usage.
    :rtype: User
    """

    quota, used = storage.get_dir(name)
    return User(
        name=name,
        quota=quota,
        disk_usage=used
    )


@api_v1_users.post("/",
                   status_code=status.HTTP_204_NO_CONTENT,
                   summary="Create a new user",
                   description="Create a new user with specified details.")
async def create_user(user: User):
    """
    Create a new user with specified details.

    :param user: The user object containing the name and quota.
    :type user: User
    """

    storage.create_dir(user.name, quota=user.quota)


@api_v1_users.delete("/{name}",
                     status_code=status.HTTP_204_NO_CONTENT,
                     summary="Delete a user",
                     description="Delete an existing user by name.")
async def delete_user(name: str):
    """
    Delete an existing user by name.

    :param name: The name of the user to delete.
    """

    storage.delete_dir(name)


@api_v1_groups.get("/{name}",
                   response_model=Group,
                   summary="Get group details",
                   description="Retrieve details of a specific group by name.")
async def get_group(name: str) -> Group:
    """
    Retrieve details of a specific group by name.

    :param name: The name of the group to retrieve.
    :return: An object containing the group's details including quota and disk usage.
    :rtype: Group
    """

    quota, used = storage.get_dir("groups", name)
    return Group(
        name=name,
        quota=quota,
        disk_usage=used
    )


@api_v1_groups.post("/",
                    status_code=status.HTTP_204_NO_CONTENT,
                    summary="Create a new group",
                    description="Create a new group with specified details.")
async def create_group(group: Group):
    """
    Create a new group with specified details.

    :param group: The group object containing the name and quota.
    :type group: Group
    """

    storage.create_dir("groups", group.name, quota=group.quota)


@api_v1_groups.delete("/{name}",
                      status_code=status.HTTP_204_NO_CONTENT,
                      summary="Delete a group",
                      description="Delete an existing group by name.")
async def delete_group(name: str):
    """
    Delete an existing group by name.

    :param name: The name of the group to delete.
    """

    storage.delete_dir(name)


@api_v1_storages.get("/",
                     response_model=list[tuple[str, int, int]],
                     summary="List all storages",
                     description="Retrieve a list of all available storages.")
async def list_storages():
    """
    List all available storage directories with their quotas and usage.

    :return: A list of tuples containing the directory name, quota, and usage.
    :rtype: list[tuple[str, int, int]]
    """

    return storage.list_dir()


api_v1.include_router(api_v1_users, tags=["Users"])
api_v1.include_router(api_v1_groups, tags=["Groups"])
api_v1.include_router(api_v1_storages, tags=["Storages"])
app.include_router(api_v1)
