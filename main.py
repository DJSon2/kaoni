import openai
from dotenv import load_dotenv
import os
from db_connector import get_connection  # 데이터베이스 연결을 위한 모듈 import

# .env 파일에서 환경 변수 로드
load_dotenv()

# OpenAI API 키 로드
openai.api_key = os.getenv('OPENAI_API_KEY')

def fetch_job_info_and_ask():
    # 데이터베이스에서 채용 정보 가져오기
    connection = get_connection()
    if not connection:
        print("Database connection couldn't be established")
        return

    try:
        cursor = connection.cursor()
        # 채용 정보를 조회하는 쿼리 실행
        cursor.execute("SELECT title, content, kind FROM job_postings LIMIT 1")
        job_info = cursor.fetchone()
        if job_info:
            title, content, kind = job_info
            # OpenAI API에 질문하기 위해 정보를 구성
            question = f"채용공고가'{title}'있나? 있으면 자세한 설명'{content}'과 모집 종류'{kind}'도 같이 보여줘"
            
            # OpenAI API에 질문
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=question,
                max_tokens=500
            )
            print(response.choices[0].text.strip())
        else:
            print("No job postings found in the database.")
    except Exception as e:
        print(f"Error fetching job information: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# 함수 실행
fetch_job_info_and_ask()