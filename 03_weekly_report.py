from sys import set_asyncgen_hooks
from sqlalchemy import create_engine
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime, date, time, timedelta

from data import * # 패키지 불러오기


# STREAMLIT 파트

# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="부서별 주간보고 대시보드", page_icon=":chart_with_upwards_trend:", layout="wide")

# 집계기간
this_mon, this_fri = sales.get_this_week()

# 지난주
last_mon, last_fri = sales.get_last_week()


# ---------- 사이드바 (메인) ----------
st.sidebar.header('부서선택')
department: list = st.sidebar.selectbox(
    '부서를 선택하세요 : ',
    options=['패턴팀', '디자인팀', '마케팅팀', '영업팀', '생산팀', '구매팀'],
)


# ---------------------------------------------------- 패턴팀 ----------------------------------------------------

if department == '패턴팀':
    st.title('패턴팀 주간업무 보고')
    st.subheader(f"주요업무 ({this_mon} ~ {this_fri})")
    st.markdown('''---''')


    # ---------- 사이드바 (패턴팀) ----------
    st.sidebar.header('시즌')

    # 사이드바 시즌 선택
    choosen_season_pt = st.sidebar.selectbox(
        '시즌을 선택하세요 : ',
        options=['22F/23N', '23S'],
    )
    
    # 사이드바 2
    st.sidebar.header('제품')

    # 사이드바 제품 선택
    choosen_jaepum_pt = st.sidebar.selectbox(
        '제품을 선택하세요 : ',
        options=['학생복', '체육복'],
    )
    
    # 제품 코드 지정
    if choosen_jaepum_pt == '학생복':
        jaepum_pt = 'H'
    elif  choosen_jaepum_pt == '체육복':
        jaepum_pt = 'F'



    # ---------- 메인페이지 (패턴팀) ----------

    st.markdown("### 패턴 출고 현황")

    
    # SQL문 만들기
    patt_sql_1 = patt.make_sql(choosen_season_pt[:3], choosen_season_pt[-3:], jaepum_pt)

    # 기본 데이터프레임 만들기
    df_patt_base = mod.select_data(patt_sql_1)

    # 전처리 (남, 여 반환)
    df_patt_M, df_patt_F = patt.data_preprocess(df_patt_base)


    # 컬럼 2분할
    left_column, right_column = st.columns(2)
    left_column.dataframe(df_patt_M.drop('작업율', axis=1), width=None, height=None)
    right_column.dataframe(df_patt_F.drop('작업율', axis=1), width=None, height=None)


    # ---------- 그래프 (패턴팀) ----------

    st.markdown('''---''')

    left_column, right_column = st.columns(2)
    fig1 = px.bar(df_patt_M,
                x='봉제업체',
                y='작업율',
                color='복종',
                title=f'{choosen_season_pt} 타입대비 패턴 현황 (남)',
                text='작업율(%)',
                # markers=True,
                # facet_row='시즌',
                height=400,
                template='plotly_white'
                )
    fig1.update_layout(plot_bgcolor="rgba(0,0,0,0)",)
    fig1.update_traces(textposition='inside', textfont_size=14)

    fig2 = px.bar(df_patt_F,
                x='봉제업체',
                y='작업율',
                color='복종',
                title=f'{choosen_season_pt} 타입대비 패턴 현황 (여)',
                text='작업율(%)',
                # markers=True,
                # facet_row='시즌',
                height=400,
                template='plotly_white'
                )
    fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)",)
    fig2.update_traces(textposition='inside', textfont_size=14)

    left_column.plotly_chart(fig1, use_container_width=True)
    right_column.plotly_chart(fig2, use_container_width=True)


    # 특이사항
    st.markdown(patt.main_text)


# ---------------------------------------------------- 디자인팀 ----------------------------------------------------

if department == '디자인팀':
    st.title('디자인팀 주간업무 보고')
    st.subheader(f"주요업무 ({this_mon} ~ {this_fri})")
    st.markdown(design.main_text)


# ---------------------------------------------------- 마케팅팀 ----------------------------------------------------

if department == '마케팅팀':
    st.title('마케팅팀 주간업무 보고')
    st.subheader(f"주요업무 ({this_mon} ~ {this_fri})")
    st.markdown(mark.main_text)


# ---------------------------------------------------- 영업팀 ----------------------------------------------------

