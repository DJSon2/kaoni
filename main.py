import streamlit as st
from db_connector import get_connection
from dotenv import load_dotenv
import os

# .env 파일에서 환경 변수 로드
load_dotenv()

# 초기화
if 'search_history' not in st.session_state:
    st.session_state['search_history'] = []

def fetch_job_info_and_ask(column, user_question_keyword):
    # 데이터베이스에서 채용 정보 가져오기
    connection = get_connection()
    if not connection:
        st.error("데이터베이스 연결에 실패했습니다.")
        return []

    try:
        cursor = connection.cursor()
        query = f"SELECT title, content, kind, organization, enddate FROM job_postings WHERE {column} LIKE %s"
        cursor.execute(query, ('%' + user_question_keyword + '%',))
        job_infos = cursor.fetchall()
    except Exception as e:
        st.error(f"직업 정보를 가져오는 데 에러가 발생했습니다: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return job_infos

def display_job_info(job_info):
    # 채용 정보를 문자열로 포맷팅하여 반환
    title, content, kind, organization, enddate = job_info
    info_str = f"**{title}**  \n" \
           f"**채용처, 채용의뢰:** {organization}  \n" \
           f"**마감일:** {enddate}  \n" \
           f"**채용 유형:** {kind}  \n" \
           f"**내용:** {content}"

    st.markdown(info_str)
               
    return info_str

def display_search_history():
    # 검색 기록을 역순으로 표시
    for entry in reversed(st.session_state['search_history']):
        st.text(f"질문: {entry['question']} (검색 종류: {entry['column']})")
        st.text("답변:")
        st.write(entry['answer'])
        st.write("---")

def main():
    st.title("채용공고 검색")

    # 검색 기록 표시
    display_search_history()

    # 사용자 입력을 요청하는 UI 컴포넌트 (하단에 배치)
    with st.container():
        column = st.selectbox('검색할 열을 선택하세요:', ('title', 'organization', 'content', 'kind', 'enddate'), key='column_select')
        user_question_keyword = st.text_input('검색하고 싶은 채용공고의 키워드를 입력하세요:', key='question_input')
        search_clicked = st.button('검색')

    # 검색 버튼 클릭 시 로직
    if search_clicked:
        job_infos = fetch_job_info_and_ask(column, user_question_keyword)

        # 가져온 채용 정보 표시 및 검색 기록에 추가
        if job_infos:
            answer = ""
            for job_info in job_infos[:3]:  # 최대 3개의 결과만 포맷팅
                answer += display_job_info(job_info) + "\n\n---\n\n"
            st.session_state['search_history'].append({
                "column": column,
                "question": user_question_keyword,
                "answer": answer.rstrip("\n\n---\n\n")  # 마지막 구분선을 제거
            })
        else:
            st.error("채용공고를 찾을 수 없습니다.")
            st.session_state['search_history'].append({
                "column": column,
                "question": user_question_keyword,
                "answer": "검색 결과가 없습니다."
            })

if __name__ == "__main__":
    main()
