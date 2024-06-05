import psycopg2
from psycopg2 import sql
import pandas as pd

def connect_to_db():
    conn = psycopg2.connect(
        database="postgres", user='postgres', password='0911', host='localhost', port='5432'
    )
    return conn

##### 로그인
def fetch_users():
    conn = connect_to_db()
    query = "SELECT userid, password, email, 이름 FROM registered_users"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


class myDB:
    def __init__(self):
        self.conn = connect_to_db()
        self.conn.autocommit = True
        self.cursor = self.conn.cursor()

    def refresh_cur(self):
        self.conn = connect_to_db()
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    ##### 검색
    def search_by_name(self, name):
        """
        시설명에 따른 시설을 반환하는 쿼리
        """
        query = sql.SQL("SELECT * FROM facility_list WHERE 시설명 = %s;")
        self.cursor.execute(query, (name,))
        result = self.cursor.fetchone()
        columns = [desc[0] for desc in self.cursor.description]
        return dict(zip(columns, result))

    def log_search(self, facility_id):
        """
        검색 로그 기록 함수
        """
        query = sql.SQL("INSERT INTO searchlogs (시설명) VALUES (%s)")
        self.cursor.execute(query, (facility_id,))
        self.conn.commit()

    def search_by_region(self, region):
        """
        지역에 따른 시설을 반환하는 쿼리 (Query 1)
        """
        query = sql.SQL("SELECT * FROM facility_list WHERE 지역 = %s;")
        self.cursor.execute(query, (region,))
        result = self.cursor.fetchall()
        columns = [desc[0] for desc in self.cursor.description]
        return pd.DataFrame(result, columns=columns)


    ##### 집계
    def search_count_and_rank(self):
        """
        검색 수 count 및 ranking (Query 8)
        """
        query = sql.SQL("""
                        SELECT f.시설명, COUNT(s.search_id) as 검색수
                        FROM searchlogs s
                        JOIN facility_list f ON s.시설명 = f.시설명
                        GROUP BY f.시설명
                        ORDER BY 검색수 DESC
                        """)
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        columns = [desc[0] for desc in self.cursor.description]
        return pd.DataFrame(result, columns=columns)

    def view_count_and_rank(self):
        """
        조회 수 count 및 ranking (Query 8)
        """
        query = sql.SQL("""
                        SELECT facilityID, COUNT(*) as view_count
                        FROM ViewLogs
                        GROUP BY facilityID
                        ORDER BY view_count DESC
                        """)
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        for r in results:
            print(f"Facility: {r[0]}, View Count: {r[1]}")

    def grade_rank(self):
        """
        평점에 따른 top 10 ranking 리턴 (Query 9)      * 리뷰 5개 이상인 시설들 한정
        """
        query = sql.SQL("""
                        SELECT 시설명, ROUND(avg(평점),2) as 평균평점
                        FROM review
                        GROUP BY 시설명
                        HAVING COUNT(*) > 5
                        ORDER BY 평균평점 DESC
                        LIMIT 10
                        """)
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        columns = [desc[0] for desc in self.cursor.description]
        return pd.DataFrame(result, columns=columns)


    ##### 예약
    def reservation(self, UserID, Date, facility_ID):
        """
        시설을 예약하는 쿼리 (Query 5)      * 시간이 겹칠 시 예약 불가능
        """
        self.cursor.execute("SELECT 1 FROM facility WHERE 시설명 = %s AND res = T", (facility_ID,))
        if self.cursor.fetchone() is not None:
            raise ValueError("It is not a reservable facuiility")

        self.cursor.execute("SELECT 1 FROM Reservation WHERE 시설명 = %s AND 예약일시 = %s", (facility_ID, Date))
        if self.cursor.fetchone() is not None:
            raise ValueError("It is already reserved")
        
        self.cursor.execute("SELECT COUNT(*) FROM reserves")
        self.rID = self.cursor.fetchone()[0]

        self.query = sql.SQL("""
                            INSERT INTO Reserves (reserveID, userID, 예약일시, 시설명)
                            VALUES(%d, %d, %s, %s, %s)
                             """)
        self.cursor.execute(self.query, (self.rID, UserID. Date, facility_ID,))
        self.conn.commit()
        print("Reservation Added Succefully !!")




    #Query 2 시설과 해당기관에 대한 리뷰 조인
    def facility_reviews(self):
        query = sql.SQL("""
                        SELECT f.시설명, r.평점, r.코멘트
                        FROM facility_list f
                        JOIN review r ON f.시설명 = r.시설명
                        """)
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        for r in results:
            print(f"시설명: {r[0]}, 평점: {r[1]}, 코멘트: {r[2]}")
    
    #Query 3 회원가입 기능
    def sign_in(self, userID, honorID, email, password, name):
        """
        계정이 존재하지 않으면, honorID를 바탕으로 새로운 계정을 만드는 쿼리
        Args:
            userID : 유저의 ID
            honorID : 유저의 honorID
            email : 유저의 email
            password : 유저의 비밀번호
            name : 유저의 이름
        """
        self.cursor.execute("SELECT 1 FROM Users WHERE HONORID = %d", (honorID,))
        if self.cursor.fetchone() is not None:
            raise ValueError("ERROR HonorID {honorID} alread exists!!")
        
        self.cursor.execute("SELECT 1 FROM Users WHERE USERID= %s", (userID,))
        if self.cursor.fetchone() is not None:
            raise ValueError("Error Already exsisting ID")
        
        self.query = sql.SQL("""
                            INSERT INTO Users (userID, honorID, email, password, name)
                            VALUES(%d, %d, %s, %s, %s)
                             """)
        self.cursor.execute(self.query, (userID, honorID, email. password, name,))
        self.conn.commit()
        print("User Added Succefully !!")

        ##except error as e : print (e)

    #Query 4 명문가 및 그에 속하는 회원 정보 조회 (view)
    def create_view(self):
        query = sql.SQL("""
                        CREATE VIEW honor_members AS
                        SELECT u.고유번호, u.userid, u.이름, u.생년, u.email
                        FROM prest_info p
                        JOIN registered_users u ON p.고유번호 = u.고유번호
                        """)
        self.cursor.execute(query)
        self.conn.commit()
        print("View created successfully")
    
   
    #Query 6 Data Integrity
    def transaction_example(self):
        try:
            self.conn.autocommit = False
            self.cursor.execute("BEGIN;")
            # Example transaction for sign up
            self.sign_in("user123", "honor456", "user123@example.com", "password", "User Name")
            # Example transaction for making a reservation
            self.reservation("user123", "2024-06-05", "facility789")
            self.conn.commit()
            print("Transaction completed successfully")
        except Exception as e:
            self.conn.rollback()
            print(f"Transaction failed: {e}")

    #Query 7 : 검색수 count & ranking
    def search_rank(self):
        self.cursor()

   

    #Query 10 Data Cube: 복지 시설 리뷰의 평균 평점, 리뷰 수 등 집계
    def data_cube(self):
        query = sql.SQL("""
                        SELECT 시설명, AVG(평점) as avgRating, COUNT(*) as reviewCount
                        FROM review
                        GROUP BY CUBE(시설명)
                        """)
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        for r in results:
            print(f"시설명: {r[0]}, 평점 평균: {r[1]}, 리뷰 개수: {r[2]}")

    #Query 11 : 시설 조회 시 같은지역 관광지 추천
    def recommendation(self, facility):
        """
        시설에 따른 같은 지역 관광지 추천

        """
        self.cursor()
    
    # Query 12: Clustering - 병역 명문가 예우시설 사용 패턴 분석 (유사한 사용 패턴 회원들 그룹화 -> 맞춤형 서비스 제공)
    def clustering(self):
        # Assuming we have a function `perform_clustering` that clusters data
        query = sql.SQL("SELECT userID, usage_pattern FROM UserPatterns")
        self.cursor.execute(query)
        data = self.cursor.fetchall()
        # clusters = perform_clustering(data)
        # print(clusters)
        print("Clustering function to be implemented")