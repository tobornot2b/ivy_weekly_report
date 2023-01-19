import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
# import binascii   # 한글 변환에 필요한 라이브러리
import sys
import sqlite3
import os.path
from datetime import datetime, date, timedelta

# SQLITE3 DB 파일명
db_file = 'daliy_order.db'


# 지난주 월요일 - 금요일 구하기
def get_last_week() -> str:
    diff_1: int = (date.today().weekday() - 0) % 7 # 0:월요일, 1:화요일, 2:수요일, 3:목요일, 4:금요일, 5:토요일, 6:일요일
    diff_2: int = (date.today().weekday() - 4) % 7 # 0:월요일, 1:화요일, 2:수요일, 3:목요일, 4:금요일, 5:토요일, 6:일요일
    
    last_mon: str = (date.today() - timedelta(days=diff_1 + 7)).strftime("%Y/%m/%d") # 대쉬를 뺀 형식으로 변경
    last_fri: str = (date.today() - timedelta(days=diff_2)).strftime("%Y/%m/%d") # 대쉬를 뺀 형식으로 변경
    
    return last_mon, last_fri


# 이번주 월요일 - 금요일 구하기
def get_this_week() -> str:
    diff_1: int = (date.today().weekday() - 0) % 7 # 0:월요일, 1:화요일, 2:수요일, 3:목요일, 4:금요일, 5:토요일, 6:일요일
    diff_2: int = (date.today().weekday() - 4) % 7 # 0:월요일, 1:화요일, 2:수요일, 3:목요일, 4:금요일, 5:토요일, 6:일요일
    
    this_mon: str = (date.today() - timedelta(days=diff_1)).strftime("%Y/%m/%d") # 대쉬를 뺀 형식으로 변경
    this_fri: str = (date.today() - timedelta(days=diff_2 - 7)).strftime("%Y/%m/%d") # 대쉬를 뺀 형식으로 변경
    
    return this_mon, this_fri

# # 유저정보 가져오기
# def select_user(db_file_name: str):
#     BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # 현재 디렉토리 경로
#     db_path = os.path.join(BASE_DIR, db_file_name) # 경로 + DB파일명

#     conn = sqlite3.connect(db_path) # conn 객체 생성, isolation_level = None (자동 commit)
#     c = conn.cursor() # 커서 생성

#     c.execute(f"SELECT username, name, hash_pw FROM STREAMLIT_USER ")
#     rows = c.fetchall()
#     conn.close()

#     return rows


# 정규식 특문 제거
def clean_text(inputString: str) -> str:
    # text_rmv = re.sub('[-=+,#/\?:^.@*\"※~ㆍ!』‘|\(\)\[\]`\'…》\”\“\’·]', ' ', inputString)
    text_rmv = inputString.rstrip('\r\n')
    # text_rmv = re.sub('/^[ㄱ-ㅎ|가-힣|a-z|A-Z|0-9|]+$/', '', str(inputString))

    return str(text_rmv)


# SQLITE3 DB 연결
def connect_sqlite3(db_file_name: str, sql_text: str) -> pd.DataFrame:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # 현재 디렉토리 경로
    db_path = os.path.join(BASE_DIR, db_file_name) # 경로 + DB파일명

    conn = sqlite3.connect(db_path) # conn 객체 생성
    c = conn.cursor() # 커서 생성

    df = pd.read_sql(sql_text, conn)
    conn.close()

    return df


# SQLITE3 DB 에 insert
def insert_text(db_file_name: str, week: int, team: str, text: str, column: str):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # 현재 디렉토리 경로
    db_path = os.path.join(BASE_DIR, db_file_name) # 경로 + DB파일명

    conn = sqlite3.connect(db_path, isolation_level = None) # conn 객체 생성, isolation_level = None (자동 commit)
    c = conn.cursor() # 커서 생성

    # text = clean_text(text)

    c.execute(f"INSERT OR REPLACE INTO WEEKLY_REPORT (isrt_week, team, {column}) VALUES (?,?,?)", (week, team, text)) # 값이 없으면 insert, 있으면 replace
    
    conn.close()


