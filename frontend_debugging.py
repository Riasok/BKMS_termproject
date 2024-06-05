import psycopg2
import streamlit as st
import pandas as pd
from sql import myDB
from sql import fetch_users


logo_path = "https://i.namu.wiki/i/PwjNC6S9U1KPSQrTGqnNDEgZ0lPKnNnKJ4ZU4FDFlc5bLZ1HIPTxdt6g5osxuwgq43bUQcym07ndc-irIU4LQLi36KCw3xb1hKOrK6vTRRM4DyieWjSQUGuQ7cDR6kwvflkFRMCKLOwUzO4ERq6YmQ.svg"


def connect_to_db():
    conn = psycopg2.connect(
        database="postgres", user='postgres', password='0911', host='localhost', port='5432'
    )
    return conn

def fetch_data_from_db(query):
    conn = connect_to_db()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

if 'users' not in st.session_state:
    # Fetch users from database
    registered_users_df = fetch_users()
    users = {}
    for index, row in registered_users_df.iterrows():
        userid = row['userid']
        password = row['password']
        email = row['email']
        name = row['이름']
        users[userid] = [password, email, name]

    st.session_state.users = users




# 데이터 불러오기
px_info_data = pd.DataFrame(fetch_data_from_db("SELECT * FROM px_info"))
honorID_list = fetch_data_from_db("SELECT 고유번호 FROM prest_info")
honorID_list = honorID_list['고유번호'].tolist()





##### 로그인
def check_login(username, password):
    '''
    로그인 조건 확인하기
    '''
    return username in st.session_state.users and st.session_state.users[username][0] == password

def register_user(username, password, email, name):
    '''
    새로운 유저 등록하기
    '''
    if username in st.session_state.users:
        return False
    st.session_state.users[username] = [password,email,name]
    return True

def checkHonorID(honorID):
    '''
    고유번호 확인하기
    '''
    return honorID in honorID_list

