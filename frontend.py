import streamlit as st

# Dictionary to store user credentials
# In a real application, use a database for storing credentials
users = {
    "user1": "password1",
    "user2": "password2"
}

honorID = [
    1234,5678
]

# Function to check login credentials
def check_login(username, password):
    return username in users and users[username] == password

# Function to register a new user
def register_user(username, password, honorID_):
    if honorID_ not in honorID:
        return False
    if username in users:
        return False
    users[username] = password
    return True

# Function to display the login page
def login_page():
    st.title("안녕하세요!")

    # Username and password input
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("로그인"):
        if check_login(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.experimental_rerun()  # Refresh the page to navigate to the second page
        else:
            st.error("Invalid username or password")

    if st.button("회원가입"):
        st.session_state.show_signup = True
        st.experimental_rerun()  # Refresh the page to navigate to the sign-up page

# Function to display the sign-up page
def signup_page():
    st.title("회원가입")

    # Username and password input
    username = st.text_input("New Username")
    password = st.text_input("New Password", type="password")
    honorID_ = st.text_input("HonorID")

    if st.button("회원가입"):
        if register_user(username, password,honorID_):
            st.success("회원가입 성공! 로그인하시길 바랍니다")
            st.session_state.show_signup = False
        else:
            st.error("wrong id")
            st.experimental_rerun()  # Refresh the page to navigate back to the login page
    if st.button("이전 페이지"):
        st.session_state.show_signup = False
        st.experimental_rerun()  # Refresh the page to navigate back to the login page

# Function to display the second page
def second_page():
    st.title("병역명문가 혜택 모음")
    st.success(f"환영합니다, {st.session_state.username}!")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.experimental_rerun()  # Refresh the page to navigate back to the login page

# Main function
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""
    
    if "show_signup" not in st.session_state:
        st.session_state.show_signup = False

    if st.session_state.logged_in:
        second_page()
    elif st.session_state.show_signup:
        signup_page()
    else:
        login_page()

if __name__ == "__main__":
    main()
