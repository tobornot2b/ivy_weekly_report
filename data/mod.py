import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd
# import binascii   # 한글 변환에 필요한 라이브러리
import sys
import sqlite3
import os.path
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta # 1달단위 날짜 구하기
import plotly.express as px


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


# MASTER_PLAN 불러오기
def select_plan(db_file_name: str, dept: str):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # 현재 디렉토리 경로
    db_path = os.path.join(BASE_DIR, db_file_name) # 경로 + DB파일명

    conn = sqlite3.connect(db_path) # conn 객체 생성, isolation_level = None (자동 commit)
    c = conn.cursor() # 커서 생성

    c.execute(f"select * from MASTER_PLAN where from_date between '2023-06-01' and '2024-06-01' and ('*' = '{dept}' or dept = '{dept}') ")
    rows = c.fetchall()
    
    conn.close()

    # 데이터프레임으로 변환
    df = pd.DataFrame(rows, columns=['부서', '시작일', '종료일', '계획명', 'line'])
    df['시작일'] = pd.to_datetime(df['시작일']) # 날짜형식으로 변경
    df['종료일'] = pd.to_datetime(df['종료일']) # 날짜형식으로 변경
    
    return df
plan_data = select_plan(db_file, '*') # 전체 부서, 한번 호출하면 계속 사용


def draw_plan(df: pd.DataFrame, dept: str):
    now = datetime.now()
    if (now - relativedelta(months=1)) < datetime.strptime('2023-06-01', '%Y-%m-%d'):
        before = datetime.strptime('2023-06-01', '%Y-%m-%d')
    else:
        before = now - relativedelta(months=1) # 뒤로 1개월까지 보임
    after = now + relativedelta(months=4) # 앞으로 4개월까지 보임

    if dept != '*':
        height = 300
        df = df[df['부서'] == dept].copy()
    else:
        height = 250
        # before = datetime.strptime('2023-06-01', '%Y-%m-%d')
        # after = before + relativedelta(months=12) # 앞으로 4개월까지 보임

    # 부서별 컬러값
    color_dict = {
        '영업관리팀': 'rgb(192, 0, 0)',
        '생산팀': 'rgb(19, 19, 185)',
        '구매팀': 'rgb(76, 37, 42)',
        '디자인팀': 'rgb(94, 144, 205)',
        '패턴팀': 'rgb(182, 211, 23)',
        '마케팅팀': 'rgb(239, 120, 64)',
        }

    fig_timeline = px.timeline(
        df,
        x_start='시작일',
        x_end='종료일',
        y='line',
        color='부서',
        color_discrete_map=color_dict,
        text='계획명',
        # facet_row='부서',
        )
    fig_timeline.update_layout(
        height=height * len(df['부서'].unique()),
        title=f'MASTER PLAN ({dept})',
        title_font_size=20,
        )
    if dept == '*':
        fig_timeline.update_traces(textposition='inside')
    else:
        fig_timeline.update_traces(textposition='auto')
    fig_timeline.update_xaxes(
        range=[before.strftime('%Y-%m-%d'), after.strftime('%Y-%m-%d')],
        tickformat='%Y / %m',
        minor_ticks='outside',
        showgrid=True,
        gridwidth=1, gridcolor='black', griddash='dot',
        tick0=before,
        dtick='M1',
        )
    fig_timeline.update_yaxes(
        title_text='',
        showticklabels=False,
        autorange='reversed',
        )
    fig_timeline.add_vline(x=now, line_width=3, line_color='red', line_dash='solid')
    
    st.plotly_chart(fig_timeline, use_container_width=True)


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
    df = pd.read_sql_query(text(sql_text) , engine.connect()) # sqlalchemy 2.0 버전업 이후 파라메터가 방식이 변경됨
    
    # 한글로 된 컬럼명
    korean_columns = [
        'cust_name', 'tkyk_name', 'agen_name', 'agen_president', 'agen_store',
        'agen_addr', 'agen_store1', 'agen_saddr1', 'agen_store5', 'agen_saddr5',
        'sch_name', 'cod_name', 'cod_etc', 'schc_small_name', 'user_name',
        'schc_name', 'master_sheet_msg',
        # 'g2b_co_gb', 'g2b_co_gb2', 'g2b_co_gb3', 'g2b_pcs_remark',
        # 'g2b_no', 'sch_f_bok',
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


# 학생수 추이
def student_pop() -> pd.DataFrame:
    df = pd.read_excel(
        './data/2022_연령별 학생수.xlsx',
        sheet_name='Sheet0',
        nrows=207,
        usecols=[0,1,2,5,8,11,14,17,20,23,26,29,32,35,38,41,44,47,50,53,56,59,62],
        )

    df.rename(columns={'만 7세(유치원은 7세이상)':'만 7세'}, inplace=True)

    df = df[
        (df['시도']=='전국')&
        (
        (df['학제']=='유치원')|
        (df['학제']=='초등학교')|
        (df['학제']=='중학교')|
        (df['학제']=='고등학교')
        )
        ]
    
    st_num: list = list(df.iloc[:,7:-4].max())
    years: list = [str(i) for i in range(2020, 2029)]
    m1: list = []
    h1: list = []

    for i in range(-1, -10, -1): # 2020~2028년
        m1.append(st_num[i-3])
        h1.append(st_num[i])

    df_plot = pd.DataFrame(zip(years, m1, h1), columns = ['년도', '중1', '고1'])

    df_plot = df_plot.melt(id_vars='년도', var_name='학교구분', value_name='학생수')

    return df, df_plot


# 인구 조사
def read_census() -> pd.DataFrame:
    df = pd.read_excel(
        './data/202212_202212_연령별인구현황_연간.xlsx',
        header=3,
        )
    
    df = df.drop(columns=['행정기관코드', '연령구간인구수', '총 인구수'])
    df1 = df.iloc[:1].copy()
    df2 = df.iloc[1:].copy()

    df1 = df1.drop(columns=['행정기관']).T.reset_index()
    df1.columns = ['연령', '인구수']
    
    return df1, df2




# -------------------- 전역변수 --------------------

# 집계기간
this_mon, this_fri = get_this_week()

# 지난주
last_mon, last_fri = get_last_week()



# -------------------- 전역변수 끝 --------------------


if __name__ == "__main__":
    print('데이터 모듈파일입니다.')
    