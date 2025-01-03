import mysql.connector

db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="taskManager"
)

cursor = db_connection.cursor()

def close_connection():
    cursor.close()
    db_connection.close()
