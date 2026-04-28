# config.py — database connection parameters
# This dictionary holds all needed to connect to PostgreSQL.
# It is imported by connect.py and passed directly to psycopg2.connect().

DB_CONFIG = {
    "host":     "localhost",  # the server where PostgreSQL is running (local machine)
    "database": "postgres",   # the name of the database to connect to
    "user":     "postgres",   # the PostgreSQL username
    "password": "NN26102007",     # the password for the above user
    "port":     "5432",       # default PostgreSQL port
}