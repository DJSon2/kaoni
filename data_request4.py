import requests
import json
from datetime import datetime
from database_tasks import insert_job_posting  # database_tasks 모듈에서 데이터베이스 작업 함수 가져오기

def fetch_and_store_job_postings(api_url):
    # API로부터 데이터 요청
    response = requests.get(api_url)
    if response.status_code != 200:
        print("Data fetching failed.")
        return

    # JSON 파싱
    data = json.loads(response.content)

    # 현재 시간을 문자열로 포맷팅
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 'data' 키에 해당하는 리스트를 순회하면서 각 정보를 추출하고 데이터베이스에 저장
    for item in data['data']:
        seq = item['생산아이디']
        title = item['채용제목']
        kind = f"공고유형 : {item['공고유형']}"
        enddate = item['채용종료일자']
        organization = "통계청_채용공고"
        # regdate 처리, 값이 없으면 현재 시간으로 설정
        regdate = item.get('regdate', current_time).strip() if item.get('regdate', '').strip() else current_time
        content = f"일괄모집여부: {item['일괄모집여부']}"
            
        # 데이터베이스에 삽입
        insert_job_posting(seq, title, kind, enddate, organization, content, regdate)

# API 엔드포인트 URL - 실제 요청 URL을 사용합니다.
api_url = 'https://api.odcloud.kr/api/15070391/v1/uddi:a5aeb984-a8a1-475b-8ad8-db5f6563bf1a?page=1&perPage=10&serviceKey=bfzIrXZ6samznW7lltLbfU8XyvtHTbku5Q9zjQZQm0%2FTSyawXf2D3O091EYgnILM%2FzSBQxhqkeYqIwwa7srQeQ%3D%3D'

# API 엔드포인트로부터 데이터를 가져와서 저장하는 함수를 호출합니다.
fetch_and_store_job_postings(api_url)
