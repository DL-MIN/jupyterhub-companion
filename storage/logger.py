"""
This module sets up a logger for the 'uvicorn.error' channel.
It can be used to log error messages related to the Uvicorn server.
"""

import logging

logger = logging.getLogger("uvicorn.error")
