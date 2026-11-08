
import mysql.connector
from database.db import get_db_connection


def get_all_students():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, fullname, educational_level
        FROM students
        ORDER BY fullname ASC
    """)

    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return students


def add_student(fullname, educational_level):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO students (fullname, educational_level)
        VALUES (%s, %s)
    """, (fullname, educational_level))

    connection.commit()

    cursor.close()
    connection.close()


def delete_student(student_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM students WHERE id = %s",
        (student_id,)
    )

    connection.commit()

    deleted = cursor.rowcount > 0

    cursor.close()
    connection.close()

    return deleted
