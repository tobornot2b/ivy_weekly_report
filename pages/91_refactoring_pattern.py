import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd
import plotly.express as px
import sys
from datetime import datetime
from data import * # 패키지 불러오기

sys.path.append('/settings') # DB 연결을 위한 경로 추가
import config


# emojis: https://www.webfx.com//tools/emoji-cheat-sheet/
st.set_page_config(
    page_title='주간업무보고',
    page_icon=":chart_with_upwards_trend:",
    layout="wide"
)


# -------------------- 사이드바 (패턴팀) --------------------

# 사이드바 옵션 1
# st.sidebar.header('시즌')

# 사이드바 시즌 선택
SEASON = st.sidebar.selectbox(
    '시즌을 선택하세요 : ',
    options=['23N', '23S'],
)

# 사이드바 옵션 2
# st.sidebar.header('제품')

# 사이드바 제품 선택
choosen_jaepum = st.sidebar.selectbox(
    '제품을 선택하세요 : ',
    options=['학생복', '체육복'],
    
)

# 제품 코드 지정
if choosen_jaepum == '학생복':
    JAEPUM = 'H'
elif  choosen_jaepum == '체육복':
    JAEPUM = 'F'



# -------------------- 함수 (패턴팀) --------------------

class OracleDB:
    def __init__(self):
        self.__user, self.__password, self.__host, self.__port, self.__sid = [config.COMPANY_DB_CONFIG[key] for key in ['user', 'password', 'host', 'port', 'sid']]
        self.engine = create_engine(
            f"oracle+cx_oracle://{self.__user}:{self.__password}@{self.__host}:{self.__port}/{self.__sid}?encoding=UTF-8&nencoding=UTF-8"
        )

    def _cp949_to_utf8_in_us7ascii(self, byte_str: str) -> str:
        try:
            return byte_str.decode('cp949') if byte_str is not None else None
        except Exception as e:
            print('='*100)
            print(byte_str, '디코딩 중 에러')
            print(e)
            return None

    def select_data(self, sql_text: str) -> pd.DataFrame:
        df = pd.read_sql_query(text(sql_text), self.engine.connect())
        korean_columns = ['cust_name', 'tkyk_name', 'agen_name', 'agen_president', 'agen_store',
                          'agen_addr', 'agen_store1', 'agen_saddr1', 'agen_store5', 'agen_saddr5',
                          'sch_name', 'cod_name', 'cod_etc', 'schc_small_name', 'user_name',
                          'schc_name', 'master_sheet_msg']
        for col in korean_columns:
            if col in df.columns:
                df[col] = df[col].apply(self._cp949_to_utf8_in_us7ascii)
        return df


