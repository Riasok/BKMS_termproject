import psycopg2
from psycopg2 import sql

class myDB:
    def __init_(self,database = 'postgres', user = 'postgres', password = 'postgres', host = 'localhost', port = '5432'):
        self.database = 'postgres'
        self.user = 'postgres'
        self.password = 'postgres'
        self.host = 'localhost'
        self.port = '5432'

        self.conn = psycopg2.connect(
            database = self.database,
            user = self.user,
            password = self.password,
            host = self.host,
            port = self.port,
        )
        self.conn.autocommit = False
        self.cursor = self.conn.cursor()

    def refresh_cur(self):
        self.conn = psycopg2.connect(
            database = self.database,
            user = self.user,
            password = self.password,
            host = self.host,
            port = self.port,
        )
        self.conn.autocommit = False
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    #Query 1 지역별 검색
    def search_by_region(self, region):
        """
        지역에 따른 시설을 반환하는 쿼리
        Args:
            region : 지역
        """
        self.query = sql.SQL(f"SELECT * FROM facility_list where 지역 LIKE '%{region}%';")
        self.cursor.execute(self.query)
        self.result = self.cursor.fetchall()
        print(self.result)
        self.conn.commit()
    
    #로그인 기능
    def login(self, userID, password):
        self.cursor.execute(f"SELECT * FROM users where USERID = '{userID}'")
        self.result = self.cursor.fetchone()
        if self.result is not None:
            if self.result[1] == password:
                return True
        return False

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
        self.cursor.execute(f"SELECT 1 FROM users WHERE HONORID = {honorID}''")
        if self.cursor.fetchone() is not None:
            return False
        
        self.cursor.execute("SELECT 1 FROM users WHERE USERID= %s", (userID,))
        if self.cursor.fetchone() is not None:
            return False
        
        self.query = sql.SQL("""
                            INSERT INTO Users (userID, honorID, email, password, name)
                            VALUES(%d, %d, %s, %s, %s)
                             """)
        self.cursor.execute(f"INSERT INTO users (USERID, HONORID, EMAIL, PASSWORD, NAME)
                            VALUES('{userID}','{honorID}','{email}','{password}','{name}')")
        self.conn.commit()
        return True
    
    #Query 5 예약가능한 시설인 경우 예약 시스템
    def reservation(self, UserID, Date, facility_ID):
        """
        시설을 예약하는 쿼리, 예약가능하거나, 시간이 겹칠 시 예약 불가능!
        Args:
            userID : 유저의 ID
            Date : 날짜
            facility_ID: 시설 이름
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

    #Query 7 : 검색수 count & ranking
    def search_rank(self):
        self.cursor()

    #Query 9 : 평점 ranking
    def grade_rank(self):
        """
        평점에 따른 top 10 ranking 리턴
        Args: None
        """
        self.query = sql.SQL("""
                             SELECT facilityID, avg(Rating) as avgR
                             FROM Reviews
                             GROUP BY facility_ID
                             ORDER BY avgR DESC
                             LIMIT 10
                             """)
        self.cursor.execute(self.query)
        self.results = self.cursor.fetchall()
        for r in self.results:
            print(f"Facility : {r[0]}, Average Rating : {r[1]}")

    #Query 11 : 시설 조회 시 같은지역 관광지 추천
    def recommendation(self, facility):
        """
        시설에 따른 같은 지역 관광지 추천

        """
        self.cursor()
    
