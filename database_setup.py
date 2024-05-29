import psycopg2
import pandas as pd
from datetime import datetime


def connect_to_db():
    conn = psycopg2.connect(
        database="postgres", user='postgres', password='0911', host='localhost', port='5432'
    )
    return conn

def generate_create_table_query(df, table_name, unique_columns=None):
    column_types = {
        'int64': 'INTEGER',
        'float64': 'DECIMAL',
        'object': 'VARCHAR',
        'datetime64[ns]': 'DATE',
        'bool': 'BOOLEAN'
    }

    create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
    for column in df.columns:
        dtype = str(df[column].dtype)
        pg_type = column_types.get(dtype, 'VARCHAR')  # Default to VARCHAR if type not found
        create_table_query += f"    {column} {pg_type},\n"
    
    if unique_columns:
        if table_name == 'prest_info': pass
        else: 
            for col in unique_columns:
                create_table_query += f"    UNIQUE({col}),\n"
    create_table_query = create_table_query.rstrip(",\n") + "\n);"
    return create_table_query

def remove_duplicates_in_excel(file_path, subset_columns=None):
    df = pd.read_excel(file_path)
    if subset_columns:
        df = df.drop_duplicates(subset=subset_columns)
    return df

def drop_table_if_exists(table_name):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
    conn.commit()
    cur.close()
    conn.close()

def create_table_from_excel(file_path, table_name, subset_columns=None):
    df = remove_duplicates_in_excel(file_path, subset_columns)

    conn = connect_to_db()
    cur = conn.cursor()

    drop_table_if_exists(table_name)
    create_table_query = generate_create_table_query(df, table_name, subset_columns)
    print("Generated CREATE TABLE query:")
    print(create_table_query)
    cur.execute(create_table_query)
    
    if table_name == 'prest_info':
        cur.execute("""ALTER TABLE prest_info ADD PRIMARY KEY (고유번호);""")
    conn.commit()

    # 데이터 삽입
    for index, row in df.iterrows():
        columns = ', '.join(row.index)
        values = ', '.join(['%s'] * len(row))
        insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
        cur.execute(insert_query, tuple(row))
    conn.commit()
    cur.close()
    conn.close()

def create_additional_tables():
    conn = connect_to_db()
    cur = conn.cursor()

    additional_table_queries = [
        """
        CREATE TABLE IF NOT EXISTS registered_users (
            UserID VARCHAR PRIMARY KEY,
            고유번호 VARCHAR,
            Email VARCHAR,
            Password VARCHAR,
            이름 VARCHAR,
            생년 DATE,
            체력단련장회원구분 VARCHAR,
            FOREIGN KEY (고유번호) REFERENCES prest_info(고유번호)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS review (
            UserID VARCHAR,
            시설명 VARCHAR,
            평점 INTEGER,
            코멘트 TEXT,
            FOREIGN KEY (UserID) REFERENCES registered_users(UserID),
            FOREIGN KEY (시설명) REFERENCES facility_list(시설명)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS reservation (
            UserID VARCHAR,
            시설명 VARCHAR,
            예약일시 TIMESTAMP,
            FOREIGN KEY (UserID) REFERENCES registered_users(UserID),
            FOREIGN KEY (시설명) REFERENCES facility_list(시설명)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS rec_facility_tour_info (
            시설명 VARCHAR,
            지역명 VARCHAR,
            시설위치 VARCHAR,
            연락처 VARCHAR,
            FOREIGN KEY (시설명) REFERENCES rec_facility_info(휴양시설명)
        );
        """
    ]

    for query in additional_table_queries:
        cur.execute(query)
    
    conn.commit()
    cur.close()
    conn.close()


def determine_elder_member(year_of_birth):
    current_year = datetime.now().year
    age = current_year - year_of_birth

    if 1941 <= year_of_birth <= 1942 and age >= 70:
        return '원로회원'
    elif 1943 <= year_of_birth <= 1944 and age >= 72:
        return '원로회원'
    elif 1945 <= year_of_birth <= 1946 and age >= 74:
        return '원로회원'
    elif 1947 <= year_of_birth <= 1948 and age >= 76:
        return '원로회원'
    elif 1949 <= year_of_birth <= 1950 and age >= 78:
        return '원로회원'
    elif year_of_birth >= 1951 and age >= 80:
        return '원로회원'
    else:
        return '원로자격 없음'

def update_elder_status():
    conn = connect_to_db()
    cur = conn.cursor()

    # 병역명문가 정보의 생년(출생연도)을 가져옵니다.
    cur.execute("""
        SELECT r.UserID, b.생년
        FROM registered_users r
        JOIN prest_info b ON r.고유번호 = b.고유번호
    """)
    
    users = cur.fetchall()

    # 각 사용자의 원로회원 여부를 판단하고, 결과를 업데이트합니다.
    for user in users:
        user_id, year_of_birth = user
        elder_status = determine_elder_member(year_of_birth)

        # 결과를 출력하거나 필요시 업데이트 쿼리를 실행합니다.
        print(f"UserID: {user_id}, 생년: {year_of_birth}, 원로회원 자격: {elder_status}")

        # 체력단련장 회원구분 업데이트 예시 (체력단련장 회원구분이 원로회원 자격에 따라 변경됨)
        update_query = """
            UPDATE registered_users
            SET 체력단련장회원구분 = %s
            WHERE UserID = %s
        """
        cur.execute(update_query, (elder_status, user_id))
    
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    # setup database (create table)
    create_table_from_excel('data/project_data/1_prest_info.xlsx', 'prest_info', ['고유번호'])
    create_table_from_excel('data/project_data/2_facility_list.xlsx', 'facility_list', ['시설명'])
    create_table_from_excel('data/project_data/3_facility_status.xlsx', 'facility_status')
    create_table_from_excel('data/project_data/4_market_run_status.xlsx', 'market_run_status')
    create_table_from_excel('data/project_data/5_rec_facility_info.xlsx', 'rec_facility_info', ['휴양시설명'])
    create_table_from_excel('data/project_data/6_event_timetable.xlsx', 'event_timetable')
    create_table_from_excel('data/project_data/7_px_info.xlsx', 'px_info')
    create_table_from_excel('data/project_data/8_gym_status.xlsx', 'gym_status')
    create_table_from_excel('data/project_data/9_co_op_list.xlsx', 'co_op_list', ['시설명'])
    create_table_from_excel('data/project_data/10_movie_status.xlsx', 'movie_status')
    create_table_from_excel('data/project_data/11_jurisdiction.xlsx', 'jurisdiction')

    create_additional_tables()
    update_elder_status()

