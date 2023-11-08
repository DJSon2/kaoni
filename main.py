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
        print("데이터베이스 연결에 실패했습니다.")
        return

    try:
        cursor = connection.cursor()
        print("데이터베이스에 연결되었습니다, 쿼리를 실행합니다...")
        user_question_keyword = '2022'  # 이 부분은 사용자의 입력에 따라 동적으로 바뀔 수 있습니다.
        query = f"SELECT title, content, kind FROM job_postings WHERE title LIKE %s"
        cursor.execute(query, ('%' + user_question_keyword + '%',))
        
        # 결과를 가져오는 동작 또한 try-except로 감싸주세요
        try:
            job_infos = cursor.fetchall()
        except Exception as e:
            print(f"결과를 가져오는 데 에러가 발생했습니다: {e}")
            raise

        print(f"쿼리가 실행되었습니다, {len(job_infos)}개의 행을 가져왔습니다.")

        # job_infos 처리하는 코드
        for job_info in job_infos:
            if len(job_info) == 3:
                title, content, kind = job_info
                question = f"채용공고가 '{title}' 있나요? 있으면 자세한 설명 '{content}'과 모집 종류 '{kind}'도 같이 보여주세요."
                
                response = openai.Completion.create(
                    engine="text-davinci-003", 
                    prompt=question,
                    max_tokens=1000
                )
                print(response.choices[0].text.strip())
            else:
                print("데이터베이스에서 채용공고를 찾을 수 없습니다.")

    except Exception as e:
        print(f"직업 정보를 가져오는 데 에러가 발생했습니다: {e}")
    finally:
        # 닫기 전에 남아있는 모든 결과를 소비해야 합니다
        while connection.unread_result:
            cursor.fetchwarnings()
            cursor.fetchall()
        cursor.close()
        connection.close()

# 함수 실행
fetch_job_info_and_ask()
