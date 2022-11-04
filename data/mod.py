import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import binascii   # 한글 변환에 필요한 라이브러리
import sys
import sqlite3
import os.path
from datetime import datetime, date, timedelta

# SQLITE3 DB 파일명
db_file = 'daliy_order.db'


# 지난주 월요일 - 금요일 구하기
# @st.cache
def get_last_week() -> str:
    diff_1: int = (date.today().weekday() - 0) % 7 # 0:월요일, 1:화요일, 2:수요일, 3:목요일, 4:금요일, 5:토요일, 6:일요일
    diff_2: int = (date.today().weekday() - 4) % 7 # 0:월요일, 1:화요일, 2:수요일, 3:목요일, 4:금요일, 5:토요일, 6:일요일
    
    last_mon: str = (date.today() - timedelta(days=diff_1 + 7)).strftime("%Y/%m/%d") # 대쉬를 뺀 형식으로 변경
    last_fri: str = (date.today() - timedelta(days=diff_2)).strftime("%Y/%m/%d") # 대쉬를 뺀 형식으로 변경
    
    return last_mon, last_fri


# 이번주 월요일 - 금요일 구하기
# @st.cache
def get_this_week() -> str:
    diff_1: int = (date.today().weekday() - 0) % 7 # 0:월요일, 1:화요일, 2:수요일, 3:목요일, 4:금요일, 5:토요일, 6:일요일
    diff_2: int = (date.today().weekday() - 4) % 7 # 0:월요일, 1:화요일, 2:수요일, 3:목요일, 4:금요일, 5:토요일, 6:일요일
    
    this_mon: str = (date.today() - timedelta(days=diff_1)).strftime("%Y/%m/%d") # 대쉬를 뺀 형식으로 변경
    this_fri: str = (date.today() - timedelta(days=diff_2 - 7)).strftime("%Y/%m/%d") # 대쉬를 뺀 형식으로 변경
    
    return this_mon, this_fri

# # 유저정보 가져오기
# # @st.cache
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
# @st.cache
def clean_text(inputString: str) -> str:
    # text_rmv = re.sub('[-=+,#/\?:^.@*\"※~ㆍ!』‘|\(\)\[\]`\'…》\”\“\’·]', ' ', inputString)
    text_rmv = inputString.rstrip('\r\n')
    # text_rmv = re.sub('/^[ㄱ-ㅎ|가-힣|a-z|A-Z|0-9|]+$/', '', str(inputString))

    return str(text_rmv)


# SQLITE3 DB 연결
# @st.cache
def connect_sqlite3(db_file_name: str, sql_text: str) -> pd.DataFrame:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # 현재 디렉토리 경로
    db_path = os.path.join(BASE_DIR, db_file_name) # 경로 + DB파일명

    conn = sqlite3.connect(db_path) # conn 객체 생성
    c = conn.cursor() # 커서 생성

    df = pd.read_sql(sql_text, conn)
    conn.close()

    return df


# SQLITE3 DB 에 insert
# @st.cache
def insert_text(db_file_name: str, week: int, team: str, text: str, column: str):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # 현재 디렉토리 경로
    db_path = os.path.join(BASE_DIR, db_file_name) # 경로 + DB파일명

    conn = sqlite3.connect(db_path, isolation_level = None) # conn 객체 생성, isolation_level = None (자동 commit)
    c = conn.cursor() # 커서 생성

    # text = clean_text(text)

    c.execute(f"INSERT OR REPLACE INTO WEEKLY_REPORT (isrt_week, team, {column}) VALUES (?,?,?)", (week, team, text)) # 값이 없으면 insert, 있으면 replace
    
    conn.close()


# SQLITE3 DB 에 select
# @st.cache
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

# @st.cache
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


# US7ASCII -> CP949(완성형한글) 로 변환
# @st.cache
def us7ascii_to_cp949(df: pd.DataFrame) -> pd.DataFrame:
    for index, byte_data in enumerate(df):
        if byte_data == None: # null 값이면 패스. 안하면 변환 에러난다.
            continue
        byte_data = binascii.unhexlify(df[index])  # 16진수 문자열 hexstr로 표현된 바이너리 데이터를 반환. 역함수는 b2a_hex()
        df[index] = byte_data.decode("cp949")  # 바이트 변환값 -> cp949(완성형 한글) 로 변환
    return df


# 기본 오라클 쿼리 함수
# @st.cache
def select_data(sql_text: str) -> pd.DataFrame:
    df = pd.read_sql_query(sql_text, engine)
    
    if 'cust_name' in df.columns: # 해당컬럼이 없어도 에러없이 처리
        df_temp = df['cust_name'].copy()
        df['cust_name'] = us7ascii_to_cp949(df_temp)

    if 'tkyk_name' in df.columns:
        df_temp = df['tkyk_name'].copy()
        df['tkyk_name'] = us7ascii_to_cp949(df_temp)

    if 'agen_name' in df.columns:
        df_temp = df['agen_name'].copy()
        df['agen_name'] = us7ascii_to_cp949(df_temp)
        
    if 'agen_president' in df.columns:
        df_temp = df['agen_president'].copy()
        df['agen_president'] = us7ascii_to_cp949(df_temp)
        
    if 'agen_store' in df.columns:
        df_temp = df['agen_store'].copy()
        df['agen_store'] = us7ascii_to_cp949(df_temp)
        
    if 'agen_addr' in df.columns:
        df_temp = df['agen_addr'].copy()
        df['agen_addr'] = us7ascii_to_cp949(df_temp)
        
    if 'agen_store1' in df.columns:
        df_temp = df['agen_store1'].copy()
        df['agen_store1'] = us7ascii_to_cp949(df_temp)
        
    if 'agen_saddr1' in df.columns:
        df_temp = df['agen_saddr1'].copy()
        df['agen_saddr1'] = us7ascii_to_cp949(df_temp)
        
    if 'agen_store5' in df.columns:
        df_temp = df['agen_store5'].copy()
        df['agen_store5'] = us7ascii_to_cp949(df_temp)
        
    if 'agen_saddr5' in df.columns:
        df_temp = df['agen_saddr5'].copy()
        df['agen_saddr5'] = us7ascii_to_cp949(df_temp)

    if 'sch_name' in df.columns:
        df_temp = df['sch_name'].copy()
        df['sch_name'] = us7ascii_to_cp949(df_temp)

    if 'cod_name' in df.columns:
        df_temp = df['cod_name'].copy()
        df['cod_name'] = us7ascii_to_cp949(df_temp)

    if 'cod_etc' in df.columns:
        df_temp = df['cod_etc'].copy()
        df['cod_etc'] = us7ascii_to_cp949(df_temp)

    if 'schc_small_name' in df.columns:
        df_temp = df['schc_small_name'].copy()
        df['schc_small_name'] = us7ascii_to_cp949(df_temp)

    return df


# @st.cache
def cod_code(cod_gbn_code: str) -> pd.DataFrame:
    sql = f'''
    SELECT cod_code,
           Rawtohex(utl_raw.Cast_to_raw(cod_name)) cod_name,
           Rawtohex(utl_raw.Cast_to_raw(cod_etc)) cod_etc
    FROM i_cod_t
    WHERE cod_gbn_code = '{cod_gbn_code}'
    AND del_yn = 'Y'
    '''
    df = select_data(sql)
    return df


# @st.cache
def tkyk_code() -> pd.DataFrame:
    sql = f'''
    SELECT tkyk_code,
           Rawtohex(utl_raw.Cast_to_raw(tkyk_name)) tkyk_name
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
    