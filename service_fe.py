import psycopg2
import base64
import time
import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_star_rating import st_star_rating      # pip install st-star-rating
from sql_deploy import myDB, log_search, fetch_users
from sklearn.neighbors import NearestNeighbors
from datetime import datetime

logo_path = "https://i.namu.wiki/i/PwjNC6S9U1KPSQrTGqnNDEgZ0lPKnNnKJ4ZU4FDFlc5bLZ1HIPTxdt6g5osxuwgq43bUQcym07ndc-irIU4LQLi36KCw3xb1hKOrK6vTRRM4DyieWjSQUGuQ7cDR6kwvflkFRMCKLOwUzO4ERq6YmQ.svg"
temp_img = "https://upload.wikimedia.org/wikipedia/commons/c/c1/%EC%A0%9C%EC%A3%BC%EB%8F%8C%EB%AC%B8%ED%99%94%EA%B3%B5%EC%9B%9001.jpg"

def connect_to_db():
    conn = psycopg2.connect(
       "postgres://avnadmin:AVNS_A9JfpBkyMrgT9ji6YhZ@pg-1d1f61c3-bkmsproject.i.aivencloud.com:22317/defaultdb?sslmode=require"
    )
    return conn

def fetch_data_from_db(query):
    '''
    Database에서 필요한 정보 가져오기
    '''
    conn = connect_to_db()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def get_base64_of_bin_file(bin_file):   
    '''
    이미지 불러오기
    '''
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# 등록된 사용자 정보 가져오기
if 'users' not in st.session_state:
    registered_users_df = fetch_users()   
    users = {}
    for index, row in registered_users_df.iterrows():
        userid = row['userid']
        password = row['password']
        email = row['email']
        name = row['이름']
        honorID = row['고유번호']
        users[userid] = [userid, honorID, email, password, name]
    st.session_state.users = users

# 사이드바 스타일 설정하기
st.markdown("""   
    <style>
    [data-testid="stSidebar"] .stButton button {
        border: none;
        background-color: transparent;
        color: black;
        font-size: 20px;
        cursor: pointer;
    }
    [data-testid="stSidebar"] .stButton button:hover {
        color: lightgreen; /* Optional: Add hover effect */
    }
    </style>
    """, unsafe_allow_html=True)

# 필요한 데이터 불러오기
facilitylist = pd.DataFrame(fetch_data_from_db("SELECT * FROM facility_list"))
px_info_data = pd.DataFrame(fetch_data_from_db("SELECT * FROM px_info"))
cooplist = pd.DataFrame(fetch_data_from_db("SELECT * FROM co_op_list"))
reservation_data = pd.DataFrame(fetch_data_from_db("SELECT * FROM reservation ORDER BY 예약일시 ASC"))
honorID_list = fetch_data_from_db("SELECT 고유번호 FROM prest_info")
honorID_list = honorID_list['고유번호'].tolist()


