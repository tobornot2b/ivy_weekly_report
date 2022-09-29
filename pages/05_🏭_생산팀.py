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


# -------------------- 함수 (생산팀) --------------------

# 타사자료 입력
S_E_L_type_qty: list = [34000, 26000, 22000]
S_E_L_chulgo_qty: list = [15000, 13000, 9000]


# 생산팀 SQL문
@st.cache
def make_sql(bok_gb: str, qty_gb: str, prod_quota: list, j_prod_quota: list, prod_gbn: str, prod_dt: str, j_prod_dt, prod_tkyk: str, prod_tkyk2: str) -> str:
    sql = f'''
    SELECT z.master_jaepum,
            z.sex,
            Min(z.sort)                sort,
            z.master_bokjong,
            Max(z.sh_gb)               sh_gb,
            SUM(Nvl(z.qty_01, 0))      qty_01,
            SUM(Nvl(z.qty_03, 0))      qty_03,
            SUM(Nvl(z.qty_04, 0))      qty_04,
            SUM(Nvl(z.qty_05, 0))      qty_05,
            SUM(Nvl(z.app_end_qty, 0)) app_end_qty,
            SUM(Nvl(z.qty_10, 0))      qty_10,
            SUM(Nvl(z.qty_11, 0))      qty_11,
            SUM(Nvl(z.qty_12, 0))      qty_12,
            SUM(Nvl(z.qty_13, 0))      qty_13,
            SUM(Nvl(z.qty_14, 0))      qty_14,
            SUM(Nvl(z.qty_15, 0))      qty_15,
            SUM(Nvl(z.qty_20, 0))      qty_20,
            SUM(Nvl(z.qty_30, 0))      qty_30,
            SUM(Nvl(z.qty_40, 0))      qty_40,
            SUM(Nvl(z.qty_50, 0))      qty_50,
            SUM(Nvl(z.qty_55, 0))      qty_55,
            SUM(Nvl(z.qty_60, 0))      qty_60,
            SUM(Nvl(z.pt_save_gb, 0))  pt_save_gb,
            SUM(Nvl(z.j_suju_qty, 0))  j_suju_qty,
            SUM(Nvl(z.j_hc_qty, 0))    j_hc_qty
        FROM   (SELECT master_jaepum,
                    Decode(master_sex, 'A', '1',
                                        'B', '2',
                                        'C', '1',
                                        'D', '2',
                                        'E', '1',
                                        'F', '2',
                                        'G', '1',
                                        'H', '2')                               sex,
                    sort,
                    cod_etc2                                                   AS
                    sh_gb,
                    Decode('{bok_gb}', '1', cod_ceo_etc,
                                        master_bokjong)                         AS
                            master_bokjong,
                    Decode('{qty_gb}', '1', Decode(master_status, '01', 1,
                                                                    0),
                                        Decode(master_status, '01', master_suju_qty,
                                                                0))               qty_01
                    ,
                    Decode('{qty_gb}', '1',
                    Decode(master_status, '03', 1,
                                            0),
                                        Decode(master_status, '03', master_suju_qty,
                                                                0))               qty_03
                    ,
                    Decode('{qty_gb}', '1',
                    Decode(master_status, '04', 1,
                                            0),
                                        Decode(master_status, '04', master_suju_qty,
                                                                0))               qty_04
                    ,
                    Decode('{qty_gb}', '1', Decode(master_appv_end_gb
                                            , 'Y', 1,
                                                0),
                                        Decode(master_appv_end_gb, 'Y',
                                        master_suju_qty,
                                                                    0))
                    app_end_qty,
                    Decode('{qty_gb}', '1', Decode(master_status, '05', 1,
                                                                    0),
                                        Decode(master_status, '05', master_suju_qty,
                                                                0))               qty_05
                    ,
                    Decode('{qty_gb}', '1',
                    Decode(master_status, '10', 1,
                                            0),
                                        Decode(master_status, '10', master_suju_qty,
                                                                0))               qty_10
                    ,
                    Decode('{qty_gb}', '1',
                    Decode(master_status, '11', 1,
                                            0),
                                        Decode(master_status, '11', master_suju_qty,
                                                                0))               qty_11
                    ,
                    Decode('{qty_gb}', '1',
                    Decode(master_status, '12', 1,
                                            0),
                                        Decode(master_status, '12', master_suju_qty,
                                                                0))               qty_12
                    ,
                    Decode('{qty_gb}', '1',
                    Decode(master_status, '13', 1,
                                            0),
                                        Decode(master_status, '13', master_suju_qty,
                                                                0))               qty_13
                    ,
                    Decode('{qty_gb}', '1',
                    Decode(master_status, '14', 1,
                                            0),
                                        Decode(master_status, '14', master_suju_qty,
                                                                0))               qty_14
                    ,
                    Decode('{qty_gb}', '1',
                    Decode(master_status, '15', 1,
                                            0),
                                        Decode(master_status, '15', master_suju_qty,
                                                                0))               qty_15
                    ,
                    Decode('{qty_gb}', '1',
                    Decode(master_status, '20', 1,
                                            0),
                                        Decode(master_status, '20', master_suju_qty,
                                                                0))               qty_20
                    ,
                    Decode('{qty_gb}', '1',
                    Decode(master_status, '30', 1,
                                            0),
                                        Decode(master_status, '30', master_suju_qty,
                                                                0))               qty_30
                    ,
                    Decode('{qty_gb}', '1',
                    Decode(master_status, '40', 1,
                                            0),
                                        Decode(master_status, '40', master_suju_qty,
                                                                0))               qty_40
                    ,
                    Decode('{qty_gb}', '1',
                    Decode(master_status, '50', 1,
                                            0),
                                        Decode(master_status, '50', master_suju_qty,
                                                                0))               qty_50
                    ,
                    Decode('{qty_gb}', '1',
                    Decode(master_status, '55', 1,
                                            0),
                                        Decode(master_status, '55', master_suju_qty,
                                                                0))               qty_55
                    ,
                    Decode('{qty_gb}', '1',
                    Decode(master_status, '60', 1,
                                            0),
                                        Decode(master_status, '60', master_suju_qty,
                                                                0))               qty_60
                    ,
                    Decode(Sign(master_status - '50'), -1, 0,
                    Decode('{qty_gb}', '1',
                    Decode(
                    Decode(
                    Decode('{bok_gb}', '1', cod_ceo_etc,
                        master_bokjong), 'G', 'Y',
                                        'K', 'Y',
                                        'T', 'Y',
                                        'X', 'Y',
                                        master_pt_save_gb),
                                                        'Y', 1,
                                                        0),
                                                                            Decode(
                                                        Decode(
                    Decode('{bok_gb}', '1', cod_ceo_etc,
                                        master_bokjong),
                                                        'G', 'Y',
                                                        'K', 'Y',
                                                        'T', 'Y',
                                                        'X', 'Y',
                                                        master_pt_save_gb), 'Y',
                    master_suju_qty
                                                                            ,
                                                                            0)))
                    pt_save_gb,
                    0                                                          AS
                    j_suju_qty
                            ,
                    0
                            AS j_hc_qty
                FROM   i_suju_master_t,
                    i_agen_t,
                    i_cod_t
                WHERE  master_agent = agen_code
                    AND master_status <> '00'
                    AND master_quota IN ( {str(prod_quota)[1:-1]} )
                    AND master_jaepum IN ( 'H', 'F' )
                    AND ( '*' = '{prod_gbn}'
                            OR master_remake = '{prod_gbn}' )
                    AND ( '*' = '{prod_tkyk}'
                            OR master_tkyk = '{prod_tkyk}' )
                    AND ( '*' = '{prod_tkyk2}'
                            OR agen_tkyk2 = '{prod_tkyk2}' )
                    AND master_bokjong = cod_code
                    AND cod_gbn_code = '01'
                    AND master_suju_date <= To_date('{prod_dt}', 'yyyymmdd')
                UNION ALL
                SELECT master_jaepum,
                    Decode(master_sex, 'A', '1',
                                        'B', '2',
                                        'C', '1',
                                        'D', '2',
                                        'E', '1',
                                        'F', '2',
                                        'G', '1',
                                        'H', '2')        sex,
                    sort,
                    cod_etc2                            AS sh_gb,
                    Decode('{bok_gb}', '1', cod_ceo_etc,
                                        master_bokjong)  AS master_bokjong,
                    0                                   qty_01,
                    0                                   qty_03,
                    0                                   qty_04,
                    0                                   app_end_qty,
                    0                                   qty_05,
                    0                                   qty_10,
                    0                                   qty_11,
                    0                                   qty_12,
                    0                                   qty_13,
                    0                                   qty_14,
                    0                                   qty_15,
                    0                                   qty_20,
                    0                                   qty_30,
                    0                                   qty_40,
                    0                                   qty_50,
                    0                                   qty_55,
                    0                                   qty_60,
                    0                                   pt_save_gb,
                    Decode('{qty_gb}', '1', 1,
                                        master_suju_qty) AS j_suju_qty,
                    Decode(master_appv_end_gb, 'Y', ( CASE
                                                        WHEN master_appv_end_dt <=
                    To_date('{j_prod_dt}', 'YYYYMMDD')
                                                        THEN
                    Decode('{qty_gb}', '1', 1,
                                        master_suju_qty)
                    ELSE 0
                                                        END ),
                                                0)       AS j_hc_qty
                FROM   i_suju_master_t,
                    i_agen_t,
                    i_cod_t
                WHERE  master_agent = agen_code
                    AND master_status = '60'
                    AND master_quota IN ( {str(j_prod_quota)[1:-1]} )
                    AND master_jaepum IN ( 'H', 'F' )
                    AND ( '*' = '{prod_gbn}'
                            OR master_remake = '{prod_gbn}' )
                    AND ( '*' = '{prod_tkyk}'
                            OR master_tkyk = '{prod_tkyk}' )
                    AND ( '*' = '{prod_tkyk2}'
                            OR agen_tkyk2 = '{prod_tkyk2}' )
                    AND master_bokjong = cod_code
                    AND cod_gbn_code = '01') z
        GROUP  BY z.master_jaepum,
                z.sex,
                z.master_bokjong
    '''
    return sql