def login_page():
    '''
    로그인 페이지
    '''
    st.title("호국명문 혜택백서")

    username = st.text_input("아이디")
    password = st.text_input("비밀번호", type="password")

    col1, col2 = st.columns([1, 1])
    with col1:
        login_button = st.button("로그인")
    with col2:
        signup_button = st.button("회원가입")

    if login_button:
        if check_login(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()  # Refresh the page -> main page
        else:
            st.error("사용자 이름 또는 비밀번호가 잘못되었습니다.")
    if signup_button:
        st.session_state.show_signup = True
        st.rerun()  # Refresh the page -> sign-up page

def signup_page():
    '''
    회원가입 페이지
    '''
    st.title("회원가입")

    # Username, password, and HonorID input
    name = st.text_input("이름")
    email = st.text_input("이메일")
    honorID = st.text_input("군번")
    username = st.text_input("새로운 아이디")
    password = st.text_input("새로운 비밀번호", type="password")
    
    col1, col2 = st.columns([0.2, 1])
    with col1:
        signup_button = st.button("회원가입")
    with col2:
        back_button = st.button("이전 페이지")

    if signup_button:
        try:
            if checkHonorID(honorID):
                try:
                    if register_user(username, password, email, name):
                        st.success("회원가입 성공! 로그인하시길 바랍니다")
                        st.session_state.show_signup = False
                        #st.session_state.page = 'login'
                        st.rerun()
                    else:
                        st.error("중복된 아이디입니다.")
                except Exception as e:
                    st.error("회원가입 중 오류가 발생했습니다.")
                    st.error(str(e))
            else:
                st.error("군번을 다시 확인해주세요")
        except Exception as e:
            st.error("군번을 확인하는 중 오류가 발생했습니다.")
            st.error(str(e))

    if back_button :
        st.session_state.show_signup = False
        st.rerun()  # Refresh the page -> login page








##### 메인 페이지
def main_page():
    '''
    메인 페이지
    '''
    st.title("병역명문가 혜택 모음")
    col1, col2 = st.columns([0.2,1])
    with col1:
        search_filter = st.selectbox("",["시설명","지역","업종"])
    with col2:
        search_query = st.text_input("원하는 시설을 검색하세요")

    st.session_state.logged_searches = []   # search_count 2씩 증가하는 거 방지
    if st.button("검색 🔍"):
        st.session_state.search_query = search_query
        st.session_state.show_search = True
        st.session_state.show_main = False
        if search_filter == "시설명":
            st.session_state.search_type = "시설명"
        elif search_filter == "지역":
            st.session_state.search_type = "지역"
        elif search_filter == "업종":
            st.session_state.search_type = "업종"
        st.experimental_rerun()

    db = myDB()
    popular_facilities = db.search_count_and_rank()
    high_rate_facilities = db.grade_rank()
    db.close()

    st.subheader("자주 검색되는 시설들")
    st.table(popular_facilities)

    st.subheader("평점이 높은 시설들")
    st.table(high_rate_facilities)

    with st.sidebar:
        st.image(logo_path, width=150)
        st.title(f"환영합니다 {st.session_state.users[st.session_state.username][2]}님")
        
        if st.button("예약 목록"):
            st.session_state.page = 'reservation'
            reservation_page()

        if st.button("병역명문가 회원 조회"):
            st.session_state.page = 'view'
            view_page()

        if st.button("PX 인기상품"):
            st.session_state.page = 'px'
            px_page()
        
        if st.button("로그아웃"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.page = 'main'
            st.rerun()  # Refresh the page to navigate back to the login page


##### 서브 페이지들
def px_page():
    st.title("PX 인기상품")
    st.table(px_info_data)

def reservation_page():
    st.title("예약 목록")

def view_page():
    st.title("병역명문가 회원 조회")


#search page
def search_page():
    st.title(f"{st.session_state.search_type} 이 {st.session_state.search_query}인 검색 결과")
    db = myDB()
    if st.session_state.search_type == "시설명":
        search_result = db.search_by_name(st.session_state.search_query)
        if search_result:
            st.write("시설명: ", search_result.get('시설명'))
            st.write("지역: ", search_result.get('지역'))
            st.write("업종: ", search_result.get('업종'))
            st.write("항목: ", search_result.get('항목'))
            st.write("예우시설고유번호: ", search_result.get('예우시설고유번호'))
            st.write("우대내역: ", search_result.get('우대내역'))
            st.write("면제할인: ", search_result.get('면제할인'))
            st.write("기관구분: ", search_result.get('기관구분'))
            if search_result.get('시설명') not in st.session_state.logged_searches:
                db.log_search(search_result.get('시설명'))  # Log the search
                st.session_state.logged_searches.append(search_result.get('시설명'))
        else:
            st.write("해당 시설명을 찾을 수 없습니다.")
    elif st.session_state.search_type == "지역":
        search_results = db.search_by_region(st.session_state.search_query)
        st.dataframe(search_results)
    # 필요한 경우 다른 검색 조건에 따라 다른 SQL 함수 호출 추가
    db.close()

    if st.button("이전 페이지"):
        st.session_state.show_search = False
        st.session_state.show_main = True
        st.experimental_rerun()

    # with st.sidebar:                ######## 여기에 무슨 다른 옵션들 넣으면 좋을 듯
    #     st.title(f"환영합니다 {st.session_state.users[st.session_state.username][2]}님")
    #     st.subheader("PX 인기상품")
    #     st.table(px_info_data)
    #     if st.button("로그아웃 🚪"):
    #         st.session_state.logged_in = False
    #         st.session_state.show_facility = False
    #         st.session_state.show_search = False
    #         st.session_state.username = ""
    #         st.rerun()  # Refresh the page to navigate back to the login page

def facility_page():
    if st.button("이전 페이지"):
        st.session_state.show_facility = False
        st.rerun()

    with st.sidebar:
        st.title(f"환영합니다 {st.session_state.users[st.session_state.username][2]}님")
        st.subheader("PX 인기상품")
        st.table(px_info_data)
        if st.button("로그아웃"):
            st.session_state.logged_in = False
            st.session_state.show_facility = False
            st.session_state.show_search = False
            st.session_state.username = ""
            st.rerun()  # Refresh the page to navigate back to the login page

# Main function
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""
    
    if "show_signup" not in st.session_state:
        st.session_state.show_signup = False

    if "show_facility" not in st.session_state:
        st.session_state.show_facility = False

    if "show_search" not in st.session_state:
        st.session_state.show_search = False

    if st.session_state.show_facility:
        facility_page()
    elif st.session_state.show_search:
        search_page()
    elif st.session_state.logged_in:
        main_page()
    elif st.session_state.show_signup:
        signup_page()
    else:
        login_page()


    
    print(f"Session state: {st.session_state}")  # Debugging statement

if __name__ == "__main__":
    main()