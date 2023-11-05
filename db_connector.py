import mysql.connector
from mysql.connector import Error

def get_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',       # 데이터베이스 서버 주소
            database='kaoni',        # 데이터베이스 이름
            user='root',            # 데이터베이스 사용자명
            password='Thsehdwls12!@'     # 데이터베이스 패스워드
        )
        print("MySQL 연동 성공 ", connection.get_server_info())
        return connection
    except Error as e:
        print("Error while connecting to MySQL", e)
        return None
