import random
import string
import pandas as pd
import psycopg2
from datetime import datetime


# userid, 고유번호, email, password, 이름, 생년, 회원 구분

def connect_to_db():
    conn = psycopg2.connect(
        database="postgres", user='postgres', password='0911', host='localhost', port='5432'
    )
    return conn

def generate_email():
    domains = ["gmail.com", "naver.com", "daum.net", "outlook.com"]
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8)) + '@' + random.choice(domains)

def generate_password():
    return ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=10))

def generate_korean_name():
    last_names = ["김", "이", "박", "최", "정", "강", "조", "윤", "장", "임", "오", "한", "서", "신", "권", "황", "안", "송", "류", "홍"]
    first_names = [
        "민준", "서준", "도윤", "예준", "시우", "하준", "주원", "지호", "준우", "준서", 
        "우진", "현우", "지안", "은우", "서윤", "서준", "태윤", "도현", "지원", "현서", 
        "윤우", "지후", "서진", "태연", "하진", "연우", "진우", "민혁", "준호", "지율", 
        "현빈", "지훈", "채윤", "지한", "성민", "수호", "태호", "승현", "도훈", "세현",
        "승우", "지완", "성현", "민규", "시현", "윤호", "민성", "재윤", "우빈", "예성",
        "지환", "동현", "승준", "재원", "승민", "정우", "태민", "민찬", "준혁", "현준",
        "정민", "하빈", "재민", "승빈", "유찬", "지우", "동우", "건우", "찬우", "성준",
        "주호", "예찬", "원준", "하준", "준희", "도균", "지훈", "태준", "태경", "승찬"
    ]
    return random.choice(last_names) + random.choice(first_names)

def fetch_birth_years():
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT 고유번호, 생년 FROM prest_info")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {row[0]: row[1] for row in rows}

def determine_membership(year_of_birth):
    current_year = datetime.now().year
    age = current_year - year_of_birth
    if (1941 <= year_of_birth <= 1942 and age >= 70) or \
       (1943 <= year_of_birth <= 1944 and age >= 72) or \
       (1945 <= year_of_birth <= 1946 and age >= 74) or \
       (1947 <= year_of_birth <= 1948 and age >= 76) or \
       (1949 <= year_of_birth <= 1950 and age >= 78) or \
       (year_of_birth >= 1951 and age >= 80):
        return "원로회원"
    else:
        return "일반"


def create_registered_user_csv(review_file, output_file):
    
    # review.csv에서 userid 가져오기
    review_df = pd.read_csv(review_file)
    user_ids = review_df['userid'].unique().tolist()

    # prest_info 테이블에서 생년 정보 가져오기
    birth_years = fetch_birth_years()
    honorid_list = list(birth_years.keys())

    if len(user_ids) != len(honorid_list):
        raise ValueError("Number of user Id does not match")


    registered_users = []

    for i in range(len(honorid_list)):
        userid = user_ids[i]
        고유번호 = honorid_list[i]
        email = generate_email()
        password = generate_password()
        이름 = generate_korean_name()
        생년 = birth_years.get(고유번호, random.randint(1950, 2000))  # 생년이 없으면 랜덤으로 생성
        체력단련장_회원_구분 = determine_membership(생년)
        
        registered_users.append([userid, 고유번호, email, password, 이름, 생년, 체력단련장_회원_구분])
    
    registered_users_df = pd.DataFrame(registered_users, columns=["userid", "고유번호", "email", "password", "이름", "생년", "체력단련장회원구분"])
    registered_users_df.to_csv(output_file, index=False)
    print(f"Registered user data saved to {output_file}")


# 메인 코드
if __name__ == "__main__":
    review_file = 'data/additional_data/review.csv'
    output_file = 'data/additional_data/registered_users.csv'
    
    create_registered_user_csv(review_file, output_file)