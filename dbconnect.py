import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb


def connection():
    conn = MySQLdb.connect(
        host = "localhost",
        user = "root",
        passwd = "password",
        db = "dental1"
    )
    c = conn.cursor()
    return c, conn
