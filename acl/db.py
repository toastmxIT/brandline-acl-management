import sys
import psycopg2
from psycopg2 import OperationalError

# rds settings
rds_host = "rds-sm.con1rcg8el6v.us-west-2.rds.amazonaws.com"
name = 'masterDB'
password = 'sm12345678'
db_name = 'brandline'


def dbconnect():
    try:
        return psycopg2.connect(host=rds_host, user=name, password=password, dbname=db_name, port=5432)
    except OperationalError as e:
        # err_type, err_obj, traceback = sys.exc_info()
        # return err_type
        sys.exit()


def execute_query(statement):
    """
    This function fetches content from MySQL RDS instance
    """

    conn = dbconnect()

    with conn.cursor() as cur:
        cur.execute(statement)
        return cur.fetchall()
