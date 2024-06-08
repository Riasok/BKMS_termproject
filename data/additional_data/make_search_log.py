import pandas as pd
import psycopg2
import random
from datetime import datetime, timedelta

def connect_to_db():
    return psycopg2.connect(
        database="postgres", user='postgres', password='0911', host='localhost', port='5432'
    )

def fetch_data_from_db(query):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def generate_random_datetime(start, end):
    return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))

users = fetch_data_from_db("SELECT userid FROM registered_users")
facilities = fetch_data_from_db("SELECT 시설명 FROM facility_list")

user_ids = [user[0] for user in users]
facility_names = [facility[0] for facility in facilities]
search_filters = ["시설명", "업종", "지역"]

# 무작위 데이터 생성
random.seed(42)
start_date = datetime(2023, 1, 1)
end_date = datetime(2024, 6, 1)

data = []
for _ in range(1000):  # 원하는 데이터 양
    user_id = random.choice(user_ids)
    facility_name = random.choice(facility_names)
    search_filter = random.choice(search_filters)
    search_time = generate_random_datetime(start_date, end_date)
    data.append((user_id, facility_name, search_filter, search_time))

search_logs_df = pd.DataFrame(data, columns=["user_id", "search_query", "search_filter", "search_time"])

# CSV 파일로 저장
search_logs_df = search_logs_df.sort_values(by="search_time").reset_index(drop=True)

search_logs_df.to_csv('data/additional_data/search_logs.csv', index=False)

print("Data saved to search_logs.csv successfully.")