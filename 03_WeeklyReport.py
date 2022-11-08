import streamlit as st
import streamlit_authenticator as stauth
import yaml

import pandas as pd
import FinanceDataReader as fdr
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

import re # 특문제거 정규식
from operator import itemgetter # 빈도집계
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

from konlpy.tag import Okt # 코엔엘파이 -> 한국어 정보처리 -> 오픈소스 한국어 처리기


# emojis: https://www.webfx.com//tools/emoji-cheat-sheet/
st.set_page_config(
    page_title='주간업무보고',
    page_icon=":chart_with_upwards_trend:",
    layout="wide"
)


@st.cache
def exchange_rate(year: str) -> pd.DataFrame:
    # today = datetime.today().strftime('%Y-%m-%d') # 오늘

    df1 = fdr.DataReader('USD/KRW', year)
    df2 = fdr.DataReader('KS11', year)
    df3 = fdr.DataReader('KQ11', year)
    df4 = fdr.DataReader('US500', year)
    
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

    st.image('./data/image/slogan.png')


    # # -------------------- 그래프 --------------------

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
        title='코스닥',
        )

    fig3 = go.Figure(data=[go.Candlestick(x=df_ex3.index,
                open=df_ex3['Open'],
                high=df_ex3['High'],
                low=df_ex3['Low'],
                close=df_ex3['Close'])])
    fig3.update_layout(
        paper_bgcolor='rgba(233,233,233,233)',
        plot_bgcolor='rgba(0,0,0,0)',
        title='코스피',
        )


    fig4 = go.Figure(data=[go.Candlestick(x=df_ex4.index,
                open=df_ex4['Open'],
                high=df_ex4['High'],
                low=df_ex4['Low'],
                close=df_ex4['Close'])])
    fig4.update_layout(
        paper_bgcolor='rgba(233,233,233,233)',
        plot_bgcolor='rgba(0,0,0,0)',
        title='S&P500',
        )



    # # -------------------- 메인페이지 --------------------

    # left_column, right_column = st.columns([2, 1])
    # left_column.video('https://youtu.be/UZ7Mc2O90hs')


    tab1, tab2 = st.tabs(['경제지수', '워드클라우드'])

    with tab1:
        st.markdown('#### 오늘의 경제지수 (2022-01-01 ~ 오늘)')
        
        left_column, right_column = st.columns(2)
        left_column.plotly_chart(fig1, use_container_width=True)
        right_column.plotly_chart(fig2, use_container_width=True)
        left_column.plotly_chart(fig3, use_container_width=True)
        right_column.plotly_chart(fig4, use_container_width=True)

        with st.expander('실데이터 (클릭해서 열기)'):
            left_column, right_column = st.columns(2)
            left_column.write('##### USD/KRW')
            right_column.write('##### 코스피')
            left_column.dataframe((df_ex1.sort_index(ascending=False)), use_container_width=True)
            right_column.dataframe((df_ex2.sort_index(ascending=False)), use_container_width=True)
            left_column.write('##### 코스닥')
            right_column.write('##### S&P500')
            left_column.dataframe((df_ex3.sort_index(ascending=False)), use_container_width=True)
            right_column.dataframe((df_ex4.sort_index(ascending=False)), use_container_width=True)



    with tab2:
        st.markdown('''
        #### 워드클라우드
            '워드클라우드'는 단어의 빈도수를 구름 형태로 표현하는 그래픽 기법입니다.

            - 적용대상 : 아이비클럽 시즌 설문조사 중 주관식 응답문항
            - 조사명 : 22N, 22S 유통품질 만족도 / 디자인 선호도
            - 응답자 : 대리점
            
            객관식 문항은 담당부서에서 수치화한 자료로 활용하고 있습니다.
            주관식 문항에 적용하여 많은 시간을 들이지 않고 단어 출현빈도를 통해 중요도를 파악할 수 있습니다.
        ''')

        # 코엔엘파이 -> 한국어 정보처리 -> 오픈소스 한국어 처리기
        okt = Okt()

        # 불용어
        STOPWORDS = ['더', '부분', '학교', '옷', '좀', '진행', '의견', '년', '달', '안함', '경우', '함', '복', '때', '지금', '대한']

        # 워드클라우드 드로우 함수
        def displayWordCloud(season: str, data=None, backgroundcolor='white', width=1600, height=800):
            # word_max = 30 # 최대단어 갯수
            wordcloud = WordCloud(
                font_path = 'C:/Windows/Fonts/D2Coding-Ver1.3.2-20180524-all.ttc',
                stopwords = STOPWORDS, # 불용어
                background_color = backgroundcolor,
                # max_words = word_max,
                prefer_horizontal = 1, #글자 수평
                width = width,
                height = height).generate(data)
            plt.figure(figsize = (15 , 10))
            plt.imshow(wordcloud)
            plt.axis("off")
            # plt.show()
            plt.savefig(f'./data/image/{season}.png')


        # 문자열 전처리 함수
        def preprocessing(text: str) -> str:
            # 양쪽끝 공백제거
            text = text.strip()
            # 개행문자 제거
            text = re.sub('\\\\n', ' ', text)
            # 특수문자 제거
            # 특수문자나 이모티콘 등은 때로는 의미를 갖기도 하지만 여기에서는 제거했습니다.
            # text = re.sub('[?.,;:|\)*~`’!^\-_+<>@\#$%&-=#}※]', '', text)
            
            text = re.sub('[?;:|\)*~`’!^\-_+<>@\#$%&-=#}※]', '', text) # ., 제외
            
            # 한글, 영문, 숫자만 남기고 모두 제거하도록 합니다.
            # text = re.sub('[^가-힣ㄱ-ㅎㅏ-ㅣa-zA-Z0-9]', ' ', text)
            # 한글, 영문만 남기고 모두 제거하도록 합니다.
            # text = re.sub('[^가-힣ㄱ-ㅎㅏ-ㅣa-zA-Z]', ' ', text)
            # 한글만 남기고 모두 제거하도록 합니다.
            # text = re.sub('[^가-힣ㄱ-ㅎㅏ-ㅣ]', ' ', text)
            # 중복으로 생성된 공백값을 제거합니다.
            text = re.sub('[\s]+', ' ', text)
            # 영문자를 소문자로 만듭니다.
            # text = text.lower()
            return text


        # 데이터 불러오기 (DB에서 다운로드)
        df_word = pd.read_excel('./22NSPD.xlsx')

        # map을 통해 전처리 일괄 적용
        df_word['rem4'] = df_word['rem4'].map(preprocessing)

        # 빈도수 카운트
        def word_count_to_dict(words: list) -> dict:
            word_cnt = {} # 사전을 만든다
            for word in words: # 모든 단어에 대해서
                if word in word_cnt: # 사전에 단어가 있으면
                    word_cnt[word] += 1 # 단어의 개수를 1 증가 시킨다
                else: # 없으면
                    word_cnt[word] = 1 # 단어의 개수를 1로 한다\
            
            return word_cnt


        # 최종집계 함수
        @st.cache
        def okt_nouns_wordcloud(season: str, df: pd.DataFrame) -> list:
            okt_content_nouns = okt.nouns(' '.join(df[df['ins_id']==season]['rem4']).replace('_x000D_', '').replace('xDxD', ''))
            displayWordCloud(season, ' '.join(okt_content_nouns))
            
            if season[-1] == 'D':
                gbn = '디자인 선호도 조사'
            else:
                gbn = '유통품질 만족도 조사'
            
            # 빈도수 카운트
            word_count = word_count_to_dict(okt_content_nouns)
            for stwd in STOPWORDS: # 불용어 빼버리기
                if stwd in word_count:
                    word_count.pop(stwd)
                else:
                    pass
            
            sorted_words = sorted(word_count.items(), key=itemgetter(1), reverse=True) # 집계
            
            # 텍스트는 리스트로 만들어서 넘김
            text_list = []
            text_list.append(f'{season[:3]} {gbn} 주관식문항 단어 등장 빈도 순위 (상위 20개)')
            text_list.append(f'< 총 {len(okt_content_nouns)}개 단어 중 상위빈도 20개 단어 >')
            
            for i, wd in enumerate(sorted_words):
                if i < 20:
                    text_list.append(f"{i+1}위 '{wd[0]}' : {wd[1]}회")
                else:
                    break

            # 데이터프레임 생성
            df_sorted_words = pd.DataFrame(sorted_words)
            df_sorted_words.columns = ['단어', '빈도']

            return text_list, df_sorted_words

        str_22ND, df_22ND = okt_nouns_wordcloud('22ND', df_word)
        str_22NP, df_22NP = okt_nouns_wordcloud('22NP', df_word)
        str_22SD, df_22SD = okt_nouns_wordcloud('22SD', df_word)
        str_22SP, df_22SP = okt_nouns_wordcloud('22SP', df_word)


        fig5 = px.bar(
            df_22ND.iloc[:20],
            x='단어',
            y='빈도',
            color='단어',
            title=f'{str_22ND[0]}',
            text='빈도',
            )
        fig5.update_layout(paper_bgcolor='rgba(233,233,233,233)', plot_bgcolor='rgba(0,0,0,0)')
        fig5.update_traces(textposition='inside', textfont_size=14)


        fig6 = px.bar(
            df_22NP.iloc[:20],
            x='단어',
            y='빈도',
            color='단어',
            title=f'{str_22NP[0]}',
            text='빈도',
            )
        fig6.update_layout(paper_bgcolor='rgba(233,233,233,233)', plot_bgcolor='rgba(0,0,0,0)')
        fig6.update_traces(textposition='inside', textfont_size=14)


        fig7 = px.bar(
            df_22SD.iloc[:20],
            x='단어',
            y='빈도',
            color='단어',
            title=f'{str_22SD[0]}',
            text='빈도',
            )
        fig7.update_layout(paper_bgcolor='rgba(233,233,233,233)', plot_bgcolor='rgba(0,0,0,0)')
        fig7.update_traces(textposition='inside', textfont_size=14)


        fig8 = px.bar(
            df_22SP.iloc[:20],
            x='단어',
            y='빈도',
            color='단어',
            title=f'{str_22SP[0]}',
            text='빈도',
            )
        fig8.update_layout(paper_bgcolor='rgba(233,233,233,233)', plot_bgcolor='rgba(0,0,0,0)')
        fig8.update_traces(textposition='inside', textfont_size=14)


        
        st.image('./data/image/22ND.png', use_column_width=True)
        left_column, right_column = st.columns([2, 1])
        left_column.plotly_chart(fig5, use_container_width=True)
        right_column.markdown(f'##### {str_22ND[0]}')
        right_column.text('\n'.join(str_22ND[1:]))
        # st.dataframe(df_22ND)
        

        st.image('./data/image/22NP.png', use_column_width=True)
        left_column, right_column = st.columns([2, 1])
        left_column.plotly_chart(fig6, use_container_width=True)
        right_column.markdown(f'##### {str_22NP[0]}')
        right_column.text('\n'.join(str_22NP[1:]))


        st.image('./data/image/22SD.png', use_column_width=True)
        left_column, right_column = st.columns([2, 1])
        left_column.plotly_chart(fig7, use_container_width=True)
        right_column.markdown(f'##### {str_22SD[0]}')
        right_column.text('\n'.join(str_22SD[1:]))


        st.image('./data/image/22SP.png', use_column_width=True)
        left_column, right_column = st.columns([2, 1])
        left_column.plotly_chart(fig8, use_container_width=True)
        right_column.markdown(f'##### {str_22SP[0]}')
        right_column.text('\n'.join(str_22SP[1:]))

        
        



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