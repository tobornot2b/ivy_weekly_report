from sqlalchemy import create_engine
import pandas as pd
import binascii   # 한글 변환에 필요한 라이브러리
import sys
import sqlite3
import os.path


# SQLITE3 DB 연결
def connect_sqlite3(db_file_name: str, sql_text: str) -> pd.DataFrame:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # 현재 디렉토리 경로
    db_path = os.path.join(BASE_DIR, db_file_name) # 경로 + DB파일명

    conn = sqlite3.connect(db_path) # conn 객체 생성
    c = conn.cursor() # 커서 생성

    df = pd.read_sql(sql_text, conn)
    conn.close()

    return df


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


# US7ASCII -> CP949(완성형한글) 로 변환
def us7ascii_to_cp949(df: pd.DataFrame) -> pd.DataFrame:
    for index, byte_data in enumerate(df):
        if byte_data == None: # null 값이면 패스. 안하면 변환 에러난다.
            continue
        byte_data = binascii.unhexlify(df[index])  # 16진수 문자열 hexstr로 표현된 바이너리 데이터를 반환. 역함수는 b2a_hex()
        df[index] = byte_data.decode("cp949")  # 바이트 변환값 -> cp949(완성형 한글) 로 변환
    return df


# 기본 오라클 쿼리 함수
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
    
    return df


if __name__ == "__main__":
    print('데이터 모듈파일입니다.')
    