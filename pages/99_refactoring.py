import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from data import * # 패키지 불러오기


# emojis: https://www.webfx.com//tools/emoji-cheat-sheet/
st.set_page_config(
    page_title='주간업무보고',
    page_icon=":chart_with_upwards_trend:",
    layout="wide"
)

# -------------------- 함수 (패턴팀) --------------------

# 패턴팀 SQL문
@st.cache_data
def make_sql(season1: str, season2: str, jaepum: str) -> str:
    sql = f'''
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
    return sql


# 전처리 함수 (남자 데이터, 여자 데이터 반환)
@st.cache_data
def data_preprocess(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = ['시즌', '구분', '복종', '정렬', '봉제업체', '타입건수', '지시량', '작업건수', '작업량']
    df['작업율'] = round((df['작업량'] / df['지시량']) * 100, 1)
    df['작업율(%)'] = round((df['작업량'] / df['지시량']) * 100, 1) # 소숫점 1자리까지
    df['작업율(%)'] = df['작업율(%)'].astype(str)
    df['작업율(%)'] = df['작업율(%)'] + '%'
    df['구분'] = df['구분'].str.replace('1', '남').replace('2', '여')
    df = df.sort_values(['구분', '복종', '봉제업체']).reset_index(drop=True)
    df = df.drop('정렬', axis=1)

    df_M = df[df['구분'] == '남'].reset_index(drop=True).set_index('시즌')
    df_F = df[df['구분'] == '여'].reset_index(drop=True).set_index('시즌')

    return df_M, df_F


# -------------------- 사이드바 (패턴팀) --------------------

# 사이드바 옵션 1
st.sidebar.header('시즌')

# 사이드바 시즌 선택
choosen_season = st.sidebar.selectbox(
    '시즌을 선택하세요 : ',
    options=['23N/22F', '23S'],
)

# 사이드바 옵션 2
st.sidebar.header('제품')

# 사이드바 제품 선택
choosen_jaepum = st.sidebar.selectbox(
    '제품을 선택하세요 : ',
    options=['학생복', '체육복'],
)

# 제품 코드 지정
if choosen_jaepum == '학생복':
    jaepum = 'H'
elif  choosen_jaepum == '체육복':
    jaepum = 'F'




# SQL문 만들기
sql_1 = make_sql(choosen_season[:3], choosen_season[-3:], jaepum)

# 기본 데이터프레임 만들기
df_base = mod.select_data(sql_1)

# 전처리 (남, 여 반환)
df_M, df_F = data_preprocess(df_base)



# -------------------- 그래프 (패턴팀) --------------------

fig1 = px.bar(df_M,
            x='봉제업체',
            y='작업율',
            color='복종',
            title=f'{choosen_season} 타입대비 패턴 현황 (남)',
            text='작업율(%)',
            height=450,
            )
fig1.update_traces(width=0.65) # 바 두께 (0 ~ 1)
fig1.update_layout(
    paper_bgcolor='rgba(233,233,233,233)',
    plot_bgcolor='rgba(0,0,0,0)',
    title_font_size=30,
    )
fig1.update_traces(textposition='inside', textfont_size=14)

fig2 = px.bar(df_F,
            x='봉제업체',
            y='작업율',
            color='복종',
            title=f'{choosen_season} 타입대비 패턴 현황 (여)',
            text='작업율(%)',
            height=450,
            )
# fig2.update_traces(width=0.8) # 바 두께 (0 ~ 1)
fig2.update_layout(
    paper_bgcolor='rgba(233,233,233,233)',
    plot_bgcolor='rgba(0,0,0,0)',
    title_font_size=30,
    )
fig2.update_traces(textposition='inside', textfont_size=14)




# -------------------- 메인페이지 (패턴팀) --------------------

st.markdown('#### 패턴팀 주간업무 보고')
st.markdown(f"주요업무 ({mod.this_mon} ~ {mod.this_fri})")

st.markdown("##### 패턴 출고 현황")

# 컬럼 2분할
left_column, right_column = st.columns(2)
left_column.dataframe(df_M.drop('작업율', axis=1), use_container_width=True)
right_column.dataframe(df_F.drop('작업율', axis=1), use_container_width=True)

# st.markdown('''---''')
left_column, right_column = st.columns(2)
left_column.plotly_chart(fig1, use_container_width=True, theme=None)
right_column.plotly_chart(fig2, use_container_width=True, theme=None)


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