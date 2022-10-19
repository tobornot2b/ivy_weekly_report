import streamlit as st
import streamlit_authenticator as stauth
import yaml

import pandas as pd
import FinanceDataReader as fdr
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime


# emojis: https://www.webfx.com//tools/emoji-cheat-sheet/
st.set_page_config(
    page_title='주간업무보고',
    page_icon=":chart_with_upwards_trend:",
    layout="wide"
)


@st.cache
def exchange_rate(year: str) -> pd.DataFrame:
    today = datetime.today().strftime('%Y-%m-%d') # 오늘

    df1 = fdr.DataReader('USD/KRW', year)
    df2 = fdr.DataReader('KS11', year)
    df3 = fdr.DataReader('US500', year)
    df4 = fdr.DataReader('BTC/KRW', year)
    
    return df1, df2, df3, df4



# st.title('메인 페이지')
st.sidebar.info('각 팀별 페이지를 선택하세요.')


# -------------------- 사용자 인증 파트 --------------------

with open('./config.yaml') as file:
    config = yaml.load(file, Loader=yaml.SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status == False:
    st.error('아이디/비번이 올바르지 않습니다.')

if authentication_status == None:
    st.warning('아이디와 비번을 입력하세요.')

if authentication_status:
    # st.success('인증완료')

    authenticator.logout("Logout", "sidebar")
    st.sidebar.title(f"환영합니다! {name}님")
    st.sidebar.success('로그인 성공')

    # st.image('./data/image/slogan.png', width=None)


    # -------------------- 그래프 --------------------

    # 환율정보
    base_date: str = '2022' # 기준일자
    df_ex1, df_ex2, df_ex3, df_ex4 = exchange_rate(base_date)

    fig1 = go.Figure(data=[go.Candlestick(x=df_ex1.index,
                open=df_ex1['Open'],
                high=df_ex1['High'],
                low=df_ex1['Low'],
                close=df_ex1['Close'],)])
    fig1.update_layout(
        paper_bgcolor='rgba(233,233,233,233)',
        plot_bgcolor='rgba(0,0,0,0)',
        title='USD/KRW',
        )

    fig2 = go.Figure(data=[go.Candlestick(x=df_ex2.index,
                open=df_ex2['Open'],
                high=df_ex2['High'],
                low=df_ex2['Low'],
                close=df_ex2['Close'])])
    fig2.update_layout(
        paper_bgcolor='rgba(233,233,233,233)',
        plot_bgcolor='rgba(0,0,0,0)',
        title='KOSPI',
        )

    fig3 = go.Figure(data=[go.Candlestick(x=df_ex3.index,
                open=df_ex3['Open'],
                high=df_ex3['High'],
                low=df_ex3['Low'],
                close=df_ex3['Close'])])
    fig3.update_layout(
        paper_bgcolor='rgba(233,233,233,233)',
        plot_bgcolor='rgba(0,0,0,0)',
        title='S&P500',
        )


    fig4 = go.Figure(data=[go.Candlestick(x=df_ex4.index,
                open=df_ex4['Open'],
                high=df_ex4['High'],
                low=df_ex4['Low'],
                close=df_ex4['Close'])])
    fig4.update_layout(
        paper_bgcolor='rgba(233,233,233,233)',
        plot_bgcolor='rgba(0,0,0,0)',
        title='BTC/KRW',
        )

    # fig1 = px.line(df_ex1,
    #         y=['Close', 'Open', 'High', 'Low'],
    #         title='USD/KRW',
    #         height=400,
    #         )
    # fig1.update_layout(
    #     paper_bgcolor='rgba(233,233,233,233)',
    #     plot_bgcolor='rgba(0,0,0,0)',
    #     )

    # fig2 = px.line(df_ex2,
    #         y=['Close', 'Open', 'High', 'Low'],
    #         title='KOSPI',
    #         height=400,
    #         )
    # fig2.update_layout(
    #     paper_bgcolor='rgba(233,233,233,233)',
    #     plot_bgcolor='rgba(0,0,0,0)',
    #     )

    # fig3 = px.line(df_ex3,
    #         y=['Close', 'Open', 'High', 'Low'],
    #         title='다우존스',
    #         height=400,
    #         )
    # fig3.update_layout(
    #     paper_bgcolor='rgba(233,233,233,233)',
    #     plot_bgcolor='rgba(0,0,0,0)',
    #     )
    
    # fig4 = px.line(df_ex4,
    #         y=['Close', 'Open', 'High', 'Low'],
    #         title='BTC/KRW',
    #         height=400,
    #         )
    # fig4.update_layout(
    #     paper_bgcolor='rgba(233,233,233,233)',
    #     plot_bgcolor='rgba(0,0,0,0)',
    #     )

    
    # -------------------- 메인페이지 --------------------

    st.markdown('#### 오늘의 지표 (2022-01-01 ~ 오늘)')

    # st.markdown('##### USD/KRW')
    left_column, right_column = st.columns(2)
    left_column.write(fig1, use_container_width=True)
    right_column.write(fig2, use_container_width=True)
    left_column.write(fig3, use_container_width=True)
    right_column.write(fig4, use_container_width=True)

    with st.expander('실데이터 (클릭해서 열기)'):
        left_column, right_column = st.columns(2)
        left_column.write('##### USD/KRW')
        right_column.write('##### KOSPI')
        left_column.write((df_ex1.sort_index(ascending=False)), use_container_width=True)
        right_column.write((df_ex2.sort_index(ascending=False)), use_container_width=True)
        left_column.write('##### S&P500')
        right_column.write('##### BTC/KRW')
        left_column.write((df_ex3.sort_index(ascending=False)), use_container_width=True)
        right_column.write((df_ex4.sort_index(ascending=False)), use_container_width=True)


    # st.markdown('##### KOSPI')
    # left_column, right_column = st.columns(2)
    # left_column.write((df_ex2.sort_index(ascending=False)), use_container_width=True)
    # right_column.write(fig2, use_container_width=True)

    # st.markdown('##### 다우존스')
    # left_column, right_column = st.columns(2)
    # left_column.write((df_ex3.sort_index(ascending=False)), use_container_width=True)
    # right_column.write(fig3, use_container_width=True)

    # st.markdown('##### 비트코인/원화')
    # left_column, right_column = st.columns(2)
    # left_column.write((df_ex4.sort_index(ascending=False)), use_container_width=True)
    # right_column.write(fig4, use_container_width=True)

    # st.markdown('''
    # # 아이비클럽 주간업무 대시보드: 표와 그래프로 구성된 웹앱
    # [![아이비클럽](http://www.ivyclub.co.kr/page/images/footer/logo.png)](http://www.ivyclub.co.kr)


    # ## 무슨 프로그램인가?

    # **아이비클럽 주간업무 대시보드**는 아이비클럽의 각 부서별 주간업무보고를 웹으로 옮긴 프로그램 입니다.  
    # 각 부서별 데이터를 **쉽고 직관적으로** 보기 위해 만들어졌으며 **실시간**으로 데이터를 DB에서 불러와  
    # 그래프와 테이블로 표현합니다. 그래프만 보고 직관적으롤 현황을 파악하는 것이 목적이며  
    # 최종적으로는 메타데이터를 활용해 더 다양한 인사이트를 도출해내는 것을 목표로 합니다.  



    # ## 주요 특징

    # - 사용자 인증
    # - DB에서 실시간 데이터 호출
    # - 불러온 데이터를 기반으로 한 그래프 도출
    # - 반응형 그래프
    # - 막대, 꺾은 선 그래프를 제외한 면적, 원 형태의 그래프는 모두 인터렉티브 그래프로 제작
    # - 웹앱이므로 모바일에서도 사용 가능



    # ## 아직 구현되지 않은 부분 혹은 미흡한 점

    # - N+F 통합시즌 뷰 (차후 구현 예정)
    # - 조회 시점에 따른 수주량 차이 (가수주)
    # - 수주량과 해제량은 시즌 막바지로 갈수록 동일한 값으로 수렴하게 된다.
    # - 시스템이 변동량을 기록하는 것이 아니라 실수량을 기록하는 것이기 때문.
    # - 운영서버는 분석이 목적이 아니므로 가변하는 수량을 기록하지 않는다.
    # - 분석만을 위한 별도의 기록을 하거나, 보고를 위해 기록된 데이터(엑셀)로 구현한다.
    # - 현재는 보고된 엑셀 데이터로 구현


    # ## 개발언어

    # - python


    # ## 사용한 라이브러리

    # - streamlit
    # - streamlit_authenticator
    # - streamlit_option_menu
    # - pyyaml
    # - sqlalchemy
    # - pandas
    # - binascii
    # - xlwings
    # - sqlite3
    # - plotly
    # ''')



    # -------------------- HIDE STREAMLIT STYLE --------------------
    hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
    st.markdown(hide_st_style, unsafe_allow_html=True)