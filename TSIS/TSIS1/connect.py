# connect.py — single place for DB connections
# Centralising the connection here means if we ever change DB settings,
# we only need to update config.py — nothing else in the project changes.

import psycopg2          # PostgreSQL adapter for Python; lets us send SQL from Python
from config import DB_CONFIG  # import the credentials dictionary from config.py


def get_connection():
    """
    Opens and returns a new connection to the PostgreSQL database.
    Called at the start of every function that needs to talk to the DB.
    The caller is responsible for closing the connection after use.
    """
    return psycopg2.connect(**DB_CONFIG)  # ** unpacks the dict as keyword arguments