if department == '영업팀':
    st.title('영업팀 주간업무 보고')
    st.subheader(f"주요업무 ({this_mon} ~ {this_fri})")
    st.markdown('''---''')


    # SQLITE3 DB 파일명
    sales_sql_1 = f'''
    select * from sales_suju_haje_t
    '''

    # SQLITE3 DB 파일명
    db_file = 'daliy_order.db'

    # 기본 데이터프레임 만들기
    df_sales_base = mod.connect_sqlite3(db_file, sales_sql_1)


    # ---------- 사이드바 (영업팀) ----------

    st.sidebar.header('시즌')

    # 사이드바 시즌 선택
    choosen_season_sales = st.sidebar.selectbox(
        '시즌을 선택하세요 : ',
        options=['N시즌', 'S시즌', 'F시즌'],
    )

    st.sidebar.header('낙찰조건')
    query_date = st.sidebar.date_input('기준계약일자를 선택하세요 : ', datetime.strptime(last_fri, "%Y/%m/%d")) # 지난주 금요일
    query_date_j = (datetime.combine(query_date, time()) - timedelta(weeks=1)).date() # 선택한 날짜에서 1주전



    
    if choosen_season_sales == 'N시즌':
        season_list: list = [x for x in (df_sales_base['시즌'].unique()) if x[-1]=='N'][-2:]
    elif choosen_season_sales == 'S시즌':
        season_list: list = [x for x in (df_sales_base['시즌'].unique()) if x[-1]=='S'][-2:]
    elif choosen_season_sales == 'F시즌':
        season_list: list = [x for x in (df_sales_base['시즌'].unique()) if x[-1]=='F'][-2:]

    df_sales = sales.make_season_data(df_sales_base, season_list) # 베이스 데이터, 선택된 시즌

    # 최종 주차, 수주량 합계, 해제량 합계, 주간 수주량, 주간 해제량, 전주 수주량, 전주 해제량
    week, week_suju_sum, week_haje_sum, j_week_suju_sum, j_week_haje_sum, week_suju_qty, week_haje_qty, j_week_suju_qty, j_week_haje_qty = sales.make_arg(df_sales)



    # ---------- 메인페이지 (영업팀) ----------

    st.markdown('### 주간 현황판')

    left_column, middle1_column, middle2_column, right_column = st.columns(4)
    with left_column:
        st.metric('수주량 합계', week_suju_sum, delta=f'{week_suju_sum - j_week_suju_sum}', delta_color="normal", help=f'전주 수주량 합계 : {j_week_suju_sum}')
    with middle1_column:
        st.metric('해제량 합계', week_haje_sum, delta=f'{week_haje_sum - j_week_haje_sum}', delta_color="normal", help=f'전주 해제량 합계 : {j_week_haje_sum}')
    with middle2_column:
        st.metric('수주 변동량', week_suju_qty, delta=f'{week_suju_qty - j_week_suju_qty}', delta_color="normal", help=f'전주 수주 변동량 : {j_week_suju_qty}')
    with right_column:
        st.metric('해제 변동량', week_haje_qty, delta=f'{week_haje_qty - j_week_haje_qty}', delta_color="normal", help=f'전주 해제 변동량 : {j_week_haje_qty}')
    

    st.markdown('''---''')


    # ---------- 그래프 (영업팀) ----------

    fig1 = px.line(df_sales,
                y=['수주량', '해제량'],
                color='상권',
                # title=f'{season_list} 시즌 상권별 수주/해제 현황',
                # text='주차',
                markers=True,
                facet_row='시즌',
                height=700,
                # template='plotly_white'
                )

    fig1.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
    )

    # fig1.update_xaxes(rangeslider_visible=True) # 슬라이드 조절바


    # ---------- 낙찰현황 데이터 ----------

    df_sales_base_bid = mod.select_data(sales.make_sql(max(season_list), query_date)) # 베이스
    df_sales_base_bid_j = mod.select_data(sales.make_sql(max(season_list), query_date_j)) # 베이스 (1주일전)
    

    df_sales_bid, df_sales_bid_graph = sales.make_bid_data(df_sales_base_bid.copy(), max(season_list))
    df_sales_bid_j, df_sales_bid_graph_j = sales.make_bid_data(df_sales_base_bid_j.copy(), max(season_list)) # 1주일전
    
    


    # ---------- 그래프 (영업팀) ----------

    fig2 = px.sunburst(df_sales_bid_graph,
                path=['시즌', '업체구분', '특약명'],
                values='학생수',
                color='업체구분',
                # title=f'{season_list} 시즌 상권별 수주/해제 현황',
                height=600,
                template='plotly_white'
                )

    fig2.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        margin = dict(t=0, l=0, r=0, b=0),
        uniformtext=dict(minsize=10, mode='hide'),
    )


    fig3 = px.sunburst(df_sales_bid_graph,
                path=['업체구분', '특약명', '시즌'],
                values='학생수',
                color='업체구분',
                # title=f'{season_list} 시즌 상권별 수주/해제 현황',
                height=600,
                template='plotly_white'
                )

    fig3.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        margin = dict(t=0, l=0, r=0, b=0),
        uniformtext=dict(minsize=10, mode='hide'),
    )


    # ---------- 탭 (영업팀) ----------

    tab1, tab2, tab3 = st.tabs(['수주현황', '상권별수주', '낙찰현황'])

    with tab1:
        st.subheader(f'{season_list} 수주량, 해제량 시즌 비교')
        st.plotly_chart(fig1, use_container_width=True)

    with tab2:
        st.subheader('상권별수주')
        st.image("https://static.streamlit.io/examples/dog.jpg", width=200)

    with tab3:
        st.subheader('낙찰현황')
        # st.write(df_sales_bid, width=None, height=None)
        # st.write(df_sales_bid_j, width=None, height=None)
        # st.write((df_sales_bid - df_sales_bid_j).iloc[-1], width=None, height=None) # 주간 차이
        # st.write(df_sales_bid.iloc[-1] - df_sales_bid.iloc[-2], width=None, height=None) # 연간 차이
        
        st.write(sales.make_bid_data2(df_sales_bid, df_sales_bid_j, season_list), width=None, height=None) # 연간 차이

        left_column, right_column = st.columns(2)
        left_column.plotly_chart(fig2, use_container_width=True)
        right_column.plotly_chart(fig3, use_container_width=True)

        


        # st.write(season_list)

        

    # ---------- 낙찰현황 ----------

    



    st.markdown('### 상권별 수주량, 해제량 시즌 비교')


    
    
    st.markdown('''---''')

    st.dataframe(df_sales)

    st.markdown(sales.main_text)


    # start_date = st.sidebar.date_input('시작일자', datetime(2022, 1, 1))
    # end_date = st.sidebar.date_input('종료일자', datetime(2022, 8, 10))