# OracleDB 클래스를 상속받아 패턴 데이터를 가져오는 클래스
class GetPatternData(OracleDB):
    def __init__(self, season: str, jaepum: str):
        super().__init__()
        
        if season[-1] == 'S':
            season1 = season
            season2 = season
        else:
            season1 = season
            season2 = str(int(season[:2])-1) + 'F'
        
        self.sql_text = self._make_sql(season1, season2, jaepum) # sql 쿼리문 생성
        self.df = self.select_data(self.sql_text) # 데이터프레임 생성
        self.df_M, self.df_F = self._data_preprocess(self.df) # 데이터 전처리
        self.fig_M, self.fig_F = self._make_graph(self.df_M, self.df_F, season) # 그래프 생성

    # 쿼리문 생성
    def _make_sql(self, season1: str, season2: str, jaepum: str) -> str:
        '''
        < 프로그램 : 타입대비 패턴현황 (WTIC33OP_1 -> d_wtic33op_1_2) >
            - 제품 : 학생복(d), 체육복, 초등복, 유치원
            - 복종 : 전체(d)
            - 타입일 : 전체(d)
            - 구분 : 업체별(d), 복종별
            - 성별 : 남자, 여자
            - 조회구분 : 대표복종합치기, 복종별
            - 수주 : 메인(d), 샘플
            - 비고 : 남녀별로 쿼리를 나누어서 보여줘야 하므로 조회 (원본에는 개별쿼리)
        '''

        sql_text = f'''
        SELECT '{season1}/{season2}'           season,
            '1'                                gubun,
            Decode('Y', 'Y', Substr(cod_etc, 1, 1),
                        a.master_bokjong)       master_bokjong,
            Max(sort) sort,
            utl_raw.Cast_to_raw(c.cust_name) cust_name,
            Count(a.master_order)               ALL_COUNT,
            SUM(a.master_jisi_qty)              ALL_QTY,
            SUM(Decode(a.master_pt_save_gb, 'Y', 1,
                                            0)) SAVE_COUNT,
            SUM(Decode(a.master_pt_save_gb, 'Y', master_jisi_qty,
                                            0)) SAVE_QTY
        FROM   i_suju_master_t a,
            i_suju_fact_t b,
            i_cust_t c,
            i_cod_t
        WHERE  cod_gbn_code = 'PY'
            AND cod_code = a.master_bokjong
            AND a.master_order = b.fact_order
            AND c.cust_code = b.fact_code
            AND a.master_quota IN ( '{season1}', '{season2}' )
            AND a.master_status >= '50'
            AND a.master_sex IN ( 'A', 'C', 'E' )
            AND a.master_jaepum = '{jaepum}'
            AND cod_etc <> 'XX'
        GROUP  BY b.fact_code,
                c.cust_name,
                Decode('Y', 'Y', Substr(cod_etc, 1, 1),
                            a.master_bokjong)
        UNION ALL
        SELECT '{season1}/{season2}'           season,
            '2'                                gubun,
            Decode('Y', 'Y', Substr(cod_etc, 1, 1),
                        a.master_bokjong)       master_bokjong,
            Max(sort) sort,
            utl_raw.Cast_to_raw(c.cust_name) cust_name,
            Count(a.master_order)               ALL_COUNT,
            SUM(a.master_jisi_qty)              ALL_QTY,
            SUM(Decode(a.master_pt_save_gb, 'Y', 1,
                                            0)) SAVE_COUNT,
            SUM(Decode(a.master_pt_save_gb, 'Y', master_jisi_qty,
                                            0)) SAVE_QTY
        FROM   i_suju_master_t a,
            i_suju_fact_t b,
            i_cust_t c,
            i_cod_t
        WHERE  cod_gbn_code = 'PY'
            AND cod_code = a.master_bokjong
            AND a.master_order = b.fact_order
            AND c.cust_code = b.fact_code
            AND a.master_quota IN ( '{season1}', '{season2}' )
            AND a.master_status >= '50'
            AND a.master_sex IN ( 'B', 'D', 'F' )
            AND a.master_jaepum = '{jaepum}'
            AND cod_etc <> 'XX'
        GROUP  BY b.fact_code,
                c.cust_name,
                Decode('Y', 'Y', Substr(cod_etc, 1, 1),
                            a.master_bokjong) 

        '''
        return sql_text
    
    # 데이터 전처리
    def _data_preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        df.columns = ['시즌', '구분', '복종', '정렬', '봉제업체', '타입건수', '지시량', '작업건수', '작업량']
        df['작업율(%)'] = round((df['작업량'] / df['지시량']) * 100, 1)
        # df['작업율(%)'] = round((df['작업량'] / df['지시량']) * 100, 1) # 소숫점 1자리까지
        # df['작업율(%)'] = df['작업율(%)'].astype(str)
        # df['작업율(%)'] = df['작업율(%)'] + '%'
        df['구분'] = df['구분'].str.replace('1', '남').replace('2', '여')
        df = df.sort_values(['구분', '복종', '봉제업체']).reset_index(drop=True)
        df = df.drop('정렬', axis=1)

        df_M = df[df['구분'] == '남'].reset_index(drop=True).set_index('시즌')
        df_F = df[df['구분'] == '여'].reset_index(drop=True).set_index('시즌')

        return df_M, df_F
    
    def _make_graph(self, df_M: pd.DataFrame, df_F: pd.DataFrame, choosen_season: str) -> px.bar:
        fig1 = px.bar(
            df_M,
            x='봉제업체',
            y='작업율(%)',
            color='복종',
            title=f'{choosen_season} 타입대비 패턴 현황 (남)',
            text=df_M['작업율(%)'].apply(lambda x: '{0:1.1f}%'.format(x)),
            height=450,
            )
        fig1.update_traces(width=0.65) # 바 두께 (0 ~ 1)
        fig1.update_layout(
            paper_bgcolor='rgba(233,233,233,233)',
            plot_bgcolor='rgba(0,0,0,0)',
            title_font_size=30,
            )
        fig1.update_traces(textposition='inside', textfont_size=14)

        fig2 = px.bar(
            df_F,
            x='봉제업체',
            y='작업율(%)',
            color='복종',
            title=f'{choosen_season} 타입대비 패턴 현황 (여)',
            text=df_F['작업율(%)'].apply(lambda x: '{0:1.1f}%'.format(x)),
            height=450,
            )
        # fig2.update_traces(width=0.8) # 바 두께 (0 ~ 1)
        fig2.update_layout(
            paper_bgcolor='rgba(233,233,233,233)',
            plot_bgcolor='rgba(0,0,0,0)',
            title_font_size=30,
            )
        fig2.update_traces(textposition='inside', textfont_size=14)

        return fig1, fig2




# -------------------- 메인페이지 (패턴팀) --------------------

patternData = GetPatternData(season=SEASON, jaepum=JAEPUM)

st.markdown('#### 패턴팀 주간업무 보고')
st.markdown(f"주요업무 ({mod.this_mon} ~ {mod.this_fri})")

mod.draw_plan(mod.plan_data, '패턴팀') # MASTER PLAN

st.markdown("##### 패턴 출고 현황")

# 컬럼 2분할
left_column, right_column = st.columns(2)
left_column.dataframe(patternData.df_M, use_container_width=True)
right_column.dataframe(patternData.df_F, use_container_width=True)

left_column, right_column = st.columns(2)
left_column.plotly_chart(patternData.fig_M, use_container_width=True)
right_column.plotly_chart(patternData.fig_F, use_container_width=True)



# 입력도구
tab1, tab2 = st.tabs(['.', '.'])
with tab1:
    try:
        sel_text = mod.select_text(mod.db_file, datetime.strptime(mod.this_fri, '%Y/%m/%d').isocalendar()[1], '패턴팀', 'text1')
        st.markdown(sel_text)
    except IndexError:
        sel_text = ''

with tab2:
    # 입력
    patt_text = st.text_area('이번 주 내용을 입력하세요.', sel_text)
    st.write('입력된 내용 : \n', patt_text)
    
    mod.insert_text(mod.db_file, datetime.strptime(mod.this_fri, '%Y/%m/%d').isocalendar()[1], '패턴팀', patt_text, 'text1')


# -------------------- HIDE STREAMLIT STYLE --------------------
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)