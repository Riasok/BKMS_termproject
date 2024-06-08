import pandas as pd
import random
from datetime import datetime, timedelta

# 파일 경로
registered_users_path = 'data/additional_data/registered_users.csv'
facility_names_path = 'facility_name.csv'
output_path = 'data/additional_data/reservation.csv'

# 사용자 및 시설명 데이터 로드
users_df = pd.read_csv(registered_users_path)
facility_df = pd.read_csv(facility_names_path)

# 사용자 ID 및 시설명 리스트
user_ids = users_df['userid'].tolist()
facility_names = facility_df['시설명'].tolist()

# 예약 정보 생성
reservations = []
num_reservations = 315  # 생성할 예약 수

for _ in range(num_reservations):
    userid = random.choice(user_ids)
    facility_name = random.choice(facility_names)
    
    # 오늘 이후 2024년 내의 랜덤 예약일시 생성
    today = datetime.now()
    end_date = datetime(2024, 12, 31)
    delta_days = (end_date - today).days
    random_days = random.randint(1, delta_days)
    reservation_date = today + timedelta(days=random_days)
    reservation_date_str = reservation_date.strftime('%Y-%m-%d')

    reservations.append({
        'userid': userid,
        '시설명': facility_name,
        '예약일시': reservation_date_str,
        '예약가능': 9
    })

# DataFrame으로 변환 및 CSV 저장
reservations_df = pd.DataFrame(reservations)
reservations_df.to_csv(output_path, index=False)

print(f"{num_reservations}개의 예약 정보가 '{output_path}'에 저장되었습니다.")