# ---------------------------------------------------- 생산팀 ----------------------------------------------------

if department == '생산팀':
    st.title('생산팀 주간업무 보고')
    st.subheader(f"주요업무 ({this_mon} ~ {this_fri})")
    st.markdown('''---''')


    # 조회조건 변수들
    bok_gb = '1' # 복종구분   1: 대표복종합치기, 2: 복종별보기
    qty_gb = '2' # 수량구분   1: 수주 건수, 2: 수주 수량
    prod_quota = ['22F', '22W', '23N'] # 이번 시즌 쿼터
    
    # 지난 시즌 쿼터
    j_prod_quota = [ str(int(prod_quota[0][:2])-1)+prod_quota[0][-1], str(int(prod_quota[1][:2])-1)+prod_quota[1][-1], str(int(prod_quota[2][:2])-1)+prod_quota[2][-1] ]

    prod_gbn = '*' # 수주구분   *: 전체, M: 메인, G: 기획제품, H: 샘플뱅크, S: 샘플수주
    prod_dt = datetime.today().strftime("%Y%m%d")
    j_prod_dt = str(int(prod_dt[:4])-1) + prod_dt[4:]
    prod_tkyk = '*' # 특약   *: 전체, C: 서울상권, D: 대전상권, H: 중부상권, I: 대구상권, L: 광주상권, R: 부산상권
    prod_tkyk2 = '*' # 상권   *: 전체, A: 서울A, B: 서울B, D:대전상권, E: 광주상권, F: 대구상권, G: 부산상권, H: 중부A, I: 본사, J: 중부B, W: 기타, Z: 없음


    # SQL문 만들기
    prod_sql_1 = prod.make_sql(bok_gb, qty_gb, prod_quota, j_prod_quota, prod_gbn, prod_dt, j_prod_dt, prod_tkyk, prod_tkyk2)

    # 기본 데이터프레임 만들기
    df_prod_base = mod.select_data(prod_sql_1)

    # 전처리 (남, 여 반환)
    df_prod = prod.data_preprocess(df_prod_base)


    # ---------- 그래프 (생산팀) ----------

    fig1 = px.bar(df_prod.query("성별 == '남'"),
                x='복종',
                y='출고율',
                color='복종',
                title=f'남',
                # text='출고율',
                text=df_prod.query("성별 == '남'")['출고율'].apply(lambda x: '{0:1.0f}%'.format(x)),
                # markers=True,
                # facet_col='성별',
                height=400,
                template='plotly_white'
                )
    fig1.update_layout(plot_bgcolor="rgba(0,0,0,0)",)
    fig1.update_traces(textposition='inside', textfont_size=14)

    # 여자
    fig2 = px.bar(df_prod.query("성별 == '여'"),
                x='복종',
                y='출고율',
                color='복종',
                title=f'여',
                # text='출고율',
                text=df_prod.query("성별 == '여'")['출고율'].apply(lambda x: '{0:1.0f}%'.format(x)),
                # markers=True,
                # facet_col='성별',
                height=400,
                template='plotly_white'
                )
    fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)",)
    fig2.update_traces(textposition='inside', textfont_size=14)

    # 공통
    fig3 = px.bar(df_prod.query("성별 == '공통'"),
                x='복종',
                y='출고율',
                color='복종',
                title=f'공통',
                # text='출고율',
                text=df_prod.query("성별 == '공통'")['출고율'].apply(lambda x: '{0:1.0f}%'.format(x)),
                # markers=True,
                # facet_col='성별',
                height=400,
                template='plotly_white'
                )
    fig3.update_layout(plot_bgcolor="rgba(0,0,0,0)",)
    fig3.update_traces(textposition='inside', textfont_size=14)



    st.markdown("### ◆ 23년 동복 생산진행 현황 (22F/23N)")
    st.markdown(f"##### [동복 / 대리점 HOLD 포함] - 실시간")

    left_column, middle_column, right_column = st.columns(3)

    left_column.dataframe(df_prod.query("성별 == '남'"), width=None, height=None)
    middle_column.dataframe(df_prod.query("성별 == '여'"), width=None, height=None)
    right_column.dataframe(df_prod.query("성별 == '공통'"), width=None, height=None)

    st.dataframe(df_prod.query("성별 == ['자켓기준', '하의기준']"), width=None, height=None)

    st.markdown('''---''')

    left_column, middle_column, right_column = st.columns(3)

    left_column.plotly_chart(fig1, use_container_width=True)
    middle_column.plotly_chart(fig2, use_container_width=True)
    right_column.plotly_chart(fig3, use_container_width=True)

    st.markdown('''---''')


    # 업체별 동복 자켓 진행 현황
    st.markdown("### ◆ 업체별 동복 자켓 진행 현황")
    left_column, right_column = st.columns(2)

    ivy_type_qty = df_prod.query("성별 == '자켓기준'").at[14, '타입'] # 아이비 타입량
    ivy_product= df_prod.query("성별 == '자켓기준'").at[14,'완료'] # 아이비 생산량

    df_major4, df_major4_graph = prod.make_major4_frame(ivy_type_qty, ivy_product)
    
    left_column.write(df_major4, width=None, height=None)
    # left_column.table(df_major4)


    # 4사 그래프
    fig4 = px.bar(df_major4_graph,
                x = '업체',
                y = '수량',
                color='구분',
                title=f'4사 진행 현황',
                text='수량',
                # markers=True,
                # facet_col='성별',
                barmode='group',
                height=400,
                template='plotly_white'
                )
    fig4.update_layout(plot_bgcolor="rgba(0,0,0,0)")
    fig4.update_traces(textposition='inside', textfont_size=14)

    right_column.plotly_chart(fig4, use_container_width=True)

    
    # 생산진행 관련
    st.markdown(prod.main_text)


