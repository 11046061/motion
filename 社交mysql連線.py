import mysql.connector

connection=mysql.connector.connect(host='localhost',
                                   port='3306',
                                   user='root',
                                   password='113409',
                                   database='fitness')

cursor = connection.cursor()

cursor.execute ('SELECT * FROM fitness.friendships;')

records = cursor.fetchall()
for r in records:
    print(r)               