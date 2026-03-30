import psycopg2 #library for working with SQL
from config import DB_CONFIG

def get_connection(): #connection to DB
    return psycopg2.connect(**DB_CONFIG) #unpacking the dictionary