# 전처리 함수
@st.cache
def data_preprocess(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = ['제품', '성별', '정렬', '복종', '상하의', 'ST01', 'ST03', 'ST04', 'ST05',
                   '영업확정', 'ST10', 'ST11', 'ST12', 'ST13', 'ST14',
                   'ST15', 'ST20', 'ST30', 'ST40', 'ST50', 'ST55', 'ST60',
                   '패턴출고', '전시즌최종수주', '전시즌영업확정']

    df['제품'] = df['제품'].str.replace('H', '학생복').replace('F', '체육복')
    df['성별'] = df['성별'].str.replace('1', '남').replace('2', '여')


    df1 = df.sort_values(['제품', '성별', '정렬', '복종'], ascending=[False, True, True, True]).reset_index(drop=True)
    df1['정렬'] = pd.Series([11, 12, 13, 31, 32, 33, 99, 35, 34, 21, 22, 24, 23, 31, 32, 33, 99, 35, 34, 36, 99, 37, 36, 99, 37])
    df1 = df1.sort_values(['정렬', '성별']).reset_index(drop=True)
    df1 = df1[df1['정렬'] != 99].copy()


    df_temp = df_common = pd.DataFrame()

    for bok in list(df1.query('정렬 > 30')['복종'].unique()):
        df_temp = df1[df1['복종'] == bok].iloc[0] + df1[df1['복종'] == bok].iloc[1]
        df_common = pd.concat([df_common, df_temp], axis=1)

    # 자켓기준
    df_temp = df1[df1['복종'] == 'J'].iloc[0] + df1[df1['복종'] == 'J'].iloc[1]
    df_common = pd.concat([df_common, df_temp], axis=1)

    # 하의기준
    df_temp = df1.query("복종 == ['P', 'S']").sum()
    df_common = pd.concat([df_common, df_temp], axis=1)

    df_common = df_common.T
    df_common['제품'] = df_common['제품'].str[:3]
    df_common['성별'] = '공통'
    df_common['정렬'] = df_common['정렬'] / 2
    df_common['정렬'] = df_common['정렬'].astype(int)
    df_common['복종'] = df_common['복종'].str[0]
    df_common['상하의'] = df_common['상하의'].str[0]

    df_prod_report = pd.concat([df1.query('정렬 < 30'), df_common]).reset_index(drop=True)

    df_prod_report.iat[-1, 1] = '하의기준'
    df_prod_report.iat[-2, 1] = '자켓기준'
    df_prod_report.iloc[-1, 2:5] = ''
    df_prod_report.iloc[-2, 2:5] = ''


    df_prod_report['홀드'] = df_prod_report['ST01'] + df_prod_report['ST03'] + df_prod_report['ST04']
    df_prod_report['본사'] = df_prod_report['ST05'] + df_prod_report['ST10'] + df_prod_report['ST11'] + df_prod_report['ST12'] + df_prod_report['ST13'] + df_prod_report['ST14'] + df_prod_report['ST15']
    df_prod_report['원단'] = df_prod_report['ST20']
    df_prod_report['타입'] = df_prod_report['ST50'] + df_prod_report['ST55'] + df_prod_report['ST60']
    df_prod_report['완료'] = df_prod_report['ST60']
    df_prod_report['출고율'] = df_prod_report['완료'] / df_prod_report['타입'] * 100
    
    df_prod_report2 = df_prod_report[['성별', '복종', '홀드', '본사', '원단', '타입', '완료', '출고율']]

    return df_prod_report2



# 업체별 동복 자켓 진행 현황
@st.cache
def make_major4_frame(ivy_type_qty: int, ivy_product: int) -> pd.DataFrame:
    A = ['타입', ivy_type_qty] + S_E_L_type_qty # 타사자료 입력
    B = ['출고', ivy_product] + S_E_L_chulgo_qty
    C = ['출고율(%)', (ivy_product*100)//ivy_type_qty, (B[2]*100)//A[2], (B[3]*100)//A[3], (B[4]*100)//A[4]]

    df_major4 = pd.DataFrame([A, B, C])
    df_major4.columns = ['구분', '아이비클럽', '스마트', '엘리트', '스쿨룩스']
    # df_major4_graph = df_major4.copy().set_index('구분') # 그래프용
    df_major4_graph = df_major4.copy()
    df_major4_graph = df_major4_graph.melt(id_vars='구분', var_name='업체', value_name='수량')
    # df_major4_graph = groupby(['업체'])[['수량']]

    df_major4['차이(스마트)'] = df_major4['스마트'] - df_major4['아이비클럽']
    df_major4['차이(엘리트)'] = df_major4['엘리트'] - df_major4['아이비클럽']
    df_major4['차이(스쿨룩스)'] = df_major4['스쿨룩스'] - df_major4['아이비클럽']

    df_major4 = df_major4[['구분', '아이비클럽', '스마트', '차이(스마트)', '엘리트', '차이(엘리트)', '스쿨룩스', '차이(스쿨룩스)']].set_index('구분')

    return df_major4, df_major4_graph



# -------------------- 사이드바 (생산팀) --------------------


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
sql_1 = make_sql(bok_gb, qty_gb, prod_quota, j_prod_quota, prod_gbn, prod_dt, j_prod_dt, prod_tkyk, prod_tkyk2)

# 기본 데이터프레임 만들기
df_base = mod.select_data(sql_1)

# 전처리 (남, 여 반환)
df_prod = data_preprocess(df_base)




# 업체별 동복 자켓 진행 현황
ivy_type_qty = df_prod.query("성별 == '자켓기준'").at[14, '타입'] # 아이비 타입량
ivy_product= df_prod.query("성별 == '자켓기준'").at[14,'완료'] # 아이비 생산량

df_major4, df_major4_graph = make_major4_frame(ivy_type_qty, ivy_product)



# -------------------- 그래프 (생산팀) --------------------

colors2 = {'(?)': 'RGB(254,217,166)', '아이비클럽': '#54A24B', '스마트': '#4C78A8', '엘리트': '#E45756', '스쿨룩스': '#EECA3B', '일반업체': '#BAB0AC'}

fig1 = px.bar(df_prod.query("성별 == ['남', '여', '공통']"),
            x='복종',
            y='출고율',
            color='복종',
            title=f'',
            text=df_prod.query("성별 == ['남', '여', '공통']")['출고율'].apply(lambda x: '{0:1.0f}%'.format(x)),
            height=500,
            )
fig1.update_layout(paper_bgcolor='rgba(233,233,233,233)', plot_bgcolor='rgba(0,0,0,0)')
fig1.update_traces(textposition='inside', textfont_size=14)


# 4사 그래프 (타입/출고)
fig2 = px.bar(df_major4_graph[df_major4_graph['구분']!='출고율(%)'],
            x='업체',
            y='수량',
            color='구분',
            title=f'4사 진행 현황 (타입량/출고량)',
            text='수량',
            barmode='group',
            height=400,
            )
fig2.update_traces(width=0.25) # 바 두께 (0 ~ 1)
fig2.update_layout(paper_bgcolor='rgba(233,233,233,233)', plot_bgcolor='rgba(0,0,0,0)')
fig2.update_traces(textposition='inside', textfont_size=14)


# 4사 그래프 (출고율)
fig3 = px.bar(df_major4_graph[df_major4_graph['구분']=='출고율(%)'],
            x='업체',
            y='수량',
            color='업체',
            color_discrete_map=colors2,
            title=f'4사 진행 현황 (출고율)',
            text='수량',
            # barmode='group',
            height=400,
            )
fig3.update_traces(width=0.25) # 바 두께 (0 ~ 1)
fig3.update_layout(paper_bgcolor='rgba(233,233,233,233)', plot_bgcolor='rgba(0,0,0,0)')
fig3.update_traces(textposition='inside', textfont_size=14)


# -------------------- 메인페이지 (생산팀) --------------------

st.markdown('#### 생산팀 주간업무 보고')
st.markdown(f'주요업무 ({mod.this_mon} ~ {mod.this_fri})')

st.markdown('##### ◆ 23년 동복 생산진행 현황 (22F/23N)')
st.markdown(f'[동복 / 대리점 HOLD 포함] - 실시간')

left_column, right_column = st.columns(2)
left_column.dataframe(df_prod, width=None, height=600)
right_column.plotly_chart(fig1, use_container_width=True)
# st.markdown('''---''')


st.markdown("##### ◆ 업체별 동복 자켓 진행 현황")

st.write(df_major4, width=None, height=None)
left_column, right_column = st.columns(2)
left_column.plotly_chart(fig2, use_container_width=True)
right_column.plotly_chart(fig3, use_container_width=True)

# st.write(df_major4_graph)

# 생산진행 관련
tab1, tab2 = st.tabs(['.', '.'])
with tab1:
    try:
        sel_text = mod.select_text(mod.db_file, datetime.strptime(mod.this_fri, '%Y/%m/%d').isocalendar()[1], '생산팀', 'text1')
    except IndexError:
        sel_text = ''

    st.markdown(sel_text)


with tab2:
    # 입력파트
    prod_text = st.text_area('1. 이번 주 내용을 입력하세요.', sel_text)
    st.write('입력된 내용 : \n', prod_text)
    
    mod.insert_text(mod.db_file, datetime.strptime(mod.this_fri, '%Y/%m/%d').isocalendar()[1], '생산팀', prod_text, 'text1')

    S_E_L_type_qty = st.text_input('2. 스마트, 엘리트, 스쿨룩스 순으로 타입량을 입력하세요.', '19000, 17000, 16000')
    st.write('입력된 값 : ', S_E_L_type_qty)

    S_E_L_chulgo_qty = st.text_input('3. 스마트, 엘리트, 스쿨룩스 순으로 출고량을 입력하세요.', '8000, 9000, 4000')
    st.write('입력된 값 : ', S_E_L_chulgo_qty)


# -------------------- HIDE STREAMLIT STYLE --------------------
hide_st_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """
st.markdown(hide_st_style, unsafe_allow_html=True)
