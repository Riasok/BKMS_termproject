import psycopg2
from psycopg2 import sql
import pandas as pd
from datetime import datetime
import random

def connect_to_db():
    conn = psycopg2.connect(
        database="postgres", user='postgres', password='postgres', host='localhost', port='5432'
    )
    return conn

def fetch_users():
    '''
    Frontend 시작 시 등록된 회원 정보 보내기
    '''
    conn = connect_to_db()
    query = "SELECT userid, password, email,고유번호, 이름 FROM registered_users"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def log_search(user_id, search_query, search_filter):
    '''
    검색 기록 저장
    '''
    conn = connect_to_db()
    cursor = conn.cursor()
    query = """
    INSERT INTO search_logs (user_id, search_query, search_filter, search_time)
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query, (user_id, search_query, search_filter, datetime.now()))
    conn.commit()
    conn.close()

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


    ##### 회원 가입 #####
    def register_user(self, username, password, email, name, honorID):
        '''
        새로운 회원 등록 (Query 3)
        '''
        self.cursor.execute("""INSERT INTO registered_users (userid, 고유번호, email, password, 이름)
                               VALUES (%s, %s, %s, %s, %s)""", (username, honorID, email, password, name))
        self.conn.commit()

    def fetch_user_by_id(self, userid):
        '''
        회원가입 시 db에 정보 반영되었는지 확인
        '''
        self.cursor.execute("SELECT * FROM registered_users WHERE userid = %s", (userid,))
        return self.cursor.fetchone()

    ## 개인정보 수정 ##
    def update(self, _userid, _password, _email, _name, _h_id):
        self.cursor.execute("""
                    UPDATE registered_users 
                    SET userid = %s, password = %s, email = %s, 이름 = %s
                    WHERE 고유번호 = %s""", (_userid, _password, _email, _name, _h_id,))

    ##### 검색 #####
    def search_by_name(self, name):
        '''
        시설명에 따른 시설 반환
        '''
        
        query = sql.SQL("SELECT * FROM facility_list WHERE 시설명 = %s;")
        self.cursor.execute(query, (name,))
        result = self.cursor.fetchone()
        columns = [desc[0] for desc in self.cursor.description]
        _return = dict(zip(columns, result))
        if _return:
            return _return, 0
        
        #협약기관
        query = sql.SQL("SELECT * FROM co_op_list WHERE 시설명 = %s;")
        self.cursor.execute(query, (name,))
        result = self.cursor.fetchone()
        columns = [desc[0] for desc in self.cursor.description]
        _return = dict(zip(columns, result))
        return _return, 1


    def log_search(self, facility_id):
        '''
        검색 수 집계를 위해 기록
        '''
        query = sql.SQL("INSERT INTO search_logs (search_query) VALUES (%s)")
        self.cursor.execute(query, (facility_id,))
        self.conn.commit()

    def search_by_region(self, region, isfree, isdiscount):
        '''
        지역에 따른 시설을 반환 (Query 1)
        '''
        region = "%{}%".format(region)
        if isfree and isdiscount:
            query1 = sql.SQL("SELECT * FROM facility_list WHERE 지역 LIKE %s;")
            query2 = sql.SQL("SELECT * FROM co_op_list WHERE 지역 LIKE %s;")
        elif isfree:
            query1 = sql.SQL("SELECT * FROM facility_list WHERE 지역 LIKE %s AND 면제할인 = '할인';")
            query2 = sql.SQL("SELECT * FROM co_op_list WHERE 지역 LIKE %s AND 우대내용 = '할인';")
        else:
            query1 = sql.SQL("SELECT * FROM facility_list WHERE 지역 LIKE %s AND 면제할인 = '면제';")
            query2 = sql.SQL("SELECT * FROM co_op_list WHERE 지역 LIKE %s AND 우대내용 = '할인';")

        self.cursor.execute(query1, (region,))
        result = self.cursor.fetchall()
        columns = [desc[0] for desc in self.cursor.description]
        result1 = pd.DataFrame(result,columns=columns)

        self.cursor.execute(query2, (region,))
        result = self.cursor.fetchall()
        columns = [desc[0] for desc in self.cursor.description]
        result2 = pd.DataFrame(result,columns=columns)

        return result1, result2

    def search_by_type(self, type, isfree, isdiscount):
        '''
        업종에 따른 시설을 반환
        '''
        if isfree and isdiscount:
            query1 = sql.SQL("SELECT * FROM facility_list WHERE 업종 = %s;")
            query2 = sql.SQL("SELECT * FROM co_op_list WHERE 업종 = %s;")
        elif isfree:
            query1 = sql.SQL("SELECT * FROM facility_list WHERE 업종 = %s AND 면제할인 = '할인';")
            query2 = sql.SQL("SELECT * FROM co_op_list WHERE 업종 = %s AND 우대내용 = '할인';")
        else:
            query1 = sql.SQL("SELECT * FROM facility_list WHERE 업종 = %s AND 면제할인 = '면제';")
            query2 = sql.SQL("SELECT * FROM co_op_list WHERE 업종 = %s AND 우대내용 = '면제';")
        
        self.cursor.execute(query1, (type,))
        result = self.cursor.fetchall()
        columns = [desc[0] for desc in self.cursor.description]
        result1 = pd.DataFrame(result,columns=columns)

        self.cursor.execute(query2, (type,))
        result = self.cursor.fetchall()
        columns = [desc[0] for desc in self.cursor.description]
        result2 = pd.DataFrame(result,columns=columns)

        return result1, result2
    


    def fac_reviews(self, facilityID):
        '''
        검색한 시설 리뷰 보여주기
        '''
        query = sql.SQL("SELECT * FROM review WHERE 시설명 = %s")
        self.cursor.execute(query, (facilityID,))
        result = self.cursor.fetchall()
        columns = [desc[0] for desc in self.cursor.description]
        return pd.DataFrame(result, columns=columns)


    ##### 집계 #####
    def search_count_and_rank(self):
        '''
        검색 수 count 및 ranking (Query 8)
        '''
        query = sql.SQL("""
                        SELECT f.시설명, COUNT(*) as 검색수
                        FROM search_logs s
                        JOIN facility_list f ON s.search_query = f.시설명
                        GROUP BY f.시설명
                        ORDER BY 검색수 DESC
                        """)
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        columns = [desc[0] for desc in self.cursor.description]
        return pd.DataFrame(result, columns=columns)
    
    def grade_rank(self):
        '''
        평점에 따른 TOP 10 ranking 리턴 (Query 9)   * 리뷰 5개 이상인 시설들 한정
        '''
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


    ##### 예약 #####
    def reservation(self, userid, date, facility_ID):
        '''
        시설 예약
        '''
        self.cursor.execute("SELECT 1 FROM facility_list WHERE 시설명 = %s AND 예약가능 > 0", (facility_ID,))
        if self.cursor.fetchone() is None:
            raise ValueError("It is not a reservable facility or no availability")

        self.cursor.execute("SELECT 1 FROM reservation WHERE 시설명 = %s AND 예약일시 = %s", (facility_ID, date))
        if self.cursor.fetchone() is not None:
            raise ValueError("It is already reserved")
    
        self.query = sql.SQL("""
                            INSERT INTO reservation (userID, 시설명, 예약일시)
                            VALUES(%s, %s, %s)
                             """)
        self.cursor.execute(self.query, (userid, facility_ID, date))
        self.cursor.execute("UPDATE facility_list SET 예약가능 = 예약가능 - 1 WHERE 시설명 = %s", (facility_ID,))

        self.conn.commit()
        print("Reservation Added Succefully !!")

    def update_facility_list(self):
        '''
        예약 정보를 바탕으로 예약 가능한 수 업데이트
        '''
        temp_table_query = """
            CREATE TEMP TABLE temp_reservation_count AS
            SELECT 시설명, COUNT(*) AS 예약횟수
            FROM reservation
            GROUP BY 시설명
        """
        self.cursor.execute(temp_table_query)

        update_query = """
            UPDATE facility_list f
            SET 예약가능 = 10 - COALESCE(t.예약횟수, 0)
            FROM temp_reservation_count t
            WHERE f.시설명 = t.시설명
        """
        self.cursor.execute(update_query)

        drop_temp_table_query = "DROP TABLE IF EXISTS temp_reservation_count"
        self.cursor.execute(drop_temp_table_query)

        self.conn.commit()
        self.cursor.close()
        self.conn.close()
        print("facility_list table updated successfully")
    
    def fetch_user_reservations(self, userid):
        '''
        사용자의 예약 정보 불러오기
        '''
        query = sql.SQL("""
                        SELECT * FROM reservation
                        WHERE userid = %s AND 예약일시 > %s
                        ORDER BY 예약일시
                        """)
        cur_date = datetime.now().date()
        cur_date = cur_date.strftime('%Y-%m-%d')
        self.cursor.execute(query, (userid,cur_date,))
        results = self.cursor.fetchall()
        columns = [desc[0] for desc in self.cursor.description]
        return pd.DataFrame(results, columns=columns)

    def facility_exists(self, facility_name):
        '''
        시설명이 존재하는지 확인
        '''
        self.cursor.execute("SELECT COUNT(*) FROM facility_list WHERE 시설명 = %s", (facility_name,))
        exists = self.cursor.fetchone()[0] > 0
        return exists

    
    def write_review(self, facilityID, userID, stars, review):
        '''
        리뷰 작성
        '''
        self.cursor.execute("SELECT COUNT(*) FROM registered_users WHERE userid = %s", (userID,))
        if self.cursor.fetchone()[0] == 0:
            raise ValueError(f"User ID '{userID}' does not exist in registered_users")

        query = sql.SQL("INSERT INTO review (시설명, userid, 평점, 코멘트) VALUES (%s, %s, %s, %s)")
        self.cursor.execute(query, (facilityID, userID, stars, review,))
        

    def fetch_honor_members(self):
        '''
        병역명문가 회원 정보
        '''
        self.cursor.execute("""
                            SELECT * FROM prest_info
                            """)
        columns = [desc[0] for desc in self.cursor.description]
        return pd.DataFrame(self.cursor.fetchall(), columns=columns)

    def get_random_facility(self):
        '''
        랜덤으로 시설 추천
        '''
        query = "SELECT 시설명 FROM facility_list"
        self.cursor.execute(query)
        facilities = self.cursor.fetchall()
        if facilities:
            return random.choice(facilities)[0]
        return None
    
    ##query 11
    #주변 관광지 추천
    def region_recommend(self, region):
        query = sql.SQL("SELECT * FROM recommend_place WHERE 지역명 LIKE %s")
        self.cursor.execute(query, (f"%{region}%",))
        recommend = self.cursor.fetchall()
        rec_facilities = pd.DataFrame(recommend, columns=[desc[0] for desc in self.cursor.description])
        return rec_facilities

    #주변 군 복지시설 휴양 정보
    def near_recommend(self, region):
        query = sql.SQL("SELECT * FROM rec_facility_info WHERE 위치 LIKE %s")
        self.cursor.execute(query, (f"%{region}%",))
        recommend = self.cursor.fetchall()
        rec_facilities = pd.DataFrame(recommend, columns=[desc[0] for desc in self.cursor.description])
        return rec_facilities

    # #Query 2 시설과 해당기관에 대한 리뷰 조인
    # def facility_reviews(self):
    #     query = sql.SQL("""
    #                     SELECT f.시설명, r.평점, r.코멘트
    #                     FROM facility_list f
    #                     JOIN review r ON f.시설명 = r.시설명
    #                     """)
    #     self.cursor.execute(query)
    #     results = self.cursor.fetchall()
    #     for r in results:
    #         print(f"시설명: {r[0]}, 평점: {r[1]}, 코멘트: {r[2]}")
    
    # #Query 3 회원가입 기능
    # def sign_in(self, userID, honorID, email, password, name):
    #     """
    #     계정이 존재하지 않으면, honorID를 바탕으로 새로운 계정을 만드는 쿼리
    #     Args:
    #         userID : 유저의 ID
    #         honorID : 유저의 honorID
    #         email : 유저의 email
    #         password : 유저의 비밀번호
    #         name : 유저의 이름
    #     """
    #     self.cursor.execute("SELECT 1 FROM Users WHERE HONORID = %d", (honorID,))
    #     if self.cursor.fetchone() is not None:
    #         raise ValueError("ERROR HonorID {honorID} alread exists!!")
        
    #     self.cursor.execute("SELECT 1 FROM Users WHERE USERID= %s", (userID,))
    #     if self.cursor.fetchone() is not None:
    #         raise ValueError("Error Already exsisting ID")
        
    #     self.query = sql.SQL("""
    #                         INSERT INTO Users (userID, honorID, email, password, name)
    #                         VALUES(%d, %d, %s, %s, %s)
    #                          """)
    #     self.cursor.execute(self.query, (userID, honorID, email. password, name,))
    #     self.conn.commit()
    #     print("User Added Succefully !!")

    #     ##except error as e : print (e)
    

    # #Query 10 Data Cube: 복지 시설 리뷰의 평균 평점, 리뷰 수 등 집계
    # def data_cube(self):
    #     query = sql.SQL("""
    #                     SELECT 시설명, AVG(평점) as avgRating, COUNT(*) as reviewCount
    #                     FROM review
    #                     GROUP BY CUBE(시설명)
    #                     """)
    #     self.cursor.execute(query)
    #     results = self.cursor.fetchall()
    #     for r in results:
    #         print(f"시설명: {r[0]}, 평점 평균: {r[1]}, 리뷰 개수: {r[2]}")

    

    
   
