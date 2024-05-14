import mysql.connector

def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        port='3306',
        user='root',
        password='11046067',
        database='healthy'
    )
    return connection
