import psycopg2

def connect_to_db():
    conn = psycopg2.connect(
        database="your-postgres", user='your-postgres', password='your-password', host='localhost', port='your-port'
    )
    return conn

def check_table_exists(table_name):
    '''
    테이블이 존재하는지 확인
    '''
    conn = connect_to_db()
    cur = conn.cursor()
    
    cur.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = %s
    );
    """, (table_name,))
    
    exists = cur.fetchone()[0]
    cur.close()
    conn.close()
    return exists

def describe_table(table_name):
    '''
    테이블 구조 확인
    '''
    conn = connect_to_db()
    cur = conn.cursor()
    
    cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = %s;
    """, (table_name,))
    
    columns = cur.fetchall()
    cur.close()
    conn.close()
    return columns

def fetch_table_data(table_name, limit=5):
    '''
    테이블 데이터 확인 (5행 출력)
    '''
    conn = connect_to_db()
    cur = conn.cursor()
    
    cur.execute(f"SELECT * FROM {table_name} LIMIT {limit};")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_primary_keys(table_name):
    '''
    테이블 primary key 확인
    '''
    conn = connect_to_db()
    cur = conn.cursor()
    
    cur.execute("""
    SELECT kcu.column_name
    FROM information_schema.table_constraints tc 
    JOIN information_schema.key_column_usage kcu 
    ON tc.constraint_name = kcu.constraint_name
    WHERE tc.table_name = %s AND tc.constraint_type = 'PRIMARY KEY';
    """, (table_name,))
    
    primary_keys = cur.fetchall()
    cur.close()
    conn.close()
    return [pk[0] for pk in primary_keys]

def get_unique_constraints(table_name):
    '''
    테이블 unique constraints 확인
    '''
    conn = connect_to_db()
    cur = conn.cursor()
    
    cur.execute("""
    SELECT kcu.column_name
    FROM information_schema.table_constraints tc 
    JOIN information_schema.key_column_usage kcu 
    ON tc.constraint_name = kcu.constraint_name
    WHERE tc.table_name = %s AND tc.constraint_type = 'UNIQUE';
    """, (table_name,))
    
    unique_constraints = cur.fetchall()
    cur.close()
    conn.close()
    return [uc[0] for uc in unique_constraints]


if __name__ == "__main__":
    table_name = 'co_op_list'       # 확인하고 싶은 테이블명 입력
    if check_table_exists(table_name):
        print(f"Table '{table_name}' exists.")
        
        columns = describe_table(table_name)
        print("\nTable structure:")
        for column in columns:
            print(f"{column[0]}: {column[1]}")
        
        primary_keys = get_primary_keys(table_name)
        print("\nPrimary keys:")
        for pk in primary_keys:
            print(pk)
        
        unique_constraints = get_unique_constraints(table_name)
        print("\nUnique constraints:")
        for uc in unique_constraints:
            print(uc)
        
        print("\nTop 5 rows in the table:")
        rows = fetch_table_data(table_name, 5)
        for row in rows:
            print(row)
    else:
        print(f"Table '{table_name}' does not exist.")



