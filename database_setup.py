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

def remove_duplicates_in_file(file_path, subset_columns=None):
    if file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path)
    elif file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        raise ValueError("Unsupported file format. Please use .xlsx or .csv files.")
    
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
    df = remove_duplicates_in_file(file_path, subset_columns)

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
        """,
        """
        CREATE TABLE IF NOT EXISTS searchlogs (
        search_id SERIAL PRIMARY KEY,
        시설명 VARCHAR,
        search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        ALTER TABLE registered_users
        ADD CONSTRAINT pk_userid PRIMARY KEY (userid);
        """,
        """
        ALTER TABLE IF EXISTS review
        ADD CONSTRAINT fk_userid
        FOREIGN KEY (userid) REFERENCES registered_users(userid),
        ADD CONSTRAINT fk_facility_name
        FOREIGN KEY (시설명) REFERENCES facility_list(시설명);
        """,
        """
        ALTER TABLE IF EXISTS facility_list
        ADD COLUMN 예약가능 INTEGER
        DEFAULT 10
        """,
        """
        ALTER TABLE IF EXISTS reservation
        ADD CONSTRAINT fk_userid
        FOREIGN KEY (userid) REFERENCES registered_users(userid),
        ADD CONSTRAINT fk_facility_name
        FOREIGN KEY (시설명) REFERENCES facility_list(시설명);
        """
    ]

    for query in additional_table_queries:
        cur.execute(query)
    
    conn.commit()
    cur.close()
    conn.close()

def create_view():
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("""
                CREATE VIEW honor_members AS
                SELECT u.고유번호, u.userid, u.이름, u.생년, u.email
                FROM prest_info p
                JOIN registered_users u ON p.고유번호 = u.고유번호
                """)
    conn.commit()
    cur.close()
    conn.close()

def update_facility_list():
    conn = connect_to_db()
    cur = conn.cursor()

    temp_table_query = """
        CREATE TEMP TABLE temp_reservation_count AS
        SELECT 시설명, COUNT(*) AS 예약횟수
        FROM reservation
        GROUP BY 시설명
    """
    cur.execute(temp_table_query)

    update_query = """
        UPDATE facility_list f
        SET 예약가능 = 10 - COALESCE(t.예약횟수, 0)
        FROM temp_reservation_count t
        WHERE f.시설명 = t.시설명
    """
    cur.execute(update_query)

    drop_temp_table_query = "DROP TABLE IF EXISTS temp_reservation_count"
    cur.execute(drop_temp_table_query)

    conn.commit()
    cur.close()
    conn.close()
    print("facility_list table updated successfully")


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
    
    create_table_from_excel('data/additional_data/review.csv', 'review')
    create_table_from_excel('data/additional_data/registered_users.csv', 'registered_users')
    create_table_from_excel('data/additional_data/reservation.csv', 'reservation')

    create_additional_tables()
    create_view()
    update_facility_list()

    

