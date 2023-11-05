# data_request.py
import xml.etree.ElementTree as ET
import requests
from database_tasks import insert_job_posting  # database_tasks 모듈에서 데이터베이스 작업 함수 가져오기

def fetch_and_store_job_postings(api_url):
    # API로부터 데이터 요청
    response = requests.get(api_url)
    if response.status_code != 200:
        print("Data fetching failed.")
        return

    # XML 파싱
    root = ET.fromstring(response.content)

    # 'item' 태그들을 순회하면서 각 정보를 추출하고 데이터베이스에 저장
    for item in root.findall('item'):
        seq = item.find('seq').text.strip() if item.find('seq') is not None else None
        title = item.find('title').text.strip() if item.find('title') is not None else None
        kind = item.find('kind').text.strip() if item.find('kind') is not None else None
        enddate = item.find('enddate').text.strip() if item.find('enddate') is not None else None
        organization = item.find('organization').text.strip() if item.find('organization') is not None else None
        content = item.find('content').text.strip() if item.find('content') is not None else None
        regdate = item.find('regdate').text.strip() if item.find('regdate') is not None else None
        
        # 데이터베이스에 삽입
        insert_job_posting(seq, title, kind, enddate, organization, content, regdate)

# API 엔드포인트 URL
api_url = 'https://www.ice.go.kr/recruit/rss.do'
fetch_and_store_job_postings(api_url)
