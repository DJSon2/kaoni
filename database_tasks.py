# database_tasks.py
from db_connector import get_connection  # 가정된 db_connector 모듈에서 연결 함수 가져오기
import mysql.connector
from mysql.connector import Error

def insert_job_posting(seq, title, kind, enddate, organization, content, regdate):
    # 데이터베이스 연결
    connection = get_connection()
    if connection is None:
        print("Database connection couldn't be established")
        return
    
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO job_postings (seq, title, kind, enddate, organization, content, regdate)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (seq, title, kind, enddate, organization, content, regdate)
        )
        connection.commit()
    except Error as e:
        print(f"An error occurred: {e}")
        if connection.is_connected():
            connection.rollback()
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