##### 로그인 ##### 
def check_login(username, password):
    '''
    로그인 조건 확인하기
    '''
    return username in st.session_state.users and st.session_state.users[username][3] == password

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
    background_pic_path = "data/main_page.png"  
    background_pic_path = get_base64_of_bin_file(background_pic_path)
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{background_pic_path}");
            background-size: contain;
            background-position: center;
            background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
    """
    <style>
    .centered {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 30vh;
    }
    .center-content {
        text-align: center;
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True
    )

    st.markdown('<div class="centered"><div class="center-content">', unsafe_allow_html=True)
    username = st.text_input("아이디")
    password = st.text_input("비밀번호", type="password")
    st.markdown('</div></div>', unsafe_allow_html=True)

    col1, col2 = st.columns([0.2, 1])
    with col1:
        login_button = st.button("로그인")
    with col2:
        signup_button = st.button("회원가입")

    if login_button:      # 로그인 시도
        if check_login(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()  
        else:
            st.error("사용자 이름 또는 비밀번호가 잘못되었습니다.")
    if signup_button:     # 회원가입
        st.session_state.show_signup = True
        st.rerun()  

def signup_page():
    '''
    회원가입 페이지
    '''
    st.title("회원가입")

    name = st.text_input("이름")
    email = st.text_input("이메일")
    honorID = st.text_input("고유번호")
    username = st.text_input("새로운 아이디")
    password = st.text_input("새로운 비밀번호", type="password")
    
    col1, col2 = st.columns([0.2, 1])
    with col1:
        signup_button = st.button("회원가입")
    with col2:
        back_button = st.button("메인 화면")

    if signup_button:
        db = myDB()
        try:
            if checkHonorID(honorID):
                try:
                    db.register_user(username, password, email, name, honorID)
                    st.success("회원가입 성공! 로그인하시길 바랍니다")
                     
                    user_data = db.fetch_user_by_id(username)  # db에 데이터가 삽입되었는지 확인
                    if user_data:
                        st.session_state.users[username] = [username, honorID, email, password, name]  # st.session_state.users에 새로 등록된 사용자 추가
                    else:
                        st.error("회원가입 후 데이터 확인에 실패했습니다.")
                    st.session_state.show_signup = False
                    db.close()
                    time.sleep(2)
                    st.rerun()
                except Exception as e:
                    st.error("회원가입 중 오류가 발생했습니다.")
                    st.error(str(e))
            else:
                st.error("고유번호를 다시 확인해주세요")
        except Exception as e:
            st.error("고유번호를 확인하는 중 오류가 발생했습니다.")
            st.error(str(e))
        finally:
            db.close()

    if back_button :
        st.session_state.show_signup = False
        st.rerun() 


##### 메인 페이지 #####
def main_page():
    '''
    메인 페이지
    '''
    background_pic_path = "data/main_page2.png" 
    background_pic_path = get_base64_of_bin_file(background_pic_path)
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{background_pic_path}");
            background-size: 100%;
            background-position: right;
            background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
    """
    <style>
    .centered {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 30vh;
    }
    .center-content {
        text-align: center;
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True
    )

    st.title("병역명문가 혜택 모음")
    col1, col2 = st.columns([0.2,1])
    with col1:
        search_filter = st.selectbox("",["시설명","지역","업종"])
    with col2:
        search_query = st.text_input("원하는 시설을 검색하세요")

    st.session_state.logged_searches = []   # search_count 2씩 증가하는 거 방지
    col3, col4, col5 = st.columns([0.2, 0.175, 0.8])
    with col3:
        search_button = st.button("검색")
    with col4:
        free = st.checkbox("할인")
    with col5:
        discount = st.checkbox("무료")
    st.session_state.free, st.session_state.discount = False, False

    if search_button:     # 검색
        st.session_state.search_query = search_query
        log_search(st.session_state.username, search_query, search_filter)  
        st.session_state.show_search = True
        st.session_state.show_main = False

        if free:
            st.session_state.free = True
        if discount:
            st.session_state.discount = True
        
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
    random_facility = db.get_random_facility()
    db.close()

    st.subheader("")
    col1, col2 = st.columns([1, 1])
    with col1: 
        if random_facility:
            st.markdown('**<p style="font-size:22px;">오늘의 추천 시설</p>**', unsafe_allow_html=True)
            st.write(f"{random_facility}")
            if st.button(f"다른 추천 받기"):
                st.rerun()
    with col2:
        st.markdown('**<p style="font-size:22px;">다가오는 예약</p>**', unsafe_allow_html=True)
        user_id = st.session_state.username
        db = myDB()
        try:
            user_reservations = db.fetch_user_reservations(user_id)
            if not user_reservations.empty:
                user_reservations["예약일시"] = pd.to_datetime(user_reservations["예약일시"]).dt.date
                user_reservations = user_reservations[user_reservations["예약일시"] >= datetime.now().date()]
                user_reservations = user_reservations.sort_values(by="예약일시")
                st.dataframe(user_reservations[["시설명", "예약일시"]])
            else:
                st.info("다가오는 예약이 없습니다.")
        except Exception as e:
            st.error(f"예약 정보를 가져오는 중 오류가 발생했습니다: {e}")
        finally:
            db.close()

    st.write("")
    st.markdown('**<p style="font-size:22px;">자주 검색되는 시설들</p>**', unsafe_allow_html=True)
    st.dataframe(popular_facilities, width = 800)

    st.markdown('**<p style="font-size:22px;">평점이 높은 시설들</p>**', unsafe_allow_html=True)
    st.dataframe(high_rate_facilities,  width = 800)

    with st.sidebar:
        st.image(logo_path, width=200)
        st.title(f"환영합니다 {st.session_state.users[st.session_state.username][4]}님")
        st.subheader("")

        if st.button("마이페이지"):
            st.session_state.show_mypage = True
            st.session_state.show_main = False
            st.experimental_rerun()

        if st.button("예약목록/예약하기"):
            st.session_state.show_reservation = True
            st.session_state.show_main = False
            st.experimental_rerun()

        if st.button("내 맞춤형 추천받기"):
            st.session_state.show_personalize = True
            st.session_state.show_main = False
            st.experimental_rerun()

        if st.button("국군복지단 협약기관 현황"):
            st.session_state.show_cooplist = True
            st.session_state.show_main = False
            st.experimental_rerun()

        if st.button("병역명문가 예우시설 목록"):
            st.session_state.show_facilitylist = True
            st.session_state.show_main = False
            st.experimental_rerun()

        if st.button("병역명문가 회원 조회"):
            st.session_state.show_view = True
            st.session_state.show_main = False
            st.experimental_rerun()

        if st.button("PX 인기상품"):
            st.session_state.show_px = True
            st.session_state.show_main = False
            st.experimental_rerun()
        
        if st.button("로그아웃"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.page = 'main'
            st.experimental_rerun()


##### 검색 페이지 #####
def search_page():
    '''
    검색 후 화면
    '''
    st.header(f"{st.session_state.search_type} 이 {st.session_state.search_query}인 검색 결과")
    db = myDB()
    if st.session_state.search_type == "시설명":
        search_result, type = db.search_by_name(st.session_state.search_query)
        if search_result:
            #예우시설인 경우
            if type == 0:
                st.image(temp_img, width=700) 
                st.write("")
                st.write("**시설명:**", search_result.get('시설명'))
                st.write("**예우시설/협약기관 분류:** 협약기관")
                st.write("**지역:**", search_result.get('지역'))
                st.write("**업종:**", search_result.get('업종')) 
                st.write("**항목:**", search_result.get('항목'))
                st.write("**예우시설고유번호:**", search_result.get('예우시설고유번호'))
                st.write("**우대내역:**", search_result.get('우대내역'))
                st.write("**면제/할인:**", search_result.get('면제할인'))
                st.write("**기관구분:**", search_result.get('기관구분'))
                if search_result.get('시설명') not in st.session_state.logged_searches:
                    db.log_search(search_result.get('시설명'))  # Log the search
                    st.session_state.logged_searches.append(search_result.get('시설명'))
                
                st.subheader("")
                st.subheader("")
                st.subheader("리뷰 목록")
                review = st.text_input("",value= "사용 후기를 남겨주세요!")
                stars = st_star_rating("",maxValue=5, defaultValue=3, key="rating", size = 30)
                insert = st.button("입력")
                if insert:
                    db.write_review(st.session_state.search_query, st.session_state.username, stars, review)
                    st.rerun()
                results = db.fac_reviews(st.session_state.search_query)
                st.dataframe(results, width=800)
            
            #협약기관인 경우
            elif type == 1:
                st.image(temp_img, width=700) 
                st.write("")
                st.write("**시설명:**", search_result.get('시설명'))
                st.write("**예우시설/협약기관 분류:** 협약기관")
                st.write("**지역:**", search_result.get('지역'))
                st.write("**업종:**", search_result.get('업종')) 
                st.write("**협약기관번호:**", search_result.get('협약기관번호'))
                st.write("**항목:**", search_result.get('항목'))
                st.write("**우대내역:**", search_result.get('우대내역'))
                if search_result.get('시설명') not in st.session_state.logged_searches:
                    db.log_search(search_result.get('시설명'))  # Log the search
                    st.session_state.logged_searches.append(search_result.get('시설명'))
                
                st.subheader("")
                st.subheader("")
                st.subheader("리뷰 목록")
                review = st.text_input("",value= "사용 후기를 남겨주세요!")
                stars = st_star_rating("",maxValue=5, defaultValue=3, key="rating", size = 30)
                insert = st.button("입력")
                if insert:
                    db.write_review(st.session_state.search_query, st.session_state.username, stars, review)
                    st.rerun()
                results = db.fac_reviews(st.session_state.search_query)
                st.dataframe(results, width=800)    
        else:
            st.write("해당 시설명을 찾을 수 없습니다.")
        
        with st.sidebar:
            st.title("추가 옵션")
            st.write("")
            if st.button("해당 시설 예약하기"):    # 예약 페이지로 전환
                st.session_state.show_search = False
                st.session_state.show_reservation = True
                st.experimental_rerun()

            if st.button("주변 관광지 추천"):
                region = search_result.get('지역')
                db = myDB()
                try:
                    rec_facilities = db.region_recommend(region)
                    if not rec_facilities.empty:
                        st.dataframe(rec_facilities)
                    else:
                        st.info("해당 지역의 추천 시설이 없습니다.")
                except Exception as e:
                    st.error(f"추천 시설 정보를 가져오는 중 오류가 발생했습니다: {e}")
                finally:
                    db.close()
                 

            if st.button("주변 군 복지시설 휴양 정보"):
                region = search_result.get('지역')
                db = myDB()
                try:
                    rec_facilities = db.near_recommend(region)
                    if not rec_facilities.empty:
                        st.dataframe(rec_facilities)
                    else:
                        st.info("해당 지역의 추천 시설이 없습니다.")
                except Exception as e:
                    st.error(f"추천 시설 정보를 가져오는 중 오류가 발생했습니다: {e}")
                finally:
                    db.close()
                                
    elif st.session_state.search_type == "지역":
        result1, result2 = db.search_by_region(st.session_state.search_query, st.session_state.free, st.session_state.discount)
        st.subheader("**예우시설**")
        st.dataframe(result1)
        st.subheader("**협약기관**")
        st.dataframe(result2)
        
    elif st.session_state.search_type == "업종":
        result1, result2 = db.search_by_type(st.session_state.search_query, st.session_state.free, st.session_state.discount)
        st.subheader("**예우시설**")
        st.dataframe(result1)
        st.subheader("**협약기관**")
        st.dataframe(result2)
        
    db.close()

    if st.button("메인 화면"):
        st.session_state.show_search = False
        st.session_state.show_main = True
        st.experimental_rerun()




##### 서브 페이지들 #####
def my_page():
    '''
    (1) 마이페이지
    '''
    user_id = st.session_state.username
    user_info = pd.DataFrame(fetch_data_from_db(f"SELECT * FROM registered_users WHERE userid = '{user_id}'"))
    if not user_info.empty:
        user_info = user_info.iloc[0] 
        profile_pic_path = "data/profile_pic.png" 
        profile_pic_base64 = get_base64_of_bin_file(profile_pic_path)
        
        st.markdown(
            f"""
            <style>
            .profile-pic {{
                border-radius: 50%;
                width: 150px;
                height: 150px;
                object-fit: cover;
            }}
            </style>
            <img src="data:image/png;base64,{profile_pic_base64}" class="profile-pic">
            """,
            unsafe_allow_html=True
        )
        st.subheader("")

        st.write(f"**아이디**: {user_info['userid']}")
        st.write(f"**이름**: {user_info['이름']}")
        st.write(f"**고유번호**: {user_info['고유번호']}")
        st.write(f"**이메일**: {user_info['email']}")
    else:
        st.error("사용자 정보를 가져오는 중 오류가 발생했습니다.")

    st.subheader("")
    st.subheader("내 정보 수정")
    with st.form(key='update_form'):
        # new_userid = st.text_input("아이디", user_info['userid'])
        new_userid = user_id
        new_name = st.text_input("이름", user_info['이름'])
        new_email = st.text_input("이메일", user_info['email'])
        password = st.text_input("비밀번호", type='password')

        submit_button = st.form_submit_button(label='수정 완료')

        if submit_button:
            h_id = st.session_state.users[st.session_state.username][1]
            db = myDB()
            db.update(new_userid, password, new_email, new_name, h_id)
            db.close()
                
            del st.session_state.users[st.session_state.username]
            st.session_state.users[new_userid] = [user_id, h_id, new_email, password, new_name]
            st.session_state.username = new_userid
            st.success("정보가 성공적으로 수정되었습니다.")
            time.sleep(2)
            st.rerun()

    st.title("")
    st.subheader(f"{st.session_state.users[st.session_state.username][4]}님의 예약정보")
    db = myDB()
    try:
        user_reservations = db.fetch_user_reservations(user_id)
        if not user_reservations.empty:
            st.dataframe(user_reservations)
        else:
            st.info("예약된 항목이 없습니다.")
    except Exception as e:
        st.error(f"예약 정보를 가져오는 중 오류가 발생했습니다: {e}")

    st.title("")
    st.subheader(f"{st.session_state.users[st.session_state.username][4]}님의 리뷰")
    user_review = pd.DataFrame(fetch_data_from_db(f"SELECT * FROM review WHERE userid = '{user_id}'"))
    st.dataframe(user_review, width=800)

    db.close()

    st.subheader("")
    if st.button("메인 화면"):
        st.session_state.show_mypage = False
        st.session_state.show_main = True
        st.experimental_rerun()

def reservation_page():
    '''
    (2) 예약목록 및 예약하기 페이지
    '''
    st.title("예약 현황")
    cur_date = datetime.now().date()
    cur_date = cur_date.strftime('%Y-%m-%d')
    reservation_data = pd.DataFrame(fetch_data_from_db(f"SELECT * FROM reservation WHERE 예약일시 > '{cur_date}' ORDER BY 예약일시"))
    st.dataframe(reservation_data, width = 800)

    facility_search = st.text_input("예약 가능 여부를 확인하고 싶은 시설명을 입력하세요")
    if st.button("검색"):
        try:
            availability = fetch_data_from_db(f"SELECT 예약가능 FROM facility_list WHERE 시설명 = '{facility_search}'")
            if not availability.empty:
                st.info(f"시설 '{facility_search}'의 예약 가능 수:  {availability.iloc[0, 0]}")
            else:
                st.warning("해당 시설명을 찾을 수 없습니다.")
        except Exception as e:
            st.error(f"검색 중 오류가 발생했습니다: {e}")


    st.title("")
    st.subheader("새 예약 추가")
    with st.form(key='reservation_form'):
        facility_id = st.text_input("시설명")
        user_id = st.text_input("유저 ID")
        reservation_date = st.date_input("예약일시")
        submit_button = st.form_submit_button(label='예약')
    if submit_button:
        db = myDB()
        try:
            user_check_query = "SELECT COUNT(*) FROM registered_users WHERE userid = %s"   # userid 확인
            db.cursor.execute(user_check_query, (user_id,))
            user_check_result = db.cursor.fetchone()
            if user_check_result[0] == 0:
                st.error("등록되지 않은 아이디입니다.")
            else:
                facility_check_query = "SELECT COUNT(*) FROM facility_list WHERE 시설명 = %s"  # 시설명 확인
                db.cursor.execute(facility_check_query, (facility_id,))
                facility_check_result = db.cursor.fetchone()
                if facility_check_result[0] == 0:
                    st.error("존재하지 않는 시설입니다. 시설명을 다시 확인해주세요.")
                else:
                    availability_check_query = "SELECT 예약가능 FROM facility_list WHERE 시설명 = %s"  # 예약 가능 여부 확인
                    db.cursor.execute(availability_check_query, (facility_id,))
                    availability_check_result = db.cursor.fetchone()
                    if availability_check_result[0] <= 0:
                        st.error("예약이 불가능한 시설입니다.")
                    else:
                        reservation_check_query = "SELECT COUNT(*) FROM reservation WHERE userID = %s AND 예약일시 = %s AND 시설명 = %s"  # 기존 예약 여부 확인
                        reservation_date_str = reservation_date.strftime('%Y-%m-%d')
                        db.cursor.execute(reservation_check_query, (user_id, reservation_date_str, facility_id))
                        reservation_check_result = db.cursor.fetchone()
                        if reservation_check_result[0] > 0:
                            st.error("이미 예약된 내역입니다.")
                        else:    # 모든 조건 통과 - 예약 추가
                            insert_reservation_query = """
                                INSERT INTO reservation (userID, 예약일시, 시설명)
                                VALUES (%s, %s, %s)
                            """
                            db.cursor.execute(insert_reservation_query, (user_id, reservation_date_str, facility_id))
                            update_facility_query = "UPDATE facility_list SET 예약가능 = 예약가능 - 1 WHERE 시설명 = %s"  # 예약 가능 수 업데이트
                            db.cursor.execute(update_facility_query, (facility_id,))
                            db.conn.commit()
                            st.success("예약이 성공적으로 추가되었습니다.")
                            st.experimental_rerun()
        except Exception as e:
            st.error(f"예약 중 오류가 발생했습니다: {e}")
        finally:
            db.close()
    
    if st.button("메인 화면"):
        st.session_state.show_reservation = False
        st.session_state.show_main = True
        st.experimental_rerun()

    with st.sidebar:
        st.title(f"바로가기")
        if st.button("내 예약보기"):
            user_id = st.session_state.username
            db = myDB()
            try:
                user_reservations = db.fetch_user_reservations(user_id)
                if not user_reservations.empty:
                    st.dataframe(user_reservations)
                else:
                    st.info("예약된 항목이 없습니다.")
            except Exception as e:
                st.error(f"예약 정보를 가져오는 중 오류가 발생했습니다: {e}")
            finally:
                db.close()

def personalize_page():
    '''
    (3) 맞춤형 추천 서비스 페이지
    '''
    st.title("AI 추천 서비스")
    st.write("나와 유사한 고객의 사용 패턴을 분석해 맞춤형 추천을 해드리는 서비스입니다.")
    st.subheader("")

    facility_name = st.text_input("시설명을 입력하세요")
    if st.button("추천받기"):
        db = myDB()
        if db.facility_exists(facility_name):
            ratings_df = fetch_data_from_db("SELECT 시설명, avg(평점) as 평균평점 FROM review GROUP BY 시설명")
            search_counts_df = fetch_data_from_db("SELECT search_query as 시설명, COUNT(*) as 검색량 FROM search_logs GROUP BY search_query")
            facility_data = pd.merge(ratings_df, search_counts_df, on='시설명')

            if facility_name not in facility_data['시설명'].values:
                st.error("입력하신 시설명에 대한 데이터가 부족합니다.")
            else:
                X = facility_data[['평균평점', '검색량']].values

                # kNN 모델 학습
                k = 5 
                knn_model = NearestNeighbors(n_neighbors=k, algorithm='auto')
                knn_model.fit(X)

                facility_index = facility_data[facility_data['시설명'] == facility_name].index[0]
                distances, indices = knn_model.kneighbors([X[facility_index]], n_neighbors=k+1)
                recommended_facilities = facility_data.iloc[indices[0][1:]]

                st.title("")
                st.subheader("추천 시설 목록")
                st.table(recommended_facilities)
        else:
            st.error("시설명을 입력하세요")
        db.close()
    
    st.title("")
    if st.button("메인 화면"):
        st.session_state.show_personalize = False
        st.session_state.show_main = True
        st.experimental_rerun()

def cooplist_page():
    '''
    (4) 협약 기관 리스트 확인 페이지
    '''
    st.title("국군복지단 협약기관 현황")
    st.write("")
    if st.button("메인 화면"):
        st.session_state.show_cooplist = False
        st.session_state.show_main = True
        st.experimental_rerun()
    st.dataframe(cooplist, width = 800)

def facilitylist_page():
    '''
    (5) 병역명문가 예우시설 목록 페이지
    '''
    st.title("병역명문가 예우시설 목록")
    st.write("")
    if st.button("메인 화면"):
        st.session_state.show_facilitylist = False
        st.session_state.show_main = True
        st.experimental_rerun()
    st.write("")

    # 필터링 기능 적용
    col1, col2, col3 = st.columns([0.2, 0.2, 0.6])
    with col1:
        discount_label = st.write("**면제할인:**")
    with col2:
        exemption = st.checkbox("면제")
    with col3:
        discount = st.checkbox("할인")
    col1, col2, col3, col4 = st.columns([0.2, 0.2, 0.2, 0.4])
    with col1:
        institution_label = st.write("**기관구분**:")
    with col2:
        government = st.checkbox("지자체")
    with col3:
        private = st.checkbox("민간")
    with col4:
        national = st.checkbox("국가")

    filtered_facilitylist = facilitylist.copy()

    if any([exemption, discount]):
        discount_filters = []
        if exemption:
            discount_filters.append("면제")
        if discount:
            discount_filters.append("할인")
        filtered_facilitylist = filtered_facilitylist[filtered_facilitylist['면제할인'].isin(discount_filters)]

    if any([government, private]):
        institution_filters = []
        if government:
            institution_filters.append("지자체")
        if private:
            institution_filters.append("민간")
        filtered_facilitylist = filtered_facilitylist[filtered_facilitylist['기관구분'].isin(institution_filters)]

    st.markdown("""
    <style>
    .small-font {
        font-size:12px !important;
        text-align: center !important;
    }
    table {
        width: 100%;
    }
    th, td {
        text-align: center !important;
        vertical-align: middle !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown(filtered_facilitylist.to_html(classes='small-font', index=False), unsafe_allow_html=True)

def view_page():
    '''
    (6) 병역명문과 회원 조회 페이지
    '''
    st.title("병역명문가 회원 조회")
    st.write("")
    if st.button("메인 화면"):
        st.session_state.show_view = False
        st.session_state.show_main = True
        st.experimental_rerun()
    st.write("")
    db = myDB()
    honor_members_df = db.fetch_honor_members()

    col1, col2, col3, col4, col5, col6 = st.columns([0.2, 0.2, 0.2, 0.2, 0.25, 0.35])
    with col1:
        army_type = st.write("**군구분:**")
    with col2:
        airforce = st.checkbox("공군")
    with col3:
        army = st.checkbox("육군")
    with col4:
        navy = st.checkbox("해군")
    with col5:
        marine = st.checkbox("해병대")
    with col6:
        non_army = st.checkbox("비군인(6.25참전)")

    filtered_honor_members_df= honor_members_df.copy()

    if any([airforce, army, navy, marine, non_army]):
        army_type_filters = []
        if airforce:
            army_type_filters.append("공군")
        if army:
            army_type_filters.append("육군")
        if navy:
            army_type_filters.append("해군")
        if marine:
            army_type_filters.append("해병대")
        if non_army:
            army_type_filters.append("비군인(6.25참전)")
        
        filtered_honor_members_df = filtered_honor_members_df[filtered_honor_members_df['군구분'].isin(army_type_filters)]
    
    st.table(filtered_honor_members_df)
    db.close()

def px_page():
    '''
    (7) PX 인기상품 페이지
    '''
    st.title("PX 인기상품")
    st.write("")
    if st.button("메인 화면"):
        st.session_state.show_px = False
        st.session_state.show_main = True
        st.experimental_rerun()
    st.dataframe(px_info_data, width = 800)






def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""
    if "show_signup" not in st.session_state:
        st.session_state.show_signup = False
    if "show_search" not in st.session_state:
        st.session_state.show_search = False
    if "show_mypage" not in st.session_state:
        st.session_state.show_mypage = False
    if "show_reservation" not in st.session_state:
        st.session_state.show_reservation = False
    if "show_personalize" not in st.session_state:
        st.session_state.show_personalize = False
    if "show_cooplist" not in st.session_state:
        st.session_state.show_cooplist= False
    if "show_facilitylist" not in st.session_state:
        st.session_state.show_facilitylist= False
    if "show_view" not in st.session_state:
        st.session_state.show_view = False
    if "show_px" not in st.session_state:
        st.session_state.show_px = False

    
    if st.session_state.logged_in:
        if st.session_state.show_search:
            search_page()
        elif st.session_state.show_mypage:
            my_page()
        elif st.session_state.show_reservation:
            reservation_page()
        elif st.session_state.show_personalize:
            personalize_page()
        elif st.session_state.show_cooplist:
            cooplist_page()
        elif st.session_state.show_facilitylist:
            facilitylist_page()
        elif st.session_state.show_view:
            view_page()
        elif st.session_state.show_px:
            px_page()
        else:
            main_page()
    else:
        if st.session_state.show_signup:
            signup_page()
        else:
            login_page() 
    print(f"Session state: {st.session_state}")  # Debugging statement

if __name__ == "__main__":
    main()