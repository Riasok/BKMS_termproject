import streamlit as st
import pandas as pd

# Initialize session state for users if not already done
if 'users' not in st.session_state:
    st.session_state.users = {
        "user1": ["password1","user1@snu.ac.kr","bob"],
        "user2": ["password2","user2@snu.ac.kr","joe"]
    }

honorID_list = [1234, 5678]
data1 = {
    "시설명":["시설1", "시설2", "시설3"],
    "지역":["서울", "인천", "부산"],
}
data2 = {
    "시설명":["시설4", "시설5", "시설6"],
    "지역":["서울", "인천", "부산"],
}
table2 = {
    "상품":["초코파이", "신라면"],
    "가격":["1000","2000"]
}
data1 = pd.DataFrame(data1)
data2 = pd.DataFrame(data2)
table2 = pd.DataFrame(table2)

# Function to check login credentials
def check_login(username, password):
    return username in st.session_state.users and st.session_state.users[username][0] == password

# Function to register a new user
def register_user(username, password, email, name):
    if username in st.session_state.users:
        return False
    st.session_state.users[username] = [password,email,name]
    return True

def checkHonorID(honorID):
    return honorID in honorID_list

# Function to display the login page
def login_page():
    st.title("안녕하세요!")

    # Username and password input
    username = st.text_input("아이디")
    password = st.text_input("비밀번호", type="password")

    col1, col2 = st.columns([0.13, 1])
    with col1:
        login_button = st.button("로그인")
    with col2:
        signup_button = st.button("회원가입")

    if login_button:
        if check_login(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()  # Refresh the page to navigate to the second page
        else:
            st.error("잘못된 로그인 정보입니다!")
    if signup_button:
        st.session_state.show_signup = True
        st.rerun()  # Refresh the page to navigate to the sign-up page

# Function to display the sign-up page
def signup_page():
    st.title("회원가입")

    # Username, password, and HonorID input
    name = st.text_input("이름")
    email = st.text_input("이메일")
    honorID = st.text_input("군번")
    username = st.text_input("새로운 아이디")
    password = st.text_input("새로운 비밀번호", type="password")
    
    col1, col2 = st.columns([0.155, 1])
    with col1:
        signup_button = st.button("회원가입")
    with col2:
        back_button = st.button("이전 페이지")

    if signup_button:
        try:
            honorID = int(honorID)
            if checkHonorID(honorID):
                if register_user(username, password,email,name):
                    st.success("회원가입 성공! 로그인하시길 바랍니다")
                    st.session_state.show_signup = False
                else:
                    st.error("중복된 아이디입니다.")
            else:
                st.error("군번을 다시 확인해주세요")
        except:
            st.error("군번을 다시 확인해주세요")

    if back_button :
        st.session_state.show_signup = False
        st.rerun()  # Refresh the page to navigate back to the login page

# Function to display the main page
def main_page():
    st.title("병역명문가 혜택 모음")
    col1, col2 = st.columns([0.2,1])
    with col1:
        search_filter = st.selectbox("",["시설명","지역","업종"])
    with col2:
        search_query = st.text_input("원하는 시설을 검색하세요")

    if st.button("검색"):
        st.session_state.search_query = search_query
        st.session_state.show_search = True
        if search_filter == "시설명":
            st.session_state.search_type = "시설명"
        elif search_filter == "지역":
            st.session_state.search_type = "지역"
        elif search_filter == "업종":
            st.session_state.search_type = "업종"
        st.rerun()
    

    st.subheader("자주 검색되는 시설들")
    st.table(data1)
    st.subheader("평점이 높은 시설들")
    st.table(data2)
    with st.sidebar:
        st.title(f"환영합니다 {st.session_state.users[st.session_state.username][2]}님")
        st.subheader("PX 인기상품")
        st.table(table2)
        if st.button("로그아웃"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()  # Refresh the page to navigate back to the login page

#search page
def search_page():
    st.title(f"{st.session_state.search_type} 이 {st.session_state.search_query}인 검색 결과")
    n = 3
    for i in range(n):
        if st.button(f"{i}"):
            st.session_state.show_search = False
            st.session_state.show_facility = True
            st.rerun()

    if st.button("이전 페이지"):
        st.session_state.show_search = False
        st.rerun()

    with st.sidebar:
        st.title(f"환영합니다 {st.session_state.users[st.session_state.username][2]}님")
        st.subheader("PX 인기상품")
        st.table(table2)
        if st.button("로그아웃"):
            st.session_state.logged_in = False
            st.session_state.show_facility = False
            st.session_state.show_search = False
            st.session_state.username = ""
            st.rerun()  # Refresh the page to navigate back to the login page

def facility_page():
    if st.button("이전 페이지"):
        st.session_state.show_facility = False
        st.rerun()

    with st.sidebar:
        st.title(f"환영합니다 {st.session_state.users[st.session_state.username][2]}님")
        st.subheader("PX 인기상품")
        st.table(table2)
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
