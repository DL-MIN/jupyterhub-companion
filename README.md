# JupyterHub Companion

The **JupyterHub Companion** is a utility service designed to manage storage backends for JupyterHub environments.
It provides functionalities such as user and group management with disk quotas and usage tracking.


## Features

- **User Management**: Create, update, and delete users with optional disk quotas.
- **Group Management**: Manage groups with optional disk quotas.
- **Disk Usage Tracking**: Track disk usage for both users and groups.
- **Storage Backend Support**: Supports different storage backends (posix, zfs).


## Requirements

- Python 3.8 or higher
- FastAPI
- Uvicorn
- pip-tools _(optional, for dependency management)_

> **Note:** Ensure that the ZFS utilities are installed and properly configured if you plan to use ZFS as your storage backend.


## Installation

1. Open a command line interface on the target system.
2. Clone this repository:
   ```shell
   git clone <GIT_REPOSITORY>
   ```
3. Navigate to the cloned directory:
   ```shell
   cd jupyterhub-companion
   ```
4. Install the required dependencies:
   ```shell
   pip-compile -qr requirements.in
   pip install -U -r requirements.txt
   ```
5. Run the application using Uvicorn:
   ```shell
   uvicorn main:app --proxy-headers --host 0.0.0.0 --port 8080
   ```


## Configuration

The service can be configured using environment variables.
Below are all the available configuration options along with their descriptions and default values:

| Environmental Variable | Description                                                                                     | Default   |
|:-----------------------|:------------------------------------------------------------------------------------------------|:----------|
| API_KEY                | Secret key (length >= 16) used to authenticate requests to the API via `X-API-Key` HTTP header. | _(empty)_ |
| STORAGE_BACKEND        | Backend to use for storage (posix, zfs).                                                        | `posix`   |
| STORAGE_BASE_PATH      | Base path for shared storage where users' and groups' files are stored.                         | _(empty)_ |
| STORAGE_UID            | User ID of the storage owner.                                                                   | `1000`    |
| STORAGE_GID            | Group ID of the storage owner.                                                                  | `1000`    |


## API Endpoints

FastAPI automatically generates interactive API documentation and an OpenAPI schema.
When the service is running, you can access these resources at:

- **Interactive Documentation**: `/docs`
- **OpenAPI Schema**: `/openapi.json`