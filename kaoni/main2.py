import streamlit as st
from db_connector import get_connection
import openai
from dotenv import load_dotenv
import os

# .env 파일에서 환경 변수 로드
load_dotenv()

# OpenAI API 키 로드
openai.api_key = os.getenv('OPENAI_API_KEY')

# 페이지 설정
st.set_page_config(page_title="채용공고 검색", layout="wide")


# AI 모델을 사용하여 질문에서 키워드를 추출하는 함수
def extract_keywords_from_question(question, model_name):
    system_message = "너는 핵심 키워드를 구별하는 AI 모델이야"
    full_prompt = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": question}
        ],
    }
    try:
        response = openai.ChatCompletion.create(**full_prompt)
        keyword = response['choices'][0]['message']['content'].strip()
        return keyword
    except openai.error.OpenAIError as e:
        st.error(f"키워드 추출 중 에러가 발생했습니다: {e}")
        return None

# 데이터베이스에서 채용 정보를 가져오는 함수
def fetch_job_info(sql_query):
    # 데이터베이스에서 채용 정보 가져오기
    connection = get_connection()
    if not connection:
        st.error("데이터베이스 연결에 실패했습니다.")
        return []

    try:
        cursor = connection.cursor()
        cursor.execute(sql_query)
        job_infos = cursor.fetchall()
        
        # 반환된 데이터 로깅
        print(f"Fetched job infos: {job_infos}")
        if job_infos and len(job_infos[0]) != 5:
            print(f"Unexpected job info structure: {job_infos[0]}")
        
        return job_infos
    except Exception as e:
        st.error(f"직업 정보를 가져오는 데 에러가 발생했습니다: {e}")
        return []
    finally:
        if connection:
            cursor.close()
            connection.close()

# 채용 정보를 표시하는 함수
def display_job_info(job_info):
    try:
        if len(job_info) == 5:
            title, kind, organization, enddate, content = job_info
            st.write(f"**{title}**")
            st.write(f"**채용처, 채용의뢰:** {organization}")
            st.write(f"**마감일:** {enddate}")
            st.write(f"**채용 유형:** {kind}")
            st.write(f"**내용:** {content}")
            st.write(f"------------")
        else:
            st.error("채용 정보의 형식이 올바르지 않습니다.")
    except Exception as e:
        st.error(f"채용 정보를 표시하는 중 예외가 발생했습니다: {e}")



# 대화 기록을 저장할 전역 변수
if 'conversation' not in st.session_state:
    st.session_state['conversation'] = []

# 사이드바에 사용자 정의 스타일을 적용하기 위한 CSS 로드 함수
def local_css(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        st.sidebar.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# 사이드바 표시 함수
def display_conversation_sidebar():
    conversation = st.session_state['conversation']
    conversation_text = ""
    for item in conversation:
        if item['type'] == "user":
            conversation_text += f"<strong>사용자:</strong> {item['content']}<br>"
            conversation_text += "<hr>"  # 대화 구분선
        elif item['type'] == "answer":
            conversation_text += f"<strong>AI 답변:</strong> {item['content']}<br>"
        elif item['type'] == "job_info":
            job_info = item['content']
            title, kind, organization, enddate, content = job_info
            conversation_text += f"<strong>{title}</strong><br>"
            conversation_text += f"<strong>채용처, 채용의뢰:</strong> {organization}<br>"
            conversation_text += f"<strong>마감일:</strong> {enddate}<br>"
            conversation_text += f"<strong>채용 유형:</strong> {kind}<br>"
            conversation_text += f"<strong>내용:</strong> {content}<br>"
            conversation_text += "<hr>"  # 대화 구분선
               

    st.sidebar.markdown(conversation_text, unsafe_allow_html=True)

# 대화 기록 제목을 스타일링
st.sidebar.markdown('<div class="custom-header">대화 기록</div>', unsafe_allow_html=True)

def main():

    # CSS 파일 로드
    local_css('style.css')

    # 메인 페이지 컨텐츠
    st.title("채용공고 검색")
    user_input = st.text_input("여기에 질문을 입력하세요:")

    # '질문하기' 버튼이 클릭되면
    if st.button("질문하기"):
        
        
        # 사용자 입력을 대화 기록에 추가
        st.session_state['conversation'].append({"type": "user", "content": user_input})

        # 파인 튜닝된 모델 이름 지정
        model_name = "ft:gpt-3.5-turbo-0613:personal::8Jz0Zo0A"  # 모델 ID를 여기에 삽입

        # 질문에서 키워드 추출
        extracted_keyword = extract_keywords_from_question(user_input, model_name)

        # 추출된 키워드가 에러 메시지를 포함하지 않는 경우
        if extracted_keyword and 'Error' not in extracted_keyword:
            # SQL 쿼리 생성
            sql_query = f"SELECT title, kind, organization, enddate, content FROM job_postings WHERE title LIKE '%{extracted_keyword}%'"

            # 데이터베이스에서 채용 정보 검색
            job_infos = fetch_job_info(sql_query)

        # 대화 기록에 검색 결과 추가
        if job_infos:
            # AI 답변을 대화 기록에 추가
            st.session_state['conversation'].append({"type": "answer", "content": ""})
            for job_info in job_infos:
                display_job_info(job_info)
                # 채용 정보를 대화 기록에 추가
                st.session_state['conversation'].append({"type": "job_info", "content": job_info})
        else:
            st.error("해당 키워드에 맞는 채용공고를 찾을 수 없습니다.")

    # 사이드바 표시 함수 호출
    display_conversation_sidebar()
    pass

if __name__ == "__main__":
    main()