# ---------------------------------------------------- 구매팀 ----------------------------------------------------

if department == '구매팀':
    st.title('구매팀 주간업무 보고')
    st.subheader(f"주요업무 ({this_mon} ~ {this_fri})")
    st.markdown('''---''')

    # ---------- 사이드바 (구매팀) ----------
    st.sidebar.header('시즌')

    # 사이드바 시즌 선택
    choosen_season_pur = st.sidebar.selectbox(
        '시즌을 선택하세요 : ',
        options=['23F', '23S'],
    )
    
    # 사이드바 2
    st.sidebar.header('제품')

    # 사이드바 제품 선택
    choosen_jaepum_pur = st.sidebar.selectbox(
        '제품을 선택하세요 : ',
        options=['학생복원단', '체육복원단'],
    )
    
    # 제품 코드 지정
    if choosen_jaepum_pur == '학생복원단':
        jaepum_pur = 'H'
    elif  choosen_jaepum_pur == '체육복원단':
        jaepum_pur = 'F'


    # ---------- 메인페이지 (구매팀) ----------

    st.markdown("### [원자재]")
    st.markdown(f"##### [{choosen_season_pur} {choosen_jaepum_pur} 진행현황]")


    # SQL문 만들기
    pur_sql_1, pur_sql_2 = pur.make_sql(choosen_season_pur[:3], choosen_season_pur[-3:], jaepum_pur)

    # 기본 데이터프레임 만들기
    df_pur_base_1 = mod.select_data(pur_sql_1)
    df_pur_base_2 = mod.select_data(pur_sql_2)
    # 위의 데이터프레임은 streamlit으로 출력 안됨. 컬럼명 길이 제한이 있는 듯.
    
    # 전처리 (astype 후 concat)
    df_pur_base = pur.data_preprocess(df_pur_base_1, df_pur_base_2)

    # merge 할 CPC 표 (기초코드 36)
    df_cpc_list = mod.select_data(pur.soje_cpc_sql)

    # merge 작업 (체육복 원단쪽엔 E 없음)
    df_pur_base2, df_pur_base2_E = pur.data_preprocess2(df_pur_base, df_cpc_list, choosen_season_pur[-1], jaepum_pur) # 원본, 머지테이블, 시즌(동하복), 제품(학,체)

    # 세부 전처리 (시즌토탈, 월별계)
    df_pur_base3, df_pur_base3_sum = pur.data_preprocess3(df_pur_base2)

    # 그래프용 melt (음수처리)
    df_pur_base4 = pur.data_preprocess4(df_pur_base3)



    # ---------- 그래프 (구매팀) ----------

    # fig1 = px.bar(df_pur_base3,
    #             x='복종',
    #             y='출고율',
    #             color='복종',
    #             title=f'남',
    #             # text='출고율',
    #             # text=df_prod.query("성별 == '남'")['출고율'].apply(lambda x: '{0:1.0f}%'.format(x*100)),
    #             # markers=True,
    #             # facet_col='성별',
    #             height=400,
    #             template='plotly_white'
    #             )
    # fig1.update_layout(plot_bgcolor="rgba(0,0,0,0)",)
    # fig1.update_traces(textposition='inside', textfont_size=14)

    # Icicle 차트
    cm: dict = {'(?)': 'lightgrey', '미입고량': 'rgb(228,26,28)', '발주량': 'rgb(77,175,)', '입고량': 'rgb(55,126,184)'}
    fig2 = px.icicle(df_pur_base4,
                path=[px.Constant('전체 (전년 + 올해)'), '발주시즌', '구분', '종류', '원단량'],
                values='원단량',
                title=f'전년도 대비 비교 (Icicle 차트)',
                color='종류',
                color_discrete_map=cm,
                maxdepth=5,
                height=600,
                )
    
    fig2.update_layout(margin = dict(t=50, l=25, r=25, b=25), uniformtext=dict(minsize=14, mode='hide'), iciclecolorway = ["pink", "lightgray"])
    # fig2.update_traces(sort=False)
        

    left_column, right_column = st.columns(2)
    left_column.write(df_pur_base3[df_pur_base3['발주시즌'] == (str(int(choosen_season_pur[:2])-1)+choosen_season_pur[-1])], width=None, height=None)
    right_column.write(df_pur_base3[df_pur_base3['발주시즌'] == choosen_season_pur], width=None, height=None)
    
    st.markdown('''---''')
    
    # 합계
    left_column.table(df_pur_base3_sum[df_pur_base3_sum['발주시즌'] == (str(int(choosen_season_pur[:2])-1)+choosen_season_pur[-1])])
    right_column.table(df_pur_base3_sum[df_pur_base3_sum['발주시즌'] == choosen_season_pur])

    st.plotly_chart(fig2, use_container_width=True)

    # st.write(df_pur_base4, width=None, height=None)

    st.markdown(pur.main_text)


# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