# SQLITE3 DB 에 select
def select_text(db_file_name: str, week: int, team: str, column: str):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # 현재 디렉토리 경로
    db_path = os.path.join(BASE_DIR, db_file_name) # 경로 + DB파일명

    conn = sqlite3.connect(db_path) # conn 객체 생성, isolation_level = None (자동 commit)
    c = conn.cursor() # 커서 생성

    c.execute(f"select {column} from WEEKLY_REPORT where isrt_week = {week} and team = '{team}' ")
    rows = c.fetchall()
    
    conn.close()

    return rows[0][0]


# 오라클 DB 연결
sys.path.append('/settings')
import config

def connect_db(sid: str):
    if sid != config.COMPANY_DB_CONFIG['sid']:
        raise ValueError("DB 를 찾을 수 없습니다.")
    
    conn = create_engine(
        "oracle+cx_oracle://{user}:{password}@{host}:{port}/{sid}?encoding=UTF-8&nencoding=UTF-8".format(
            user=config.COMPANY_DB_CONFIG['user'],
            password=config.COMPANY_DB_CONFIG['password'],
            host=config.COMPANY_DB_CONFIG['host'],
            port=config.COMPANY_DB_CONFIG['port'],
            sid=config.COMPANY_DB_CONFIG['sid']
        )
    )
    return conn

engine = connect_db('IVY')


# US7ASCII의 CP949(완성형한글) -> UTF-8 로 변환
def cp949_to_utf8_in_us7ascii(byte_str: str) -> str:
    try:
        if byte_str is not None: # null 값이면 패스. 안하면 변환 에러난다.
            return byte_str.decode('cp949') # 바이트코드 -> cp949로 디코딩 (서버 쿼리에는 utl_raw.Cast_to_raw()만 씌우면 됨)
    except Exception as e:
        print('='*100)
        print(byte_str, '디코딩 중 에러')
        print(e)
        return None


# 기본 오라클 쿼리 함수
def select_data(sql_text: str) -> pd.DataFrame:
    df = pd.read_sql_query(sql_text, engine)
    
    # 한글로 된 컬럼명
    korean_columns = [
        'cust_name', 'tkyk_name', 'agen_name', 'agen_president', 'agen_store',
        'agen_addr', 'agen_store1', 'agen_saddr1', 'agen_store5', 'agen_saddr5',
        'sch_name', 'cod_name', 'cod_etc', 'schc_small_name', 'user_name',
        ]

    for col in korean_columns: # 한글 컬럼명 순회
        if col in df.columns: # 데이터프레임에 한글 컬럼명이 있으면
            df[col] = df[col].apply(cp949_to_utf8_in_us7ascii)

    return df


def cod_code(cod_gbn_code: str) -> pd.DataFrame:
    sql = f'''
    SELECT cod_code,
           utl_raw.Cast_to_raw(cod_name) cod_name,
           utl_raw.Cast_to_raw(cod_etc) cod_etc
    FROM i_cod_t
    WHERE cod_gbn_code = '{cod_gbn_code}'
    AND del_yn = 'Y'
    '''
    df = select_data(sql)
    return df


def tkyk_code() -> pd.DataFrame:
    sql = f'''
    SELECT tkyk_code,
           utl_raw.Cast_to_raw(tkyk_name) tkyk_name
    FROM i_tkyk_t
    WHERE tkyk_del_yn = 'Y'
    ORDER BY sort
    '''
    df = select_data(sql)
    return df



# -------------------- 전역변수 --------------------

# 집계기간
this_mon, this_fri = get_this_week()

# 지난주
last_mon, last_fri = get_last_week()



# -------------------- 전역변수 끝 --------------------


if __name__ == "__main__":
    print('데이터 모듈파일입니다.')
    