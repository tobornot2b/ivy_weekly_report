import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from data import * # 패키지 불러오기


# emojis: https://www.webfx.com//tools/emoji-cheat-sheet/
st.set_page_config(
    page_title='주간업무보고',
    page_icon=":chart_with_upwards_trend:",
    layout="wide"
)


# -------------------- 함수 (생산팀) --------------------

# 전역변수들

# 타사자료 입력 (동하복 둘 중 하나 선택해야 함)
S_E_L_TYPE_QTY: list = [187000, 148000, 145000]
S_E_L_CHULGO_QTY: list = [132000, 90000, 107000]

DELI_DATE_N = datetime.today().strftime('%Y-%m-%d') # 동복납기
DELI_DATE_S = '2023-05-20' # 하복납기
SPEED_DATE_N = '2022-02-01' # 동복 PEAK 시작일
SPEED_DATE_S = '2022-03-21' # 하복 PEAK 시작일
# SPEED_DATE_S = '2022-04-15' # 하복 PEAK 시작일


# 생산팀 SQL문
@st.cache_data
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
@st.cache_data
def data_preprocess(season: str, df: pd.DataFrame) -> pd.DataFrame:
    if season[-1] != 'S': # 동복
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
        
        df_prod_report2 = df_prod_report[['성별', '복종', '홀드', '본사', '원단', '타입', '완료', '출고율']].copy()

        return df_prod_report2
    else: # 하복
        df.columns = ['제품', '성별', '정렬', '복종', '상하의', 'ST01', 'ST03', 'ST04', 'ST05',
                    '영업확정', 'ST10', 'ST11', 'ST12', 'ST13', 'ST14',
                    'ST15', 'ST20', 'ST30', 'ST40', 'ST50', 'ST55', 'ST60',
                    '패턴출고', '전시즌최종수주', '전시즌영업확정']

        df['제품'] = df['제품'].str.replace('H', '학생복').replace('F', '체육복')
        df['성별'] = df['성별'].str.replace('1', '남').replace('2', '여')

        df1 = df.sort_values(['제품', '성별', '정렬', '복종'], ascending=[False, True, True, True]).reset_index(drop=True)
     
        df_prod_report = df1.query(f"복종 == ['Y', 'B']").copy() # 계산이 필요없는 Y, B 복종부터 조립 시작

        df_temp = pd.DataFrame()
        for gender in ['남', '여']:
            # P, Q
            df_temp = df1.query(f"복종 == ['P', 'Q'] and 성별 == '{gender}'").copy()
            df_temp.loc[-1] = df1.query(f"복종 == ['P', 'Q'] and 성별 == '{gender}'").sum(axis=0)
            df_temp.loc[-1, '제품':'상하의'] = ['학생복', gender, '14', 'P', 'H']
            df_prod_report.loc[f'P{gender}'] = df_temp.loc[-1].copy()

            # D, Z
            df_temp = df1.query(f"복종 == ['D', 'Z'] and 성별 == '{gender}'").copy()
            df_temp.loc[-1] = df1.query(f"복종 == ['D', 'Z'] and 성별 == '{gender}'").sum(axis=0)
            df_temp.loc[-1, '제품':'상하의'] = ['학생복', gender, '16', 'D', 'H']
            df_prod_report.loc[f'D{gender}'] = df_temp.loc[-1].copy()


        # S, R
        df_temp = df1.query(f"복종 == ['S', 'R'] and 성별 == '여'").copy()
        df_temp.loc[-1] = df1.query(f"복종 == ['S', 'R'] and 성별 == '여'").sum(axis=0)
        df_temp.loc[-1, '제품':'상하의'] = ['학생복', '여', '13', 'S', 'H']
        df_prod_report.loc['S'] = df_temp.loc[-1].copy()

        df_prod_report = df_prod_report.sort_values(['제품', '성별', '정렬'], ascending=[False, True, True]) # 일단 정렬
        
        # 공통 N
        df_temp = df1.query("복종 == 'N'").copy()
        df_temp.loc[-1] = df1.query("복종 == ['N']").sum(axis=0)
        df_temp.loc[-1, '제품':'상하의'] = ['학생복', '공통', '30', 'N', 'S']
        df_prod_report.loc['N'] = df_temp.loc[-1].copy()

        # 공통 체육복
        df_temp = df1.query("제품 == '체육복'").copy()
        df_temp.loc[-1] = df1.query("제품 == ['체육복']").sum(axis=0)
        df_temp.loc[-1, '제품':'상하의'] = ['체육복', '공통', '21', 'F', '*']
        df_prod_report.loc['F'] = df_temp.loc[-1].copy()

        # 상의기준
        df_temp = df1.query("상하의 == 'S'").copy()
        df_temp.loc[-1] = df1.query("상하의 == 'S'").sum(axis=0)
        df_temp.loc[-1, '제품':'상하의'] = ['학생복', '상의기준', '98', '', 'S']
        df_prod_report.loc['상의'] = df_temp.loc[-1].copy()

        # 하의기준
        df_temp = df1.query("상하의 == 'H'").copy()
        df_temp.loc[-1] = df1.query("상하의 == 'H'").sum(axis=0)
        df_temp.loc[-1, '제품':'상하의'] = ['학생복', '하의기준', '99', '', 'H']
        df_prod_report.loc['하의'] = df_temp.loc[-1].copy()

        df_prod_report = df_prod_report.reset_index(drop=True)

        df_prod_report['홀드'] = df_prod_report['ST01'] + df_prod_report['ST03'] + df_prod_report['ST04']
        df_prod_report['본사'] = df_prod_report['ST05'] + df_prod_report['ST10'] + df_prod_report['ST11'] + df_prod_report['ST12'] + df_prod_report['ST13'] + df_prod_report['ST14'] + df_prod_report['ST15']
        df_prod_report['원단'] = df_prod_report['ST20']
        df_prod_report['타입'] = df_prod_report['ST50'] + df_prod_report['ST55'] + df_prod_report['ST60']
        df_prod_report['완료'] = df_prod_report['ST60']
        df_prod_report['출고율'] = df_prod_report['완료'] / df_prod_report['타입'] * 100
        
        df_prod_report2 = df_prod_report[['성별', '복종', '홀드', '본사', '원단', '타입', '완료', '출고율']].copy()

        return df_prod_report2


# 전처리 함수2 (상세)
@st.cache_data
def data_preprocess2(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = ['제품', '성별', '정렬', '복종', '상하의', 'ST01', 'ST03', 'ST04', 'ST05',
                   '영업확정', 'ST10', 'ST11', 'ST12', 'ST13', 'ST14',
                   'ST15', 'ST20', 'ST30', 'ST40', 'ST50', 'ST55', 'ST60',
                   '패턴출고', '전시즌최종수주', '전시즌영업확정']

    df['제품'] = df['제품'].str.replace('H', '학생복').replace('F', '체육복')
    df['성별'] = df['성별'].str.replace('1', '남').replace('2', '여')

    df = df[[
        '제품', '성별', '정렬', '복종', '상하의',
        'ST01', 'ST03', 'ST04',
        'ST05', 'ST10', 'ST11', 'ST12', 'ST13', 'ST14', 'ST15', 'ST20',
        'ST30', 'ST40', 'ST50', 'ST55', 'ST60',
        '영업확정', '패턴출고', '전시즌최종수주', '전시즌영업확정',
        ]]
    
    df1 = df.sort_values(['제품', '성별', '정렬', '복종'], ascending=[False, True, True, True]).reset_index(drop=True)

    return df1.drop(['정렬', '상하의', '영업확정', '패턴출고', '전시즌영업확정'], axis=1)



# 업체별 동복 자켓 진행 현황
def make_major4_frame(ivy_type_qty: int, ivy_product: int) -> pd.DataFrame:
    A = ['타입', ivy_type_qty] + S_E_L_TYPE_QTY # 타사자료 입력
    B = ['출고', ivy_product] + S_E_L_CHULGO_QTY
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


def make_deli_sql(season: str) -> str:
    sql = f'''
    SELECT j.master_quota,
           j.master_order,
           utl_raw.Cast_to_raw(t.tkyk_name) tkyk_name,
           t.sort sort1,
           j.master_bokjong,
           a.agen_code,
           utl_raw.Cast_to_raw(a.agen_name) agen_name,
           utl_raw.Cast_to_raw(Decode(j.master_jaepum, 'U', '', 'R', '', s.sch_name)) sch_name,
           utl_raw.Cast_to_raw(Decode(n.cust_name, NULL, f.fact_code, n.cust_name)) cust_name,
           utl_raw.Cast_to_raw(u.user_name) user_name,
           j.master_suju_qty,
           Nvl(j.master_prodm_qty, 0),
           j.master_status,
           Nvl(j.master_com_school, ''),
           Decode(Nvl(f.fact_hold, ''), 'H', 'Y',
                                        ''),
           --j.master_st03_date, --ST03처리일
           j.master_suju_date, --수주일
           j.master_st04_date, --수주확정
           j.master_appv_end_dt, --영업확정(납기 스타트 지점)
           j.master_repl_date, --디자인확정
           j.master_app_b_end_dt, --부자재확정
           j.master_stand_end_dt, --표준확정
           j.master_st20_dt, --원단확정(ST20)
           f.fact_date, --타입일
           f.fact_cut_date, --재단일
           f.fact_sew_date, --봉제일
           j.master_prodm_date, --생산일
           f.fact_hdate, --타입변경홀드지시일
           f.fact_cdate, --타입변경홀드해제일
           --j.master_appv_start_dt, --업무요청일자
           --j.master_sojae_mod_dt, --표준원단변경일자
           --j.master_out_date, --조기출고요청일자
           --j.master_taip, --예정타입일
           --j.master_st20_cancle_dt, --20to15취소일자
           --f.fact_issue_deli, --출고납기
           --f.fact_deli, --생산요청납기
           tt.sort sort2
    FROM   i_tkyk_t t,
           i_agen_t a,
           i_sch_t s,
           i_suju_master_t j,
           i_suju_fact_t f,
           i_user_t u,
           i_cust_t n,
           i_cod_t tt,
           i_stand_bkjk_t b
    WHERE  t.tkyk_code(+) = j.master_tkyk
           AND a.agen_code(+) = j.master_agent
           AND s.sch_code(+) = j.master_school
           AND b.bkjk_squota(+) = j.master_squota
           AND b.bkjk_school(+) = j.master_school
           AND b.bkjk_bokjong(+) = j.master_bokjong
           AND u.user_id(+) = j.master_person
           AND tt.cod_code = j.master_bokjong
           AND tt.cod_gbn_code = '01'
           AND f.fact_order(+) = j.master_order
           AND f.fact_year(+) = j.master_year
           AND f.fact_season(+) = j.master_season
           AND n.cust_code(+) = f.fact_code
           AND j.master_status >= '60'
           AND j.master_status <= '60'
           AND j.master_remake = 'M'
           AND j.master_jaepum IN( 'H', 'A', 'B', 'F' )
           AND j.master_quota IN ('{season}')
    ORDER  BY t.sort, agen_name, tt.sort
    '''
    
    return sql


def deli_calc(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [
        '시즌', '오더', '상권명', 'sort1', '복종',
        '대리점코드', '대리점명', '학교명', '봉제업체', '수주등록자',
        '수주량', '생산량', 'STATUS', '공통학교코드', '홀드', '수주일',
        '수주확정', '영업확정', '디자인확정', '부자재확정', '표준확정',
        '원단확정', '타입일', '재단일', '봉제일', '생산일',
        'T/H지시일', 'T/H해제일', 'sort2',
        ]

    # 결측값 채우기. 보통 뒷 컬럼의 날짜에 동일하거나 근접하므로 이렇게 처리함
    df['수주확정'] = df['수주확정'].mask(df['수주확정'].isnull(), df['영업확정'])
    df['부자재확정'] = df['부자재확정'].mask(df['부자재확정'].isnull(), df['표준확정'])

    df['홀드유지기간'] = df['영업확정'] - df['수주일']
    df['타입소요기간'] = df['타입일'] - df['영업확정']
    df['재봉기간'] = df['생산일'] - df['타입일']

    # streamlit 버그 대체 코드
    # dt.days를 사용하여 일자로 변환
    # 다른 방법으로는 streamlit 옵션에서 데이터프레임을 레거시 타입으로 전환하면 된다고 하는데... 싫다!
    # 날짜-날짜 타입의 기간 표시는 무조건 에러남 ->
    # 상세히 들어가면 streamlit의 JS 파트는 arrow v7을 사용하는데 여기서 알려진 공식 버그라고 함.
    # 현버전은 arrow v8

    df['홀드유지기간'] = df['홀드유지기간'].dt.days
    df['타입소요기간'] = df['타입소요기간'].dt.days
    df['재봉기간'] = df['재봉기간'].dt.days

    df_dt = df.groupby(['시즌', '복종', '봉제업체'])[['재봉기간']].describe()
    # df_dt = df_dt.stack(level=0) # 필요없는 상단 멀티컬럼 인덱스로 전환
    df_dt = df_dt.reset_index()
    # df_dt = df_dt.drop('level_2', axis=1) # 필요없는 상단 멀티컬럼 삭제


    df_dt.columns = [
        '시즌',
        '복종',
        '봉제업체',
        '오더수',
        '평균',
        '표준편차',
        '최소값',
        '25%',
        '50%',
        '75%',
        '최댓값'
        ]

    df_dt = df_dt.fillna(0) # NaN 값이 있으면 형변환 에러남
    df_dt['오더수'] = df_dt['오더수'].astype(int)
    df_dt['평균'] = df_dt['평균'].astype(int)
    df_dt['표준편차'] = df_dt['표준편차'].astype(int)
    df_dt['최소값'] = df_dt['최소값'].astype(int)
    df_dt['25%'] = df_dt['25%'].astype(int)
    df_dt['50%'] = df_dt['50%'].astype(int)
    df_dt['75%'] = df_dt['75%'].astype(int)
    df_dt['최댓값'] = df_dt['최댓값'].astype(int)

    return df_dt, df


def deli_calc_cut(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [
        '시즌', '오더', '상권명', 'sort1', '복종',
        '대리점코드', '대리점명', '학교명', '봉제업체', '수주등록자',
        '수주량', '생산량', 'STATUS', '공통학교코드', '홀드', '수주일',
        '수주확정', '영업확정', '디자인확정', '부자재확정', '표준확정',
        '원단확정', '타입일', '재단일', '봉제일', '생산일',
        'T/H지시일', 'T/H해제일', 'sort2',
        ]

    # 결측값 채우기. 보통 뒷 컬럼의 날짜에 동일하거나 근접하므로 이렇게 처리함
    df['수주확정'] = df['수주확정'].mask(df['수주확정'].isnull(), df['영업확정'])
    df['부자재확정'] = df['부자재확정'].mask(df['부자재확정'].isnull(), df['표준확정'])

    df['타입~재단'] = df['재단일'] - df['타입일']
    df['재단~봉제'] = df['봉제일'] - df['재단일']
    df['봉제~생산'] = df['생산일'] - df['봉제일']
    df['타입~생산기간'] = df['생산일'] - df['타입일']

    # streamlit 버그 대체 코드
    # dt.days를 사용하여 일자로 변환
    # 다른 방법으로는 streamlit 옵션에서 데이터프레임을 레거시 타입으로 전환하면 된다고 하는데... 싫다!
    # 날짜-날짜 타입의 기간 표시는 무조건 에러남 ->
    # 상세히 들어가면 streamlit의 JS 파트는 arrow v7을 사용하는데 여기서 알려진 공식 버그라고 함.
    # 현버전은 arrow v8

    df['타입~재단'] = df['타입~재단'].dt.days
    df['재단~봉제'] = df['재단~봉제'].dt.days
    df['봉제~생산'] = df['봉제~생산'].dt.days
    df['타입~생산기간'] = df['타입~생산기간'].dt.days

    df_dt = df.groupby(['시즌', '복종', '봉제업체'])[['타입~재단', '재단~봉제', '봉제~생산', '타입~생산기간']].agg('mean')
    df_dt = df_dt.reset_index()

    df_dt = df_dt.fillna(0) # NaN 값이 있으면 형변환 에러남
    df_dt['타입~재단'] = np.ceil(df_dt['타입~재단']).astype(int)
    df_dt['재단~봉제'] = np.ceil(df_dt['재단~봉제']).astype(int)
    df_dt['봉제~생산'] = np.ceil(df_dt['봉제~생산']).astype(int)
    df_dt['타입~생산기간'] = np.ceil(df_dt['타입~생산기간']).astype(int)

    return df_dt, df # 평균값, 오더별 원본데이터


# ----------------------------------------------------------------------------------------------
# 낙찰데이터 가져오기
def get_bid_data(bid_season: str) -> pd.DataFrame:
    sql = f'''
    select  utl_raw.Cast_to_raw(a.g2b_no) g2b_no
           ,a.g2b_year
           ,a.g2b_year2
           ,a.g2b_agency
           ,a.g2b_school
           ,TO_CHAR(a.g2b_open_yejeong_dt,'YY/MM/DD') g2b_open_yejeong_dt 
           ,TO_CHAR(a.g2b_date,'YY/MM/DD') g2b_date
           ,a.g2b_tkyk
           ,a.g2b_sch_gb
           ,a.g2b_qty
           ,utl_raw.Cast_to_raw(decode(a.g2b_co_gb,'Z',a.g2b_etc_co_nm,a.g2b_co_gb)) g2b_co_gb
           ,a.g2b_stand_amt
           ,a.g2b_stand_price
           ,a.g2b_end_amt
           ,a.g2b_end_price
           ,a.g2b_price
           ,a.g2b_n_deliv_dt
           ,a.g2b_s_deliv_dt
           ,a.g2b_season
           ,a.g2b_sch_gb2
           ,a.g2b_sch_cnt
           ,a.g2b_f_school
           ,a.g2b_m_school
           ,a.g2b_sex_gb
           ,utl_raw.Cast_to_raw(b.agen_name) agen_name
           ,utl_raw.Cast_to_raw(c.schc_name) schc_name
           ,c.schc_area
           ,a.g2b_bok_gb
           ,a.g2b_n_pcs
           ,a.g2b_s_pcs
           ,utl_raw.Cast_to_raw(a.g2b_pcs_remark) g2b_pcs_remark
           ,TO_CHAR(a.g2b_bid_begin_dt,'YY/MM/DD') g2b_bid_begin_dt
           ,TO_CHAR(a.g2b_bid_close_dt,'YY/MM/DD') g2b_bid_close_dt
           ,utl_raw.Cast_to_raw((
             SELECT CASE WHEN (Min(cod_name) <> Max(cod_name) AND SubStr(Min(cod_name),1,1) =  '*') THEN Max(cod_name)
                                 WHEN (Min(cod_name) <> Max(cod_name) AND SubStr(Min(cod_name),1,1) <> '*') THEN '2 이상' 
                         ELSE Max(cod_name) END 
              FROM i_sch_t, i_cod_t
              WHERE sch_code IN (a.G2B_M_STAND_SCHOOL,a.G2B_F_STAND_SCHOOL,a.g2b_m_school,a.g2b_f_school)
                AND cod_gbn_code    = 'SZ'
                AND sch_f_bokjong   = cod_code
           )) sch_f_bok
           ,a.g2b_end_gb
           ,a.g2b_gb
           ,c.schc_gbn3
           ,A.G2B_COM_SCH_GB
           ,(case when (sysdate - a.g2b_date) < 14 then 'N'
                  else 'Y' end) g2b_2ju_gb
           ,TO_CHAR(a.g2b_open_save_dt,'YY/MM/DD') g2b_open_save_dt 
      from i_sale_g2b_t a,i_agen_t b,i_sch_com_t c
     where b.agen_code (+)= a.g2b_agency 
       and c.schc_code (+)= a.g2b_school
       and (a.g2b_quota1 in ('{bid_season}') or a.g2b_quota2 in ('{bid_season}'))
       and a.g2b_co_gb = 'I'
       and g2b_end_gb = '9'
    '''
    
    df_bid_data = mod.select_data(sql)

    df_bid_data.columns = [
        '입찰번호', '입찰시즌1', '입찰시즌2', '대리점코드', '입찰학교코드',
        '개찰예정일자', '개찰일자', '특약코드', '남녀공학구분코드', '학생수',
        '낙찰업체', '기초금액', '기초단가', '낙찰금액', '낙찰단가',
        '낙찰단가_price', '동복납품일자', '하복납품일자', '입찰시즌', '초중고구분코드',
        '학생수_미사용', '연결학교_여', '연결학교_남', '남녀구분', '대리점명',
        '학교명', '지역코드', '낙찰복종구분_미사용', '동복복종수', '하복복종수',    
        '동하복복종수', '입찰개시일자', '입찰마감일자', '대표복종', '진행상태코드',
        '입찰구분코드', '국립사립구분코드', '표준교복_편한교복구분코드', '개찰후2주경과', '개찰일등록일자',
        ]
    
    # 남자학교
    df_bid_data_Male = df_bid_data[[
        '특약코드',
        '연결학교_남',
        '대리점코드',
        '대리점명',
        '학생수',
        '동복복종수',
        '하복복종수',
        '개찰일자',
        ]].copy()
    
    df_bid_data_Male = df_bid_data_Male[df_bid_data_Male['연결학교_남'] != 'X']
    df_bid_data_Male['개찰일자'] = '20' + df_bid_data_Male['개찰일자']
    df_bid_data_Male['개찰일자'] = df_bid_data_Male['개찰일자'].str.replace('/', '-')
    df_bid_data_Male['개찰일자_2'] = pd.to_datetime(df_bid_data_Male['개찰일자'])

    # 여자학교
    df_bid_data_Female = df_bid_data[[
        '특약코드',
        '연결학교_여',
        '대리점코드',
        '대리점명',
        '학생수',
        '동복복종수',
        '하복복종수',
        '개찰일자',
        ]].copy()

    df_bid_data_Female = df_bid_data_Female[df_bid_data_Female['연결학교_여'] != 'X']
    df_bid_data_Female['개찰일자'] = '20' + df_bid_data_Female['개찰일자']
    df_bid_data_Female['개찰일자'] = df_bid_data_Female['개찰일자'].str.replace('/', '-')
    df_bid_data_Female['개찰일자_2'] = pd.to_datetime(df_bid_data_Female['개찰일자'])


    df_bid_data_Male['연결학교'] = df_bid_data_Male['연결학교_남']
    df_bid_data_Female['연결학교'] = df_bid_data_Female['연결학교_여']
    df_merge_date = pd.concat([df_bid_data_Male, df_bid_data_Female])
    df_merge = df_merge_date[[
        '연결학교',
        '개찰일자_2',
        ]]
    df_merge = df_merge.rename(columns={
        '개찰일자_2': '개찰일자',
        '연결학교': '학교코드',
        })

    return df_merge


# 수주데이터 전체 (ST03 ~ ST60)
def get_suju_data(season: str) -> pd.DataFrame:
    sql = f'''
    SELECT j.master_order,
           utl_raw.Cast_to_raw(t.tkyk_name) tkyk_name,
           t.sort,
           j.master_bokjong,
           a.agen_code,
           utl_raw.Cast_to_raw(a.agen_name) agen_name,
           s.sch_code,
           utl_raw.Cast_to_raw(Decode(j.master_jaepum, 'U', '', 'R', '', s.sch_name)) sch_name,
           j.master_grade_cnt, -- 학년
           utl_raw.Cast_to_raw(Decode(n.cust_name, NULL, f.fact_code, n.cust_name)) cust_name,
           utl_raw.Cast_to_raw(u.user_name) user_name,
           j.master_suju_qty,
           Nvl(j.master_prodm_qty, 0),
           j.master_status,
           Nvl(j.master_com_school, ''),
           Decode(Nvl(f.fact_hold, ''), 'H', 'Y',
                                        ''),
           --j.master_st03_date, --ST03처리일
           j.master_suju_date, --수주일
           j.master_st04_date, --수주확정
           j.master_appv_end_dt, --영업확정(납기 스타트 지점)
           j.master_repl_date, --디자인확정
           j.master_app_b_end_dt, --부자재확정
           j.master_stand_end_dt, --표준확정
           j.master_st20_dt, --원단확정(ST20)
           f.fact_date, --타입일
           f.fact_cut_date, --재단일
           f.fact_sew_date, --봉제일
           j.master_prodm_date, --생산일
           f.fact_hdate, --타입변경홀드지시일
           f.fact_cdate, --타입변경홀드해제일
           --j.master_appv_start_dt, --업무요청일자
           --j.master_sojae_mod_dt, --표준원단변경일자
           --j.master_out_date, --조기출고요청일자
           --j.master_taip, --예정타입일
           --j.master_st20_cancle_dt, --20to15취소일자
           --f.fact_issue_deli, --출고납기
           --f.fact_deli, --생산요청납기
           tt.sort,
           j.master_sheet_msg_gb, -- 작지문구 구분
           utl_raw.Cast_to_raw(j.master_sheet_msg) master_sheet_msg -- 작지문구
    FROM   i_tkyk_t t,
           i_agen_t a,
           i_sch_t s,
           i_suju_master_t j,
           i_suju_fact_t f,
           i_user_t u,
           i_cust_t n,
           i_cod_t tt,
           i_stand_bkjk_t b
    WHERE  t.tkyk_code(+) = j.master_tkyk
           AND a.agen_code(+) = j.master_agent
           AND s.sch_code(+) = j.master_school
           AND b.bkjk_squota(+) = j.master_squota
           AND b.bkjk_school(+) = j.master_school
           AND b.bkjk_bokjong(+) = j.master_bokjong
           AND u.user_id(+) = j.master_person
           AND tt.cod_code = j.master_bokjong
           AND tt.cod_gbn_code = '01'
           AND f.fact_order(+) = j.master_order
           AND f.fact_year(+) = j.master_year
           AND f.fact_season(+) = j.master_season
           AND n.cust_code(+) = f.fact_code
           AND j.master_status >= '03'
           AND j.master_status <= '60'
           AND j.master_remake = 'M'
           AND j.master_jaepum IN( 'H', 'A', 'B', 'F' )
           AND j.master_quota = '{season}'
    ORDER  BY t.sort, agen_name, tt.sort
    '''
    
    df_suju_data = mod.select_data(sql)

    df_suju_data.columns = [
        '오더', '상권명', 't.sort' ,'복종', '대리점코드',
        '대리점명', '학교코드', '학교명', '학년', '봉제업체', '수주등록자',
        '수주량', '생산량', 'STATUS', '공통학교코드', '홀드',
        '수주일', '수주확정', '영업확정', '디자인확정', '부자재확정',
        '표준확정', '원단확정', '타입일', '재단일', '봉제일',
        '생산일', 'T/H지시일', 'T/H해제일', 'tt.sort',
        '작지문구구분', '작지문구',
        ]
    
    # 결측치 최소화 (비슷한 날짜로 대체)
    df_suju_data['수주확정'] = df_suju_data['수주확정'].mask(df_suju_data['수주확정'].isnull(), df_suju_data['영업확정'])
    df_suju_data['부자재확정'] = df_suju_data['부자재확정'].mask(df_suju_data['부자재확정'].isnull(), df_suju_data['표준확정']) 

    # 리드타임 계산
    df_suju_data['홀드유지기간'] = df_suju_data['영업확정'] - df_suju_data['수주일']
    df_suju_data['타입소요기간'] = df_suju_data['타입일'] - df_suju_data['영업확정']
    df_suju_data['재봉기간'] = df_suju_data['생산일'] - df_suju_data['타입일']

    # df_suju_data['홀드유지기간'].fillna(0)

    # streamlit 버그 대체 코드
    # dt.days를 사용하여 일자로 변환
    # 다른 방법으로는 streamlit 옵션에서 데이터프레임을 레거시 타입으로 전환하면 된다고 하는데... 싫다!
    # 날짜-날짜 타입의 기간 표시는 무조건 에러남 ->
    # 상세히 들어가면 streamlit의 JS 파트는 arrow v7을 사용하는데 여기서 알려진 공식 버그라고 함.
    # 현버전은 arrow v8

    df_suju_data['홀드유지기간'] = df_suju_data['홀드유지기간'].dt.days.fillna(0).astype(int)
    df_suju_data['타입소요기간'] = df_suju_data['타입소요기간'].dt.days.fillna(0).astype(int)
    df_suju_data['재봉기간'] = df_suju_data['재봉기간'].dt.days.fillna(0).astype(int)

    return df_suju_data



# ----------------------------------------------------------------------------------------------


# -------------------- 사이드바 (생산팀) --------------------

st.sidebar.header('시즌')

# 사이드바 시즌 선택
choosen_season_prod = st.sidebar.selectbox(
    '시즌을 선택하세요 : ',
    options=['23S', '23N'],
)


# 조회조건 변수들
if choosen_season_prod[-1] == 'S':
    bok_gb = '2' # 복종구분   1: 대표복종합치기, 2: 복종별보기
else:
    bok_gb = '1' # 복종구분   1: 대표복종합치기, 2: 복종별보기

qty_gb = '2' # 수량구분   1: 수주 건수, 2: 수주 수량

if choosen_season_prod == '23N':
    prod_quota = ['22F', '22W', '23N'] # 이번 시즌 쿼터
elif choosen_season_prod == '23S':
    prod_quota = ['23S', '23S', '23S']

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
df_prod = data_preprocess(choosen_season_prod, df_base) # 선택한 시즌, 데이터프레임

# st.dataframe(df_base) # 데이터프레임 확인용
# st.dataframe(df_prod)

# 업체별 동복 자켓 진행 현황
if choosen_season_prod[-1] == 'S': # 하복
    ivy_type_qty = df_prod.query("성별 == '하의기준'").at[10, '타입'] # 아이비 타입량
    ivy_product= df_prod.query("성별 == '하의기준'").at[10,'완료'] # 아이비 생산량
else: # 동복
    ivy_type_qty = df_prod.query("성별 == '자켓기준'").at[14, '타입'] # 아이비 타입량
    ivy_product= df_prod.query("성별 == '자켓기준'").at[14,'완료'] # 아이비 생산량

df_major4, df_major4_graph = make_major4_frame(ivy_type_qty, ivy_product)


# 납기
df_deli = mod.select_data(make_deli_sql(choosen_season_prod))
df_deli_j = mod.select_data(make_deli_sql(str(int(choosen_season_prod[:2])-1) + choosen_season_prod[-1]))

df_date, df_date_graph = deli_calc(df_deli)
df_date_j, df_date_graph_j = deli_calc(df_deli_j)



# -------------------- 그래프 (생산팀) --------------------

colors2 = {'(?)': 'RGB(255,255,255)', '아이비클럽': '#9BBA53', '스마트': '#6183BF', '엘리트': '#BB534A', '스쿨룩스': '#E36C0E', '일반업체': '#BFBFBF'}

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
fig2.update_traces(
    textposition='outside',
    texttemplate='%{text:,}',
    width=0.25, # 바 두께 (0 ~ 1)
    ) 
fig2.update_yaxes(tickformat=',d')
fig2.update_layout(
    paper_bgcolor='rgba(233,233,233,233)',
    plot_bgcolor='rgba(0,0,0,0)',
    title_font_size=30,
    yaxis_range=[0, max(df_major4_graph[df_major4_graph['구분']!='출고율(%)']['수량'])*1.1],
    )


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
fig3.update_yaxes(title='출고율(%)')
fig3.update_traces(width=0.25) # 바 두께 (0 ~ 1)
fig3.update_layout(
    paper_bgcolor='rgba(233,233,233,233)',
    plot_bgcolor='rgba(0,0,0,0)',
    title_font_size=30,
    yaxis_range=[0, max(df_major4_graph[df_major4_graph['구분']=='출고율(%)']['수량'])*1.1],
    )
fig3.update_traces(textposition='outside', textfont_size=14)



fig4 = px.bar(df_prod.query("성별 == ['남']"),
            x='복종',
            y='출고율',
            color='복종',
            title=f'남',
            text=df_prod.query("성별 == ['남']")['출고율'].apply(lambda x: '{0:1.0f}%'.format(x)),
            height=500,
            )
fig4.update_layout(paper_bgcolor='rgba(233,233,233,233)', plot_bgcolor='rgba(0,0,0,0)', title_font_size=30)
fig4.update_traces(textposition='inside', textfont_size=14, width=0.4) # 바 두께 (0 ~ 1)


fig5 = px.bar(df_prod.query("성별 == ['여']"),
            x='복종',
            y='출고율',
            color='복종',
            title=f'여',
            text=df_prod.query("성별 == ['여']")['출고율'].apply(lambda x: '{0:1.0f}%'.format(x)),
            height=500,
            )
fig5.update_layout(paper_bgcolor='rgba(233,233,233,233)', plot_bgcolor='rgba(0,0,0,0)', title_font_size=30)
fig5.update_traces(textposition='inside', textfont_size=14, width=0.5) # 바 두께 (0 ~ 1)


fig6 = px.bar(df_prod.query("성별 == ['공통']"),
            x='복종',
            y='출고율',
            color='복종',
            title=f'공통',
            text=df_prod.query("성별 == ['공통']")['출고율'].apply(lambda x: '{0:1.0f}%'.format(x)),
            height=500,
            )
fig6.update_layout(paper_bgcolor='rgba(233,233,233,233)', plot_bgcolor='rgba(0,0,0,0)', title_font_size=30)
fig6.update_traces(textposition='inside', textfont_size=14)


fig7 = go.Figure()
fig7.add_trace(
    go.Bar(
        x=[df_date['복종'], df_date['봉제업체']],
        y=df_date['평균'],
        error_y=dict(
            type='data',
            array=df_date['표준편차'],
            # color='grey',
            thickness=0.5,
            ),
        name=max(df_date['시즌'].unique()),
        # text=['{:,}<br>+-{:,}<br>({:,})'.format(m, s, v) for m, s, v in zip(df_date['평균'], df_date['표준편차'], df_date['오더수'])],
        text=['{:,}<br>({:,})'.format(m, v) for m, v in zip(df_date['평균'], df_date['오더수'])],
        # hovertemplate=
        # '<b>%{text:,}</b><br>' + '%{y}<br>',
        ))
fig7.add_trace(
    go.Bar(
        x=[df_date_j['복종'], df_date_j['봉제업체']],
        y=df_date_j['평균'],
        error_y=dict(
            type='data',
            array=df_date_j['표준편차'],
            # color='grey',
            thickness=0.5,
            ),
        name=min(df_date_j['시즌'].unique()),
        # text=['{:,}<br>+-{:,}<br>({:,})'.format(m, s, v) for m, s, v in zip(df_date_j['평균'], df_date_j['표준편차'], df_date_j['오더수'])],
        text=['{:,}<br>({:,})'.format(m, v) for m, v in zip(df_date_j['평균'], df_date_j['오더수'])],
        # hovertemplate=
        # '<b>%{text:,}</b><br>' + '%{y}<br>',
        ))
fig7.update_xaxes(title='복종별 봉제업체')
fig7.update_yaxes(title='생산시간 (일)')
fig7.update_layout(
    paper_bgcolor='rgba(233,233,233,233)',
    plot_bgcolor='rgba(0,0,0,0)',
    height=750,
    title=f"{max(df_date['시즌'].unique())}/{min(df_date_j['시즌'].unique())} 평균 생산시간 비교",
    title_font_size=30,
    margin_b=170,
    # legend=dict(
    #     traceorder='grouped', # legend 뒤집기
    #     groupclick='toggleitem' # 개별토글 (더블클릭기능과 별개)
    #     ),
    # uniformtext_minsize=18, # 균일폰트 (텍스트만)
    # uniformtext_mode='hide',
    # font_size=15, # 전체폰트 (틱, 텍스트 모두)
    # hoverlabel_font_size=20,
)
fig7.update_traces(textposition='outside')
# fig7.update_traces(texttemplate='%{text:,}')
# fig7['layout']['yaxis']['autorange'] = 'reversed' # Y축 값 뒤집기


# fig8 = go.Figure()
# plot_df_8 = pd.concat([df_date_graph, df_date_graph_j])
# fig8.add_trace(
#         go.Histogram(
#             x=plot_df_8,
#             ))
# fig8.update_layout(barmode='overlay')
# fig8.update_traces(opacity=0.75)
# fig8.update_layout(
#     paper_bgcolor='rgba(233,233,233,233)',
#     plot_bgcolor='rgba(0,0,0,0)',
#     height=750,
#     )




# fig9 = px.histogram(
#     # plot_df_8[(plot_df_8['봉제업체']=='(주)예지패션') & (plot_df_8['봉제업체']=='예사')],
#     plot_df_8,
#     x='재봉기간',
#     color='시즌',
#     facet_col='봉제업체',
#     facet_col_wrap=2,
#     # size='생산량',
#     # hover_data=['petal_width'],
#     )
# fig9.update_layout(
#     paper_bgcolor='rgba(233,233,233,233)',
#     plot_bgcolor='rgba(0,0,0,0)',
#     height=3000,
#     )

# -------------------- 메인페이지 (생산팀) --------------------

st.markdown('#### 생산팀 주간업무 보고')
st.markdown(f'주요업무 ({mod.this_mon} ~ {mod.this_fri})')

# -------------------- 탭 (생산팀) --------------------

EXAMPLE_NO = 3


def streamlit_menu(example=1):
    if example == 1:
        # 1. as sidebar menu
        with st.sidebar:
            selected = option_menu(
                menu_title="Main Menu",  # required
                options=['진행현황', '상세현황', '생산시간', '체크리스트', '시즌점검', '시즌점검2'],  # required
                icons=['forward-fill', 'speedometer', 'play-fill', 'list-check', 'bar-chart-line-fill', 'bar-chart-line-fill'],  # optional
                menu_icon="cast",  # optional
                default_index=0,  # optional
            )
        return selected

    if example == 2:
        # 2. horizontal menu w/o custom style
        selected = option_menu(
            menu_title=None,  # required
            options=['진행현황', '상세현황', '생산시간', '체크리스트', '시즌점검', '시즌점검2'],  # required
            icons=['forward-fill', 'speedometer', 'play-fill', 'list-check', 'bar-chart-line-fill', 'bar-chart-line-fill'],  # optional
            menu_icon="cast",  # optional
            default_index=0,  # optional
            orientation="horizontal",
        )
        return selected

    if example == 3:
        # 2. horizontal menu with custom style
        selected = option_menu(
            menu_title=None,  # required
            options=['진행현황', '상세현황', '생산시간', '체크리스트', '시즌점검', '시즌점검2'],  # required
            icons=['forward-fill', 'speedometer', 'play-fill', 'list-check', 'bar-chart-line-fill', 'bar-chart-line-fill'],  # optional
            menu_icon="cast",  # optional
            default_index=0,  # optional
            orientation="horizontal",
            styles={
                "container": {"padding": "0!important", "background-color": "#F5F5F7"},
                "icon": {"color": "#EF7840", "font-size": "25px"},
                "nav-link": {
                    "font-size": "25px",
                    "text-align": "left",
                    "margin": "0px",
                    "--hover-color": "#eee",
                },
                "nav-link-selected": {"background-color": "#5e90cd"},
            },
        )
        return selected


selected = streamlit_menu(example=EXAMPLE_NO)


if selected == "진행현황":
    if choosen_season_prod[-1] == 'S':
        st.markdown(f'##### ◆ 23년 하복 생산진행 현황 ({choosen_season_prod})')
        st.markdown(f'[하복 / 대리점 HOLD 포함] - 실시간')
    else:
        st.markdown(f'##### ◆ 23년 동복 생산진행 현황 ({choosen_season_prod})')
        st.markdown(f'[동복 / 대리점 HOLD 포함] - 실시간')

    # 한 번에 표시하기
    # left_column, right_column = st.columns(2)
    # left_column.dataframe(df_prod, use_container_width=True)
    # right_column.plotly_chart(fig1, use_container_width=True, theme=None)

    # 남, 여, 공통 3분할
    left_column, middle_column, right_column = st.columns(3)
    left_column.dataframe(df_prod[df_prod['성별']=='남'], use_container_width=True)
    left_column.dataframe(df_prod.query("성별 != ['남', '여', '공통']"), use_container_width=True)
    middle_column.dataframe(df_prod[df_prod['성별']=='여'], use_container_width=True)
    right_column.dataframe(df_prod[df_prod['성별']=='공통'], use_container_width=True)

    left_column, middle_column, right_column = st.columns(3)
    left_column.plotly_chart(fig4, use_container_width=True, theme=None)
    middle_column.plotly_chart(fig5, use_container_width=True, theme=None)
    right_column.plotly_chart(fig6, use_container_width=True, theme=None)

    # 일시숨김
    if choosen_season_prod[-1] == 'S':
        st.markdown("##### ◆ 업체별 하복 하의기준 진행 현황")
    else:
        st.markdown("##### ◆ 업체별 동복 자켓기준 진행 현황")

    st.dataframe(df_major4)
    left_column, right_column = st.columns(2)
    left_column.plotly_chart(fig2, use_container_width=True, theme=None)
    right_column.plotly_chart(fig3, use_container_width=True, theme=None)

    # st.dataframe(df_major4_graph)


if selected == "상세현황":
    st.markdown('##### ◆ STATUS별 진행현황')
    
    df_status = data_preprocess2(df_base)

    # st.dataframe(df_base, use_container_width=True)
    # st.dataframe(df_status.set_index(['제품']), use_container_width=True)
    st.dataframe(df_status.style.background_gradient(
        subset=[
        'ST01', 'ST03', 'ST04',
        'ST05', 'ST10', 'ST11', 'ST12', 'ST13', 'ST14', 'ST15', 'ST20', 'ST30', 'ST40',
        'ST50', 'ST55',
        ]),
        use_container_width=True)
    # df.style.background_gradient(subset=["C"], cmap="RdYlGn", vmin=0, vmax=2.5)

    # 데이터가 그래프 그리기에 적당하지 않음. 재구성 필요.
    plot_df_10 = df_status.drop(['ST01', 'ST60', '전시즌최종수주'], axis=1)
    plot_df_10['ST03 ~ ST04'] = plot_df_10['ST03'] + plot_df_10['ST04']
    plot_df_10['ST05 ~ ST40'] = plot_df_10['ST05'] + plot_df_10['ST10'] + plot_df_10['ST11'] +\
        plot_df_10['ST12'] + plot_df_10['ST13'] + plot_df_10['ST14']+ plot_df_10['ST15'] +\
        plot_df_10['ST20'] + plot_df_10['ST30'] + plot_df_10['ST40']
    plot_df_10['ST50 ~ ST55'] = plot_df_10['ST50'] + plot_df_10['ST55']
    plot_df_10 = plot_df_10.drop(['ST03', 'ST04', 'ST05', 'ST10', 'ST11', 'ST12', 'ST13', 'ST14', 'ST15', 'ST20', 'ST30', 'ST40', 'ST50', 'ST55'], axis=1)
    plot_df_10['복종'] = plot_df_10['성별'] + plot_df_10['복종']
    plot_df_10 = plot_df_10.melt(id_vars=['제품', '성별', '복종'], var_name='STATUS', value_name='수량')
    # st.dataframe(plot_df_10, use_container_width=True)

    df_partly_sum = plot_df_10.groupby(['제품', 'STATUS'])[['수량']].agg(sum).reset_index().pivot(values='수량', index='제품', columns='STATUS')
    st.dataframe(df_partly_sum, use_container_width=True)

    
    fig10 = px.bar(
        plot_df_10[(plot_df_10['제품'] == '학생복') & (plot_df_10['성별'] == '남')],
        x='STATUS',
        y='수량',
        text=plot_df_10[(plot_df_10['제품'] == '학생복') & (plot_df_10['성별'] == '남')]['수량'].replace(0, ''),
        color='복종',
        height=500,
        )
    fig10.update_xaxes(ticks='inside', tickfont_size=16, tickson='boundaries', ticklen=10, tickwidth=2, title_font_size=20,)
    fig10.update_yaxes(
        # type='log',
        range=[0, plot_df_10['수량'].max() * 1.1], # 로그스케일 적용시 비활성화 해야함
        ticks='inside', tickfont_size=14, ticklen=10, tickwidth=2, tickformat=',d', title_font_size=20,)
    fig10.update_layout(paper_bgcolor='rgba(233,233,233,233)', plot_bgcolor='rgba(0,0,0,0)',
                        barmode='group', title_text=f'학생복 남', title_font_size = 30,
                        margin_b=70, margin_t=70)
    fig10.update_traces(textposition='outside', textfont_size=14)
    
    #수직 사각 영역 추가하기
    fig10.add_vrect(
        x0=-0.5, x1=0.5, line_width=2, fillcolor='red', opacity=0.07,
        annotation_text='대리점', 
        annotation_position='top right',
        annotation_font_size=20,
        annotation_font_color='red',
        )
    fig10.add_vrect(
        x0=0.5, x1=1.5, line_width=2, fillcolor='green', opacity=0.07,
        annotation_text='본사', 
        annotation_position='top',
        annotation_font_size=20,
        annotation_font_color='green',
        )
    fig10.add_vrect(
        x0=1.5, x1=2.5, line_width=2, fillcolor='blue', opacity=0.07,
        annotation_text='생산처', 
        annotation_position='top left',
        annotation_font_size=20,
        annotation_font_color='blue',
        )

    fig11 = px.bar(
        plot_df_10[(plot_df_10['제품'] == '학생복') & (plot_df_10['성별'] == '여')],
        x='STATUS',
        y='수량',
        text=plot_df_10[(plot_df_10['제품'] == '학생복') & (plot_df_10['성별'] == '여')]['수량'].replace(0, ''),
        color='복종',
        height=500,
        )
    fig11.update_xaxes(ticks='inside', tickfont_size=16, tickson='boundaries', ticklen=10, tickwidth=2, title_font_size=20)
    fig11.update_yaxes(
        # type='log',
        range=[0, plot_df_10['수량'].max() * 1.1], # 로그스케일 적용시 비활성화 해야함
        ticks='inside', tickfont_size=14, ticklen=10, tickwidth=2, tickformat=',d', title_font_size=20,)
    fig11.update_layout(paper_bgcolor='rgba(233,233,233,233)', plot_bgcolor='rgba(0,0,0,0)',
                        barmode='group', title_text=f'학생복 여', title_font_size = 30,
                        margin_b=70, margin_t=70,)
    fig11.update_traces(textposition='outside', textfont_size=14)

    #수직 사각 영역 추가하기
    fig11.add_vrect(
        x0=-0.5, x1=0.5, line_width=2, fillcolor='red', opacity=0.07,
        annotation_text='대리점', 
        annotation_position='top right',
        annotation_font_size=20,
        annotation_font_color='red',
        )
    fig11.add_vrect(
        x0=0.5, x1=1.5, line_width=2, fillcolor='green', opacity=0.07,
        annotation_text='본사', 
        annotation_position='top',
        annotation_font_size=20,
        annotation_font_color='green',
        )
    fig11.add_vrect(
        x0=1.5, x1=2.5, line_width=2, fillcolor='blue', opacity=0.07,
        annotation_text='생산처', 
        annotation_position='top left',
        annotation_font_size=20,
        annotation_font_color='blue',
        )

    fig12 = px.bar(
        plot_df_10[(plot_df_10['제품'] == '체육복')],
        x='STATUS',
        y='수량',
        text=plot_df_10[(plot_df_10['제품'] == '체육복')]['수량'].replace(0, ''),
        color='복종',
        height=500,
        )
    fig12.update_xaxes(ticks='inside', tickfont_size=16, tickson='boundaries', ticklen=10, tickwidth=2, title_font_size=20,)
    fig12.update_yaxes(
        # type='log',
        range=[0, plot_df_10['수량'].max() * 1.1], # 로그스케일 적용시 비활성화 해야함
        ticks='inside', tickfont_size=14, ticklen=10, tickwidth=2, tickformat=',d', title_font_size=20,)
    fig12.update_layout(paper_bgcolor='rgba(233,233,233,233)', plot_bgcolor='rgba(0,0,0,0)',
                        barmode='group', title_text=f'체육복 남녀', title_font_size = 30,
                        margin_b=70, margin_t=70,)
    fig12.update_traces(textposition='outside', textfont_size=14)

    #수직 사각 영역 추가하기
    fig12.add_vrect(
        x0=-0.5, x1=0.5, line_width=2, fillcolor='red', opacity=0.07,
        annotation_text='대리점', 
        annotation_position='top right',
        annotation_font_size=20,
        annotation_font_color='red',
        )
    fig12.add_vrect(
        x0=0.5, x1=1.5, line_width=2, fillcolor='green', opacity=0.07,
        annotation_text='본사', 
        annotation_position='top',
        annotation_font_size=20,
        annotation_font_color='green',
        )
    fig12.add_vrect(
        x0=1.5, x1=2.5, line_width=2, fillcolor='blue', opacity=0.07,
        annotation_text='생산처', 
        annotation_position='top left',
        annotation_font_size=20,
        annotation_font_color='blue',
        )

    # st.warning('아래 그래프는 데이터 격차로 인해 로그스케일로 표현되었습니다.')
    st.plotly_chart(fig10, use_container_width=True, theme=None)
    st.plotly_chart(fig11, use_container_width=True, theme=None)
    st.plotly_chart(fig12, use_container_width=True, theme=None)



if selected == "생산시간":

    # st.write(str(int(choosen_season_prod[:2])-1) + choosen_season_prod[-1])
    # st.write(str(choosen_season_prod))
    # st.write(mod.select_data(make_deli_sql(choosen_season_prod)))

    # st.dataframe(df_deli, use_container_width=True)
    # st.dataframe(df_deli_j, use_container_width=True)

    left_column, right_column = st.columns(2)
    left_column.write(f'##### {choosen_season_prod} 업체별 평균 생산시간 (생산일 - 타입일, 생산완료 오더기준)')
    left_column.dataframe(df_date, use_container_width=True)

    right_column.write(f'##### {str(int(choosen_season_prod[:2])-1) + choosen_season_prod[-1]} 업체별 평균 생산시간 (생산일 - 타입일)')
    right_column.dataframe(df_date_j, use_container_width=True)
    st.plotly_chart(fig7, use_container_width=True, theme=None)

    
    
    plot_df_8 = pd.concat([df_date_graph, df_date_graph_j])
    
    left_column, middle_column, right_column = st.columns([1, 1, 8])
    sel_bj = left_column.radio(
        '복종을 선택하세요',
        options=sorted(plot_df_8['복종'].unique()),
        )
    # left_column.write(f'{sel_bj} 선택')

    # 업체가 1개면 select_slider는 에러난다. 1 ~ 1을 찾는 꼴.
    sel_comp = middle_column.selectbox(
        '업체를 선택하세요',
        options=plot_df_8[plot_df_8['복종']==sel_bj]['봉제업체'].unique(),
        )
    # left_column.write(f'{sel_comp} 선택')

    x0 = plot_df_8[(plot_df_8['복종']==sel_bj) & (plot_df_8['봉제업체']==sel_comp)]
    # x1 = plot_df_8[(plot_df_8['복종']==sel_bj) & (plot_df_8['봉제업체']==sel_comp) & (plot_df_8['시즌']==str(int(choosen_season_prod[:2])-1) + choosen_season_prod[-1])]

    fig8 = go.Figure()
    for ss in x0['시즌'].unique():
        fig8.add_trace(
                go.Histogram(
                    x=x0[x0['시즌']==ss]['재봉기간'],
                    name=ss,
                    bingroup=1,
                    # textposition='inside',
                    # texttemplate='%{y}',
                    ))
    fig8.update_layout(barmode='overlay')
    fig8.update_traces(opacity=0.5)
    fig8.update_xaxes(title='생산시간 (일)')
    fig8.update_yaxes(title='오더 수')
    fig8.update_layout(
        paper_bgcolor='rgba(233,233,233,233)',
        plot_bgcolor='rgba(0,0,0,0)',
        title=f'{sel_bj}복종 / {sel_comp} 생산시간별 오더수',
        title_font_size=30,
        # height=750,
        )
    
    right_column.plotly_chart(fig8, use_container_width=True, theme=None)
    # st.plotly_chart(fig9, use_container_width=True, theme=None)

    st.markdown('---')
    st.markdown('##### 업체별 생산량 추이')

    df_prod_speed = df_deli[['복종', '봉제업체', '생산일', '오더']]
    df_prod_speed_graph = df_prod_speed.groupby(['복종', '봉제업체', '생산일']).count().reset_index()
    
    # 주단위 집계
    df_prod_speed_graph = df_prod_speed_graph.set_index('생산일')
    df_prod_speed_graph2 = df_prod_speed_graph.groupby(['복종', '봉제업체', '생산일'])[['오더']].sum(numeric_only=True).reset_index()
    df_prod_speed_graph = df_prod_speed_graph.groupby(['복종', '봉제업체']).resample('W').sum(numeric_only=True).reset_index()
    
    
    
    fig_speed = go.Figure()
    for bok in (df_prod_speed_graph['복종'].unique()):
        for cust in (df_prod_speed_graph['봉제업체'].unique()):
            plot_fig_speed = df_prod_speed_graph[(df_prod_speed_graph['복종'] == bok) & (df_prod_speed_graph['봉제업체'] == cust)] 
            if bok == 'J':  
                fig_speed.add_trace(
                    go.Scatter(
                        x=plot_fig_speed['생산일'],
                        y=plot_fig_speed['오더'],
                        # text=plot_fig_speed['오더'],
                        # textposition='middle right',
                        # textfont=dict(
                            # color=colors_basic[0],
                            # size=18,
                            # ),
                        mode='markers+lines',
                        name=f'{bok} {cust}',
                        legendgroup=bok,
                        legendgrouptitle_text=bok,
                        # line=dict(color=colors_basic[0], width=4),
                        marker=dict(size=7),
                        ))
            else:
                fig_speed.add_trace(
                    go.Scatter(
                        x=plot_fig_speed['생산일'],
                        y=plot_fig_speed['오더'],
                        # text=plot_fig_speed['오더'],
                        # textposition='middle right',
                        # textfont=dict(
                            # color=colors_basic[0],
                            # size=18,
                            # ),
                        visible='legendonly',
                        mode='markers+lines',
                        name=f'{bok} {cust}',
                        legendgroup=bok,
                        legendgrouptitle_text=bok,
                        # line=dict(color=colors_basic[0], width=4),
                        marker=dict(size=7),
                        ))
    fig_speed.update_xaxes(title='생산일', dtick='M1', tickformat='%Y/%m')
    fig_speed.update_yaxes(title='오더수', tickformat=',d')
    fig_speed.update_layout(
        paper_bgcolor='rgba(233,233,233,233)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=850,
        title=f'업체별 생산량 추이 (주단위)',
        title_font_size=30,
        # legend=dict(
        #     groupclick='toggleitem' # 개별토글 (더블클릭기능과 별개)
        #     ),
        )
    
    # st.dataframe(df_deli)
    # st.write(len(df_deli))
    # st.dataframe(df_prod_speed)
    # st.dataframe(df_prod_speed_graph)
    # st.dataframe(df_deli[(df_deli['생산일'] > '2022-12-18') & (df_deli['생산일'] <= '2022-12-25') & (df_deli['복종'] == 'B')])
    st.plotly_chart(fig_speed, use_container_width=True, theme=None)


    left_column, right_column = st.columns([1, 8])
    bok2 = left_column.radio(
        '복종을 선택하세요.',
        options=sorted(df_prod_speed_graph['복종'].unique()),
        key='bok2',
        )
    fig_speed2 = px.scatter(
        df_prod_speed_graph[df_prod_speed_graph['복종'] == bok2],
        x='생산일',
        y='오더',
        color='봉제업체',
        title=f'{bok2}복종 업체별 생산량 추이 (이동평균선)',
        # trendline='ols',
        # trendline='lowess',
        trendline='rolling', trendline_options=dict(window=5),
        # trendline='ewm', trendline_options=dict(halflife=5),
        # trendline='expanding',
        )
    # 라인만 남기기
    # fig_speed2.data = [t for t in fig_speed2.data if t.mode == 'lines']
    
    fig_speed2.update_xaxes(dtick='M1', tickformat='%Y/%m')
    fig_speed2.update_yaxes(title='오더수', tickformat=',d')
    fig_speed2.update_layout(
        paper_bgcolor='rgba(233,233,233,233)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=850,
        title_font_size=30,
        )

    right_column.plotly_chart(fig_speed2, use_container_width=True, theme=None)



# if selected == "체크리스트":
#     st.markdown('#### 예상생산일자')
#     st.latex('예상생산일자 = 준비기간(대리점) + 타입소요기간(본사) + 재봉기간(공장)')
#     st.latex('ST03(홀드) -> 개찰 -> 준비기간(대리점) -> ST12(영업확정) -> 타입소요기간(본사) -> ST40(타입) -> 재봉기간(공장) -> ST60(생산완료)')
#     st.markdown('---')

#     df_code_date = get_bid_data(choosen_season_prod) # 학교코드 별 개찰일자
#     df_delay_order = get_suju_data(choosen_season_prod) # 전체 수주데이터
    
#     # st.dataframe(df_delay_order)
#     # st.write(df_delay_order.shape)
    
#     df_delay_order_merged = df_delay_order.merge(df_code_date, how='left')
#     df_delay_order_merged = df_delay_order_merged[[
#         '오더', '상권명', 't.sort', '복종', '대리점코드',
#         '대리점명', '학교코드', '학교명', '학년', '봉제업체', '수주등록자',
#         '수주량', '생산량', 'STATUS', '공통학교코드', '홀드',
#         '수주일', '수주확정', '개찰일자', '영업확정', '디자인확정',
#         '부자재확정', '표준확정', '원단확정', '타입일', '재단일',
#         '봉제일', '생산일', 'T/H지시일', 'T/H해제일', '홀드유지기간',
#         '타입소요기간', '재봉기간', '작지문구구분', '작지문구',
#         ]]

#     # st.dataframe(df_delay_order_merged)
#     # st.write(df_delay_order_merged.shape)

#     df_bid_date_true = df_delay_order_merged[~df_delay_order_merged['개찰일자'].isna()]
#     # df_bid_date_false = df_delay_order_merged[df_delay_order_merged['개찰일자'].isna()] # 개찰일자에 없는 것들

#     # st.dataframe(df_delay_order_merged, use_container_width=True)
#     # st.write(df_delay_order_merged.shape)

#     # 복종별 평균 타입소요기간 계산
#     df_taip_temp = df_delay_order_merged[df_delay_order_merged['타입소요기간'] > 0].copy()
#     df_taip_temp_2 = df_delay_order_merged[(df_delay_order_merged['타입소요기간'] > 0) & (df_delay_order_merged['타입일'] >= SPEED_DATE_N)].copy() # 2023년 2월 1일 이후 타입일자만 추출
#     df_bok_per_taip_time = df_taip_temp.groupby(['복종'])[['타입소요기간']].agg('mean').reset_index().round(0) # 복종별 타입에 걸리는 시간
#     df_bok_per_taip_time_2 = df_taip_temp_2.groupby(['복종'])[['타입소요기간']].agg('mean').reset_index().round(0) # 복종별 타입에 걸리는 시간 (2023년 2월 1일 이후)
#     df_bok_per_taip_time = pd.merge(df_bok_per_taip_time, df_bok_per_taip_time_2, on='복종', how='left', suffixes=('', '(2월1일이후)'))
    

#     st.markdown('#### 타입소요기간')
#     st.markdown('''
#     1. 영업확정 ~ 타입일 사이의 기간\n
#     2. 후반부로 갈수록 빨라진다.\n
#     3. 2023년 2월 1일 이후의 타입소요기간을 구한다.
#     ''')

#     st.dataframe(df_bok_per_taip_time.set_index('복종').T)
#     st.markdown('---')

#     df_bok_per_taip_time = df_bok_per_taip_time.fillna(method='ffill', axis=1)
#     df_bok_per_taip_time = df_bok_per_taip_time.drop('타입소요기간', axis=1)
#     df_bok_per_taip_time.columns = ['복종', '타입소요기간(일)']

#     # ----------------------------------------------- 타입소요기간 -----------------------------------------------
#     st.markdown('#### 평균생산시간')
#     st.markdown(f'''
#     1. 타입일 ~ 생산일 사이의 기간\n
#     2. 시즌 후반부로 갈수록 빨라진다.\n
#     3. 시즌평균, 1월이후평균, 2월이후평균을 계산한다.
#     ''')
    
#     df_deli_1month = df_deli[df_deli['생산일'] >= '2023-01-01'].copy().drop(['홀드유지기간', '타입소요기간', '재봉기간'], axis=1) # 앞선 구문에서 컬럼을 추가해서 원래대로 짤라야 들어감
#     df_deli_2weeks = df_deli[df_deli['생산일'] >= SPEED_DATE_N].copy().drop(['홀드유지기간', '타입소요기간', '재봉기간'], axis=1)
#     df_date_1month, _ = deli_calc(df_deli_1month)
#     df_date_2weeks, _ = deli_calc(df_deli_2weeks)

#     df_date_cut = df_date.iloc[:, 1:6]
#     df_date_1month_cut = df_date_1month.iloc[:, 1:6]
#     df_date_2weeks_cut = df_date_2weeks.iloc[:, 1:6]

#     df_date_1month_cut.columns = ['복종', '봉제업체', '오더수(1월)', '평균(1월)', '표준편차(1월)']
#     df_date_2weeks_cut.columns = ['복종', '봉제업체', '오더수(2월)', '평균(2월)', '표준편차(2월)']

#     df_date_all = pd.merge(df_date_cut, df_date_1month_cut, how='left', on=['복종', '봉제업체'])
#     df_date_all = pd.merge(df_date_all, df_date_2weeks_cut, how='left', on=['복종', '봉제업체'])

#     df_date_all = df_date_all[['복종', '봉제업체', '평균', '평균(1월)', '평균(2월)', '표준편차', '표준편차(1월)', '표준편차(2월)', '오더수', '오더수(1월)', '오더수(2월)']]
#     df_date_all = df_date_all.fillna(method='ffill', axis=1).reset_index(drop=True) # 2주안에 복종이 없는 경우 None값이 될테고 앞의 값(시즌평균)으로 채움. (axis=1은 컬럼방향)

#     st.dataframe(df_date_all)

#     df_date_rank_2w = df_date_all[['복종', '봉제업체', '평균(2월)', '오더수(2월)']].copy() # 생산일자 평균값 merge하기 위해 복사
#     df_date_rank_2w = df_date_rank_2w.sort_values(['복종', '오더수(2월)', '평균(2월)'], ascending=[True, False, True]).reset_index(drop=True)
#     df_date_rank_2w['오더수순위'] = df_date_rank_2w.groupby(['복종'])[['오더수(2월)']].rank(method='first', ascending=False) # 오더수 순위
#     df_date_rank_2w = df_date_rank_2w[df_date_rank_2w['오더수순위'] == 1] # 오더수 순위 1위만
#     df_date_rank_2w = df_date_rank_2w.drop(['오더수(2월)', '오더수순위'], axis=1).reset_index(drop=True)
#     df_date_rank_2w.columns = ['복종', '대표생산처', '평균생산시간(일)']
#     df_date_rank_2w['평균생산시간(일)'] = df_date_rank_2w['평균생산시간(일)'].astype(int)

#     st.markdown('##### 대표 봉제업체 평균생산시간')
#     st.dataframe(df_date_rank_2w.set_index('복종').style.background_gradient())
#     st.write(f"합계: {df_date_rank_2w['평균생산시간(일)'].sum()}")
#     st.markdown('---')


#     # -------------------------------------------------------------- #
#     st.markdown('#### 복종별 데드라인')
    
#     if choosen_season_prod[-1] == 'S':
#         deadline_dt = st.date_input('출고기준일을 지정하세요.', datetime.strptime(DELI_DATE_S, '%Y-%m-%d')) # 납기일 변수
#     else:
#         deadline_dt = st.date_input('출고기준일을 지정하세요.', datetime.strptime(DELI_DATE_N, '%Y-%m-%d')) # 납기일 변수
#     # st.write(type(deadline_dt))

#     st.markdown(f'''
#     1. 기준일 : {deadline_dt}\n
#     2. 타입소요기간 + 평균생산시간을 기준일부터 역으로 계산하여 데드라인을 구한다.\n
#     3. **:red[데드라인 이후에 영업확정 할 경우 납기일을 못 맞출 확률이 매우 높다.]**\n
#     ''')

#     df_deadline = pd.merge(df_bok_per_taip_time, df_date_rank_2w, how='left', on='복종').drop('대표생산처', axis=1)
#     df_deadline['제작기간'] = df_deadline['타입소요기간(일)'] + df_deadline['평균생산시간(일)']
#     df_deadline['데드라인(영업확정)'] = (pd.to_datetime(deadline_dt) - pd.to_timedelta(df_deadline['제작기간'], unit='D')).dt.date
#     df_deadline['데드라인(타입)'] = (pd.to_datetime(deadline_dt) - pd.to_timedelta(df_deadline['평균생산시간(일)'], unit='D')).dt.date
#     df_deadline = df_deadline.set_index('복종')
    
#     st.dataframe(df_deadline)

#     st.markdown('---')

#     # -------------------------------------------------------------- #

#     st.markdown('#### 지연오더 점검(ST03)')

#     # st.markdown('This text is :red[colored red], and this is **:blue[colored]** and bold.') # 텍스트 컬러적용 예시
#     st.markdown(f'1. **{len(df_delay_order_merged)}** 개(ST03 ~ ST60)의 수주오더 중 낙찰일자가 확정된 오더 **:red[{len(df_bid_date_true)}]** 개')
#     st.markdown(f'''
#     2. 낙찰일자 확정오더 **:red[{len(df_bid_date_true)}]** 개 중
#     **ST03**(HOLD)은 **:green[{len(df_bid_date_true[df_bid_date_true["STATUS"] == "03"])}]** 개
#     ''')
        
#     df_bid_date_true_status_sum = df_bid_date_true['STATUS'].value_counts().sort_index().reset_index()
#     df_bid_date_true_status_sum.columns = ['STATUS', '오더수']
#     df_bid_date_true_status_sum = df_bid_date_true_status_sum.T
#     df_bid_date_true_status_sum.columns = df_bid_date_true_status_sum.loc['STATUS']
#     df_bid_date_true_status_sum = df_bid_date_true_status_sum.drop('STATUS')

#     st.dataframe(df_bid_date_true_status_sum)

#     df_true_st03 = df_bid_date_true[df_bid_date_true['STATUS'] == '03']

#     if len(df_true_st03) > 0: # ST03 오더가 있을 경우에만 실행
#         st.markdown(f'''
#         3. **ST03**(HOLD)오더 **:green[{len(df_bid_date_true[df_bid_date_true["STATUS"] == "03"])}]** 개를
#         대리점, 학교명으로 그룹화하여 복종수가 가장 적은 학교 순으로 정렬
#         ''')

#         df_true_st03_bok = df_true_st03.groupby(['대리점명', '학교명', '학교코드'])[['복종']].agg(sum)['복종'].reset_index()
#         df_true_st03_bok['복종수'] = df_true_st03_bok['복종'].str.len()
#         df_true_st03_bok = df_true_st03_bok.sort_values('복종수').set_index('대리점명')

#         st.dataframe(df_true_st03_bok)

#         st.markdown(f'''
#         4. 복종수가 2개 이상인 곳들은 제외 : 복종수가 2개 이상이면 학교요청으로 지연되었을 가능성이 높음
#         ''')
        
#         df_true_st03_bok_1 = df_true_st03_bok[df_true_st03_bok['복종수'] == 1]

#         st.dataframe(df_true_st03_bok_1)

#         st.markdown(f'''
#         5. 4번의 오더리스트에 타입소요기간과 평균생산시간을 더한 날짜를 예상생산일자로 가정한다.\n
#         **:red[예상생산일자 = 오늘날짜 + 타입소요기간 + 평균생산시간]** \n
#         또한 **:green[작지문구가 있는 오더는 납기여유가 있는 오더]** 이므로 목록에서 제외한다.
#         ''')
        
#         # if choosen_season_prod[-1] == 'S':
#         #     deli_dt = st.date_input('납기일을 지정하세요.', datetime.strptime(DELI_DATE_S, '%Y-%m-%d')) # 납기일 변수 (전역변수 동하복납기일)
#         # else:
#         #     deli_dt = st.date_input('납기일을 지정하세요.', datetime.strptime(DELI_DATE_N, '%Y-%m-%d')) # 납기일 변수 (전역변수 동하복납기일)
#         # st.markdown(f'##### 납기일 {deli_dt} 선택!')
        

#         df_deli_list = pd.merge(df_true_st03_bok_1, df_date_rank_2w, on='복종', how='left') # 복종별 평균생산시간 추가
#         df_deli_list = pd.merge(df_deli_list, df_bok_per_taip_time, on='복종', how='left') # 복종별 타입소요기간 추가
#         df_deli_list = pd.merge(df_deli_list, df_true_st03[['대리점명', '학교코드', '복종', '오더', '수주량', '작지문구구분', '작지문구', '개찰일자']], on=['학교코드', '복종'], how='left')
#         df_deli_list['개찰이후경과일'] = (datetime.today() - pd.to_datetime(df_deli_list['개찰일자'])).dt.days
#         df_deli_list = df_deli_list.drop(['복종수'], axis=1)
#         df_deli_list['예상생산일자'] = datetime.today() + \
#             pd.to_timedelta(df_deli_list['타입소요기간(일)'], unit='d') + \
#             pd.to_timedelta(df_deli_list['평균생산시간(일)'], unit='d')
#         df_deli_list[f'납기준수여부({deadline_dt}까지)'] = df_deli_list['예상생산일자'].apply(lambda x: 'X' if x > pd.Timestamp(deadline_dt) else 'O')

#         st.dataframe(df_deli_list)

#         df_tt_cnt = df_deli_list[(df_deli_list[f'납기준수여부({deadline_dt}까지)'] == 'X') & (df_deli_list['작지문구구분'] == 'N')]
#         df_tt_cnt = df_tt_cnt.drop(['작지문구구분'], axis=1)

#         st.markdown(f'''
#         6. **:red[주의가 필요한 오더리스트]**\n
        
#         **:blue[- 복종수 1]**\n
#         **:blue[- 작지문구 없음]**\n
#         **:blue[- 예상일자 이후 출고]**\n
#         \n
#         **:red[총 오더수 : {len(df_tt_cnt)} 개]**
#         ''')

#         st.dataframe(df_tt_cnt)

#         st.markdown('7. 복종별 수주량 합계')
#         st.dataframe(df_tt_cnt.groupby(['복종'])[['수주량']].agg(sum).T)

#     else: # ST03 오더가 없는 경우
#         st.markdown('#### :red[ST03 오더가 없습니다.]')

#     st.markdown('---')


#     # ------------------------------------------------- ST03 끝 -------------------------------------------------------

#     st.markdown('#### 지연오더 점검(ST04 ~ ST55)')

#     st.markdown(f'1. **{len(df_delay_order_merged)}** 개(ST03 ~ ST60)의 수주오더 중 낙찰일자가 확정된 오더 **:red[{len(df_bid_date_true)}]** 개')
#     st.markdown(f'''
#     2. 낙찰일자 확정오더 **:red[{len(df_bid_date_true)}]** 개 중
#     **ST04 ~ ST55**는 **:green[{len(df_bid_date_true[(df_bid_date_true["STATUS"] != "03") & (df_bid_date_true["STATUS"] != "60")])}]** 개
#     ''')
    
#     st.dataframe(df_bid_date_true_status_sum)


#     # ST04 ~ ST55 오더만 추출 (개찰일자가 없는 오더는 제외)
#     df_true_st04_to_st55 = df_bid_date_true[(df_bid_date_true['STATUS'] != '60') & (df_bid_date_true['STATUS'] != '03')]
#     df_true_st04_to_st55_1 = pd.merge(df_true_st04_to_st55, df_bok_per_taip_time, on='복종', how='left') # 복종별 타입소요기간 추가
    
#     df_cust_per_prod_time = df_date_all[['복종', '봉제업체', '평균(2월)']]
#     df_true_st04_to_st55_2 = pd.merge(df_true_st04_to_st55_1, df_cust_per_prod_time, on=['복종', '봉제업체'], how='left') # 봉제업체 매칭해서 평균생산시간 추가
#     df_true_st04_to_st55_2 = df_true_st04_to_st55_2.rename(columns={'평균(2월)': '평균생산시간(일)'})

#     df_true_st04_to_st55_3_1 = df_true_st04_to_st55_2[~df_true_st04_to_st55_2['평균생산시간(일)'].isna()] # 생산시간 매칭된곳
#     df_true_st04_to_st55_3_2 = df_true_st04_to_st55_2[df_true_st04_to_st55_2['평균생산시간(일)'].isna()] # 생산시간 매칭안된곳 (스팟, 업체미정)
    
#     df_true_st04_to_st55_3_2 = df_true_st04_to_st55_3_2.drop('평균생산시간(일)', axis=1) # 평균생산시간(일) 컬럼 삭제(안찍힌 컬럼이라서 삭제 후 재생성)
#     df_true_st04_to_st55_4_2 = pd.merge(df_true_st04_to_st55_3_2, df_date_rank_2w.drop('대표생산처', axis=1), on='복종', how='left') # 매칭이 안된곳은 대표생산처 평균생산시간으로 대체(스팟, 업체미정)
#     df_true_st04_to_st55_4 = pd.concat([df_true_st04_to_st55_3_1, df_true_st04_to_st55_4_2]) # 날짜기입(타입시간, 생산시간) 완료

    
#     # 예상생산일자 계산
#     df_true_st04_to_st55_5_1 = df_true_st04_to_st55_4[~df_true_st04_to_st55_4['타입일'].isna()].copy() # 타입일자가 있는 오더
#     df_true_st04_to_st55_5_2 = df_true_st04_to_st55_4[df_true_st04_to_st55_4['타입일'].isna()].copy() # 타입일자가 없는 오더
#     df_true_st04_to_st55_5_3 = df_true_st04_to_st55_5_2[~df_true_st04_to_st55_5_2['영업확정'].isna()].copy() # 타입일자가 없고, 영업확정일자가 있는 오더
#     df_true_st04_to_st55_5_4 = df_true_st04_to_st55_5_2[df_true_st04_to_st55_5_2['영업확정'].isna()].copy() # 타입일자도 없고, 영업확정일자가 없는 오더


#     if len(df_true_st04_to_st55_5_1) > 0: # 타입일자가 있는 오더 = 타입일 + 평균생산시간
#         df_true_st04_to_st55_5_1['예상생산일자'] = df_true_st04_to_st55_5_1['타입일'] + \
#             pd.to_timedelta(df_true_st04_to_st55_5_1['평균생산시간(일)'], unit='d')
    
#     if len(df_true_st04_to_st55_5_3) > 0: # 타입일자가 없고, 영업확정일자가 있는 오더 = 영업확정일자 + 타입소요기간 + 평균생산시간
#         df_true_st04_to_st55_5_3['예상생산일자'] = df_true_st04_to_st55_5_3['영업확정'] + \
#             pd.to_timedelta(df_true_st04_to_st55_5_3['타입소요기간(일)'], unit='d') + \
#             pd.to_timedelta(df_true_st04_to_st55_5_3['평균생산시간(일)'], unit='d')

#     if len(df_true_st04_to_st55_5_4) > 0: # 타입일자도 없고, 영업확정일자가 없는 오더 = 오늘 + 타입소요기간 + 평균생산시간
#         df_true_st04_to_st55_5_4['예상생산일자'] = datetime.today() + \
#             pd.to_timedelta(df_true_st04_to_st55_5_4['타입소요기간(일)'], unit='d') + \
#             pd.to_timedelta(df_true_st04_to_st55_5_4['평균생산시간(일)'], unit='d')
    
#     if len(df_true_st04_to_st55_5_1) > 0: 
#         if len(df_true_st04_to_st55_5_2) > 0:
#             if len(df_true_st04_to_st55_5_3) > 0:
#                 if len(df_true_st04_to_st55_5_4) > 0:
#                     df_true_st04_to_st55_5 = pd.concat([df_true_st04_to_st55_5_1, df_true_st04_to_st55_5_3, df_true_st04_to_st55_5_4])
#                 else:
#                     df_true_st04_to_st55_5 = pd.concat([df_true_st04_to_st55_5_1, df_true_st04_to_st55_5_3])
#             else:
#                 df_true_st04_to_st55_5 = pd.concat([df_true_st04_to_st55_5_1, df_true_st04_to_st55_5_4])
#         else:
#             df_true_st04_to_st55_5 = df_true_st04_to_st55_5_1.copy()
#     else:
#         st.write('### 오더가 없습니다.')

#     df_true_st04_to_st55_5[f'납기준수여부({deadline_dt}까지)'] = df_true_st04_to_st55_5['예상생산일자'].apply(lambda x: 'X' if x > pd.Timestamp(deadline_dt) else 'O')
    

#     st.markdown(f'''
#     3. **:green[타입소요기간]** 과 **:red[평균생산시간]** 을 산입하여 **:blue[예상생산일자]** 를 계산합니다.\n\n
#     **타입일자가 있는 오더 = 타입일 + 평균생산시간** \n
#     **타입일자가 없고, 영업확정일자가 있는 오더 = 영업확정일자 + 타입소요기간 + 평균생산시간** \n
#     **타입일자도 없고, 영업확정일자가 없는 오더 = 오늘 + 타입소요기간 + 평균생산시간** \n
#     ''')

#     st.dataframe(df_true_st04_to_st55_5)
    
#     st.write(f'''
#         타입일자가 있는 오더 : {len(df_true_st04_to_st55_5_1)}개\n
#         타입일자가 없는 오더 : {len(df_true_st04_to_st55_5_2)}개\n
#         타입일자가 없고, 영업확정일자가 있는 오더 : {len(df_true_st04_to_st55_5_3)}개\n
#         타입일자, 영업확정일자 없는 오더 : {len(df_true_st04_to_st55_5_4)}개
#     ''')


#     df_true_st04_to_st55_6 = df_true_st04_to_st55_5[(df_true_st04_to_st55_5[f'납기준수여부({deadline_dt}까지)'] == 'X') & (df_true_st04_to_st55_5['작지문구구분'] == 'N')].copy()
#     df_true_st04_to_st55_6['개찰이후경과일'] = (df_true_st04_to_st55_6['영업확정'] - df_true_st04_to_st55_6['개찰일자']).dt.days
#     df_true_st04_to_st55_6['영업확정경과일'] = (datetime.now() - df_true_st04_to_st55_6['영업확정']).dt.days
#     df_true_st04_to_st55_6['타입경과일'] = (datetime.now() - df_true_st04_to_st55_6['타입일']).dt.days
#     df_true_st04_to_st55_6 = df_true_st04_to_st55_6[[
#         '오더', '상권명', '복종', '대리점명', '학교명',
#         '봉제업체', '수주량', '개찰일자', '영업확정', '타입일',
#         '타입소요기간(일)', '평균생산시간(일)', '개찰이후경과일', '영업확정경과일', '타입경과일',
#         'STATUS', '예상생산일자', f'납기준수여부({deadline_dt}까지)',
#         ]]
    
    
#     df_true_st04_to_st55_6 = df_true_st04_to_st55_6.sort_values('예상생산일자').reset_index(drop=True)
    
    
#     st.markdown(f'''
#     4. 주의가 필요한 오더리스트 : **:red[{len(df_true_st04_to_st55_6)}]** 개
#     ''')
#     st.dataframe(df_true_st04_to_st55_6)
#     st.markdown('---')


#     st.write('5. 주의오더 복종별 수주량 합계')
#     left_column, right_column = st.columns([1, 6])
#     left_column.dataframe(df_true_st04_to_st55_6.groupby(['복종'])[['수주량']].agg(sum))
    
#     fig_deli_bok = px.bar(
#         df_true_st04_to_st55_6.groupby(['복종'])[['수주량']].agg(sum).reset_index(),
#         x='복종',
#         y='수주량',
#         color='복종',
#         text='수주량',
#         )
#     fig_deli_bok.update_xaxes(ticks='outside')
#     fig_deli_bok.update_yaxes(ticks='inside')
#     fig_deli_bok.update_layout(
#         paper_bgcolor='rgba(233,233,233,233)',
#         plot_bgcolor='rgba(0,0,0,0)',
#         # height=800,
#         title=f'복종별 수주량 합계',
#         title_font_size = 30,
#         # barmode='group',
#         )
#     fig_deli_bok.update_traces(
#         textposition='outside',
#         texttemplate='%{text:,}',
#         ) 

#     right_column.plotly_chart(fig_deli_bok, use_container_width=True, theme=None)
#     st.markdown('---')

#     st.write('6. 주의오더 상권, 복종별 수주량 집계')
#     left_column, right_column = st.columns([1, 6])
#     left_column.dataframe(df_true_st04_to_st55_6.groupby(['상권명', '복종'])[['수주량']].agg(sum))

#     fig_deli_tkyk = px.bar(
#         df_true_st04_to_st55_6.groupby(['상권명', '복종'])[['수주량']].agg(sum).reset_index(),
#         x='상권명',
#         y='수주량',
#         color='복종',
#         text='수주량',
#         )
#     fig_deli_tkyk.update_xaxes(ticks='outside', tickson='boundaries')
#     fig_deli_tkyk.update_yaxes(ticks='inside')
#     fig_deli_tkyk.update_layout(
#         paper_bgcolor='rgba(233,233,233,233)',
#         plot_bgcolor='rgba(0,0,0,0)',
#         # height=800,
#         title=f'상권, 복종별 수주량',
#         title_font_size = 30,
#         barmode='group',
#         )
#     fig_deli_tkyk.update_traces(
#         textposition='outside',
#         texttemplate='%{text:,}',
#         ) 

#     right_column.plotly_chart(fig_deli_tkyk, use_container_width=True, theme=None)
#     st.markdown('---')

#     st.write('7. 주의오더 일자별 생산예정량 집계')
#     left_column, right_column = st.columns([1, 5])
#     left_column.dataframe(df_true_st04_to_st55_6.groupby(['예상생산일자', '복종'])[['수주량']].agg(sum))

#     fig_prod_deli = px.bar(
#         df_true_st04_to_st55_6,
#         x='예상생산일자',
#         y='수주량',
#         color='복종',
#         # size='수주량',
#         )
#     fig_prod_deli.update_xaxes(ticks='outside', tickson='boundaries')
#     fig_prod_deli.update_yaxes(ticks='inside')
#     fig_prod_deli.update_layout(
#         paper_bgcolor='rgba(233,233,233,233)',
#         plot_bgcolor='rgba(0,0,0,0)',
#         # height=800,
#         title=f'일자별 생산예정량',
#         title_font_size = 30,
#         # barmode='group',
#         )
#     fig_prod_deli.update_xaxes(tickformat='%m-%d', dtick='day')
    
#     right_column.plotly_chart(fig_prod_deli, use_container_width=True, theme=None)
#     st.markdown('---')


#     st.markdown('8. 주의오더 타임라인 (영업확정 기준)')
    
#     bok_colors: list = px.colors.qualitative.Alphabet # plotly 알파벳 컬러셋
#     alphabets: list = [chr(i) for i in range(65, 91)] # 알파벳 리스트
#     bok_colors_dict: dict = dict(zip(alphabets, bok_colors)) # 알파벳과 컬러셋을 딕셔너리로 만들기
#     # st.write(bok_colors)
#     # st.write(alphabets)
#     # st.write(bok_colors_dict)

#     # bok_stick = st.multiselect(
#     #     '**복종을 선택하세요!**',
#     #     options=[bok for bok in df_true_st04_to_st55_6['복종'].unique()],
#     #     default=lambda ['N', 'Y', 'B'] : ,
#     #     key='bok_stick',
#     #     ) # 복종 선택 (멀티셀렉트)

#     if choosen_season_prod[-1] == 'S':
#         bok_stick = st.multiselect(
#             '**복종을 선택하세요!**',
#             options=[bok for bok in df_true_st04_to_st55_6['복종'].unique()],
#             # default=['N'],
#             key='bok_stick',
#             ) # 복종 선택 (멀티셀렉트)
#     else:
#         bok_stick = st.multiselect(
#             '**복종을 선택하세요!**',
#             options=[bok for bok in df_true_st04_to_st55_6['복종'].unique()],
#             # default=['H', 'W'],
#             key='bok_stick',
#             ) # 복종 선택 (멀티셀렉트)
#     # st.write(bok_stick)

#     fig_timeline = px.timeline(
#         df_true_st04_to_st55_6,
#         x_start='영업확정',
#         x_end='예상생산일자',
#         y='오더',
#         color='복종',
#         )
#     fig_timeline.update_xaxes(ticks='outside', tickformat='%Y-%m-%d', dtick='day')
#     fig_timeline.update_layout(
#         paper_bgcolor='rgba(233,233,233,233)',
#         plot_bgcolor='rgba(0,0,0,0)',
#         height=700,
#         title='오더별 타임라인 (영업확정 ~ 예상생산일)',
#         title_font_size=30,
#         )
#     fig_timeline.add_vrect(
#         x0=deadline_dt,
#         x1=deadline_dt,
#         line_width=2,
#         line_dash='dash',
#         fillcolor='black',
#         annotation_text=f'출고기준일 : {deadline_dt}', 
#         annotation_position='top left',
#         annotation_textangle=90,
#         annotation_font_size=20,
#         annotation_font_color='black',
#         )
#     for bok in bok_stick:
#         fig_timeline.add_vrect(
#             x0=df_deadline.loc[bok, '데드라인(영업확정)'],
#             x1=df_deadline.loc[bok, '데드라인(영업확정)'],
#             line_width=2,
#             line_color='black',
#             # line_dash='dash',
#             fillcolor=bok_colors_dict[bok],
#             annotation_text=f'{bok} : {df_deadline.loc[bok, "데드라인(영업확정)"]}', 
#             annotation_position='top right',
#             annotation_textangle=90,
#             annotation_font_size=20,
#             annotation_font_color='black',
#             )   
    
#     st.plotly_chart(fig_timeline, use_container_width=True, theme=None)

#     st.dataframe(df_deadline.reset_index().groupby(['데드라인(영업확정)'])[['복종']].agg(sum).reset_index().set_index('복종').T)
#     st.markdown('---')

#     st.markdown('9. 주의오더 타임라인 (타입일 기준)')

#     if choosen_season_prod[-1] == 'S':
#         bok_stick_taip = st.multiselect(
#             '**복종을 선택하세요!**',
#             options=[bok for bok in df_true_st04_to_st55_6['복종'].unique()],
#             # default=['J', 'H'],
#             key='bok_stick_taip',
#             ) # 복종 선택 (멀티셀렉트)
#     else:
#         bok_stick_taip = st.multiselect(
#             '**복종을 선택하세요!**',
#             options=[bok for bok in df_true_st04_to_st55_6['복종'].unique()],
#             # default=['H', 'W'],
#             key='bok_stick_taip',
#             ) # 복종 선택 (멀티셀렉트)

#     fig_timeline_taip = px.timeline(
#         df_true_st04_to_st55_6,
#         x_start='타입일',
#         x_end='예상생산일자',
#         y='오더',
#         color='복종',
#         )
#     fig_timeline_taip.update_xaxes(ticks='outside', tickformat='%Y-%m-%d', dtick='day')
#     fig_timeline_taip.update_layout(
#         paper_bgcolor='rgba(233,233,233,233)',
#         plot_bgcolor='rgba(0,0,0,0)',
#         height=700,
#         title='오더별 타임라인 (타입일 ~ 예상생산일)',
#         title_font_size=30,
#         )
#     fig_timeline_taip.add_vrect(
#         x0=deadline_dt,
#         x1=deadline_dt,
#         line_width=2,
#         line_dash='dash',
#         fillcolor='black',
#         annotation_text=f'출고기준일 : {deadline_dt}', 
#         annotation_position='top left',
#         annotation_textangle=90,
#         annotation_font_size=20,
#         annotation_font_color='black',
#         )
#     for bok in bok_stick_taip:
#         fig_timeline_taip.add_vrect(
#             x0=df_deadline.loc[bok, '데드라인(타입)'],
#             x1=df_deadline.loc[bok, '데드라인(타입)'],
#             line_width=2,
#             line_color='black',
#             # line_dash='dash',
#             fillcolor=bok_colors_dict[bok],
#             annotation_text=f'{bok} : {df_deadline.loc[bok, "데드라인(타입)"]}', 
#             annotation_position='top right',
#             annotation_textangle=90,
#             annotation_font_size=20,
#             annotation_font_color='black',
#             )   
    
#     st.plotly_chart(fig_timeline_taip, use_container_width=True, theme=None)
#     st.dataframe(df_deadline.reset_index().groupby(['데드라인(타입)'])[['복종']].agg(sum).reset_index().set_index('복종').T)

#     st.dataframe(
#         df_true_st04_to_st55_6[[
#             '오더', '상권명', '복종', '봉제업체', '수주량', '타입일',
#             '평균생산시간(일)', '타입경과일', 'STATUS', '예상생산일자',
#             f'납기준수여부({deadline_dt}까지)',
#             ]]
#     )

#     st.markdown(f'''
#     #### 주의오더 : :red[{len(df_true_st04_to_st55_6)}]건 중\n
#     #### 평균생산시간 초과 오더 : :red[{len(df_true_st04_to_st55_6[df_true_st04_to_st55_6['타입경과일'] > df_true_st04_to_st55_6['평균생산시간(일)']])}]건
#     ''')
#     st.markdown('---')

#     st.markdown('10. 주의오더 업체, 복종, 상권별 정리')

#     df_10 = df_true_st04_to_st55_6.groupby(['복종', '봉제업체', '상권명', '평균생산시간(일)', '타입경과일'])[['수주량']].agg(sum).copy().reset_index()
#     df_10['평균생산시간(일)'] = df_10['평균생산시간(일)'].astype(int)
#     df_10['타입경과일'] = df_10['타입경과일'].astype(int)
#     df_10 = df_10.sort_values(['복종', '봉제업체', '타입경과일'], ascending=[True, True, False])
                
#     st.dataframe(df_10.style.background_gradient(cmap='Blues', subset=['타입경과일', '수주량']))


#     # 사이드바 복종표
#     df_bok_info = mod.cod_code('01').drop('cod_etc', axis=1).sort_values('cod_code')
#     df_bok_info.columns = ['복종', '복종명']
#     df_bok_info = df_bok_info.set_index('복종')

#     # 사이드바 STATUS
#     df_st_info = mod.cod_code('05').drop('cod_etc', axis=1)
#     df_st_info.columns = ['STATUS', '구분']
#     df_st_info['STATUS'] = 'ST' + df_st_info['STATUS']
#     df_st_info = df_st_info.sort_values('STATUS').set_index('STATUS')
    
#     left_column, right_column = st.sidebar.columns(2)
#     left_column.dataframe(df_bok_info)
#     right_column.dataframe(df_st_info)

#     # st.dataframe(df_bok_info[['복종명']])


if selected == "체크리스트":
    st.markdown('#### 예상생산일자')
    st.markdown('##### 예상생산일자 = :red[**준비기간(대리점)**] + :green[**타입소요기간(본사)**] + :blue[**재봉기간(공장)**]')
    st.markdown('##### ST03(홀드) -> 개찰 -> :red[**준비기간(대리점)**] -> ST12(영업확정) -> :green[**타입소요기간(본사)**] -> ST40(타입) -> :blue[**재봉기간(공장)**] -> ST60(생산완료)')
    st.markdown('---')

    df_win_date = get_bid_data(choosen_season_prod) # 금년 학교코드 별 개찰일자
    df_win_date_j = get_bid_data(str(int(choosen_season_prod[:2])-1)+choosen_season_prod[-1]) # 전년 학교코드 별 개찰일자
    df_suju_order = get_suju_data(choosen_season_prod) # 금년 전체 수주데이터
    df_suju_order_j = get_suju_data(str(int(choosen_season_prod[:2])-1)+choosen_season_prod[-1]) # 전년 전체 수주데이터
    
    # 테스트
    # st.dataframe(df_suju_order_j)
    # st.write(len(df_win_date))
    # st.write(len(df_win_date_j))
    # st.write(len(df_suju_order))
    # st.write(len(df_suju_order_j))

    def bid_date_merge_and_div(df: pd.DataFrame, df_dt: pd.DataFrame) -> pd.DataFrame:
        df1 = df.merge(df_dt, how='left')
        df1 = df1[[
            '오더', '상권명', '복종', '대리점코드',
            '대리점명', '학교코드', '학교명', '학년', '봉제업체', '수주등록자',
            '수주량', '생산량', 'STATUS',
            '수주일', '수주확정', '개찰일자', '영업확정', '디자인확정',
            '부자재확정', '표준확정', '원단확정', '타입일', '재단일',
            '봉제일', '생산일', 'T/H지시일', 'T/H해제일', '홀드유지기간',
            '타입소요기간', '재봉기간', '작지문구구분', '작지문구',
            ]]
        
        df_true = df1[df1['개찰일자'].notna()] # 개찰일자 있는 것
        df_false = df1[df1['개찰일자'].isna()] # 개찰일자 없는 것

        return df_true, df_false, df1

    df_suju_order_merged_true, df_suju_order_merged_false, df_suju_order_merged = bid_date_merge_and_div(df_suju_order, df_win_date) # 금년 수주 낙찰일자 merge
    df_suju_order_merged_true_j, df_suju_order_merged_false_j, df_suju_order_merged_j = bid_date_merge_and_div(df_suju_order_j, df_win_date_j) # 전년 수주 낙찰일자 merge
    

    # 선택한 시즌따라 피크기간 던져주는 함수
    pk_date = lambda x: SPEED_DATE_S if x[-1] == 'S' else SPEED_DATE_N

    # 선택한 시즌따라 납기 던져주는 함수
    pk_deli = lambda x: DELI_DATE_S if x[-1] == 'S' else DELI_DATE_N
    
    # 복종별 평균 타입소요기간 계산
    def calc_taip_time(df: pd.DataFrame) -> pd.DataFrame:
        df_temp = df[df['타입소요기간'] > 0].copy() # 시즌 평균
        
        df_temp2 = df[(df['타입소요기간'] > 0) & (df['타입일'] >= pk_date(choosen_season_prod))].copy() # 생산속도 PEAK를 계산하기 위한 데이터
        df_bok_per = df_temp.groupby(['복종'])[['타입소요기간']].agg('mean').reset_index().round(0) # 복종별 타입에 걸리는 시간
        df_bok_per2 = df_temp2.groupby(['복종'])[['타입소요기간']].agg('mean').reset_index().round(0) # 복종별 타입에 걸리는 시간 (피크)
        df_result = pd.merge(df_bok_per, df_bok_per2, on='복종', how='left', suffixes=(' (시즌전체)', f' ({pk_date(choosen_season_prod)}이후)'))

        return df_result

    df_bok_per_time = calc_taip_time(pd.concat([df_suju_order_merged_true_j, df_suju_order_merged_false_j])) # 전년도 기준 (낙찰여부 안 따지고 전체 오더 대상으로 해야함)

    
    st.markdown('#### 타입소요기간 (본사)')
    st.markdown(f'''
    1. 영업확정 ~ 타입일 사이의 기간\n
    2. 시즌 후반부로 갈수록 빨라진다.\n
    3. :green[**이전시즌({str(int(choosen_season_prod[:2])-1)+choosen_season_prod[-1]}) 기준 {pk_date(choosen_season_prod)} 이후**]의 **타입소요기간**을 구한다. (:green[**피크기간**])
    ''')

    st.dataframe(df_bok_per_time.set_index('복종').T)
    stand_taip = st.radio(':green[**사용할 기준을 선택하세요!**]', ['피크기간', '시즌전체'], key='타입소요기간') # 시즌전체 or 피크기간
    st.write(f'선택한 기준: :red[**{stand_taip}**]')

    df_bok_per_time = df_bok_per_time.fillna(method='ffill', axis=1) # 결측치 있을때 시즌 평균으로 채우기
    if stand_taip == '피크기간':
        df_bok_per_time = df_bok_per_time.drop('타입소요기간 (시즌전체)', axis=1) # 시즌전체 타입소요기간 컬럼 삭제
    else:
        df_bok_per_time = df_bok_per_time.drop(f'타입소요기간 ({pk_date(choosen_season_prod)}이후)', axis=1) # 피크기간 타입소요기간 컬럼 삭제
    df_bok_per_time.columns = ['복종', '타입소요기간(일)']

    # 테스트
    # st.dataframe(df_bok_per_time)
    st.markdown('---')


    # ----------------------------------------------- 타입소요기간 -----------------------------------------------
    st.markdown('#### 평균생산시간 (공장)')
    st.markdown(f'''
    1. 타입일 ~ 생산일 사이의 기간\n
    2. 시즌 후반부로 갈수록 빨라진다.\n
    3. :blue[**이전시즌({str(int(choosen_season_prod[:2])-1)+choosen_season_prod[-1]}) 기준 {pk_date(choosen_season_prod)} 이후**]의 **평균생산시간**을 구한다. (:blue[**피크기간**])
    ''')
    stand_prod = st.radio(':blue[**사용할 기준을 선택하세요!**]', ['피크기간', '시즌전체'], key='평균생산시간') # 시즌전체 or 피크기간
    st.write(f'선택한 기준: :red[**{stand_prod}**]')

    def calc_average_production_time(df_dl: pd.DataFrame, df_deli_aver: pd.DataFrame, stand_val: str) -> pd.DataFrame:
        stand_val = stand_val[:2] # 2글자만 가져오기

        df_deli_peak = df_dl[df_dl['생산일'] >= pk_date(choosen_season_prod)].copy().drop(['홀드유지기간', '타입소요기간', '재봉기간'], axis=1) # 전년도 피크
        df_date_peak, _ = deli_calc(df_deli_peak)

        df_date_cut = df_deli_aver.iloc[:, 1:6].copy() # 시즌 평균
        df_date_peak_cut = df_date_peak.iloc[:, 1:6].copy() # 피크

        df_date_cut.columns = ['복종', '봉제업체', '오더수(시즌)', '평균(시즌)', '표준편차(시즌)']
        df_date_peak_cut.columns = ['복종', '봉제업체', '오더수(피크)', '평균(피크)', '표준편차(피크)']

        df_date_compare = pd.merge(df_date_cut, df_date_peak_cut, how='left', on=['복종', '봉제업체']) # 시즌 평균과 피크를 병합
        df_date_compare = df_date_compare[['복종', '봉제업체', '평균(시즌)', '평균(피크)', '표준편차(시즌)', '표준편차(피크)', '오더수(시즌)', '오더수(피크)']]
        df_date_compare = df_date_compare.fillna(method='ffill', axis=1).reset_index(drop=True) # 수치가 없는 경우 None값이 될테고 앞의 값(시즌평균)으로 채움. (axis=1은 컬럼방향)

        df_date_comp_rank = df_date_compare[['복종', '봉제업체', f'평균({stand_val})', f'오더수({stand_val})']].copy() # 생산일자 평균값 merge하기 위해 복사
        df_date_comp_rank = df_date_comp_rank.sort_values(['복종', f'평균({stand_val})', f'오더수({stand_val})'], ascending=[True, False, True]).reset_index(drop=True)
        df_date_comp_rank['오더수순위'] = df_date_comp_rank.groupby(['복종'])[[f'오더수({stand_val})']].rank(method='first', ascending=False) # 오더수 순위
        df_date_comp_rank = df_date_comp_rank[df_date_comp_rank['오더수순위'] == 1] # 오더수 순위 1위만
        df_date_comp_rank = df_date_comp_rank.drop([f'오더수({stand_val})', '오더수순위'], axis=1).reset_index(drop=True)
        df_date_comp_rank.columns = ['복종', '대표생산처', '평균생산시간(일)']
        df_date_comp_rank['평균생산시간(일)'] = df_date_comp_rank['평균생산시간(일)'].astype(int)

        return df_date_compare, df_date_comp_rank # 전체업체, 복종별 대표업체
    df_all_prod_comp_time, df_rep_comp_time = calc_average_production_time(df_deli_j, df_date_j, stand_prod)

    left_column, right_column = st.columns([3, 2])
    left_column.markdown('##### 전체업체 평균생산시간')
    left_column.dataframe(df_all_prod_comp_time.set_index('복종'))
    right_column.markdown('##### 복종별 대표업체 평균생산시간 (오더수 기준)')
    right_column.dataframe(df_rep_comp_time.set_index('복종').style.background_gradient())
    right_column.write(f"합계: {df_rep_comp_time['평균생산시간(일)'].sum()}")
    st.markdown('---')


    # ----------------------------------------------- 타입 -> 재단 -> 봉제 -> 생산 -----------------------------------------------

    st.markdown('#### 각 구간별 소요기간 (타입 -> 재단 -> 봉제 -> 생산)')

    st.markdown(f'''
    1. 타입일 -> 재단일 -> 봉제일 -> 생산일 사이의 기간 계산\n
    2. :blue[**이전시즌({str(int(choosen_season_prod[:2])-1)+choosen_season_prod[-1]}) 기준 {pk_date(choosen_season_prod)} 이후**]의 **타입 -> 재단 -> 봉제 -> 생산시간**을 구한다. (:blue[**피크기간**])
    3. 학생복시스템 기입용 날짜, 특성상 올림(ceil) 처리
    ''')
    
    # st.dataframe(df_deli_j)
    # st.dataframe(df_date_j)

    def calc_base_cut_date(df_dl: pd.DataFrame, df_deli_aver: pd.DataFrame, stand_val: str) -> pd.DataFrame:
        stand_val = stand_val[:2] # 2글자만 가져오기

        df_deli_peak = df_dl[df_dl['생산일'] >= pk_date(choosen_season_prod)].copy().drop(['홀드유지기간', '타입소요기간', '재봉기간'], axis=1) # 전년도 피크
        df_date_peak, df_date_peak_org = deli_calc_cut(df_deli_peak)

        return df_date_peak, df_date_peak_org

        # st.dataframe(df_date_peak)

        # df_date_peak_cut = df_date_peak.iloc[:, 16].copy() # 피크

        # df_date_peak_cut.columns = ['복종', '봉제업체', '오더수(피크)', '평균(피크)', '표준편차(피크)']

        # st.dataframe(df_date_cut)
        # st.dataframe(df_date_peak_cut)

        # df_date_compare = pd.merge(df_date_cut, df_date_peak_cut, how='left', on=['복종', '봉제업체']) # 시즌 평균과 피크를 병합
        # df_date_compare = df_date_compare[['복종', '봉제업체', '평균(시즌)', '평균(피크)', '표준편차(시즌)', '표준편차(피크)', '오더수(시즌)', '오더수(피크)']]
        # df_date_compare = df_date_compare.fillna(method='ffill', axis=1).reset_index(drop=True) # 수치가 없는 경우 None값이 될테고 앞의 값(시즌평균)으로 채움. (axis=1은 컬럼방향)

        # df_date_compare = df_date_peak.copy()

        # df_date_comp_rank = df_date_compare[['복종', '봉제업체', f'평균({stand_val})', f'오더수({stand_val})']].copy() # 생산일자 평균값 merge하기 위해 복사
        # df_date_comp_rank = df_date_comp_rank.sort_values(['복종', f'평균({stand_val})', f'오더수({stand_val})'], ascending=[True, False, True]).reset_index(drop=True)
        # df_date_comp_rank['오더수순위'] = df_date_comp_rank.groupby(['복종'])[[f'오더수({stand_val})']].rank(method='first', ascending=False) # 오더수 순위
        # df_date_comp_rank = df_date_comp_rank[df_date_comp_rank['오더수순위'] == 1] # 오더수 순위 1위만
        # df_date_comp_rank = df_date_comp_rank.drop([f'오더수({stand_val})', '오더수순위'], axis=1).reset_index(drop=True)
        # df_date_comp_rank.columns = ['복종', '대표생산처', '재단~생산(일)']
        # df_date_comp_rank['재단~생산(일)'] = df_date_comp_rank['재단~생산(일)'].astype(int)

        # return df_date_compare, df_date_comp_rank # 전체업체, 복종별 대표업체
    df_cut_date_base_time, df_cut_date_base_time_org = calc_base_cut_date(df_deli_j, df_date_j, stand_prod)
    # calc_base_cut_date(df_deli_j, df_date_j, stand_prod)

    # left_column, right_column = st.columns([3, 2])
    # left_column.markdown('##### 전체업체 재단~생산 시간')
    # left_column.dataframe(df_cut_date_base_time.set_index('복종'))
    # right_column.markdown('##### 복종별 대표업체 재단~생산 시간 (오더수 기준)')
    # right_column.dataframe(df_rep_comp_cut_time.set_index('복종').style.background_gradient())
    # right_column.write(f"합계: {df_rep_comp_cut_time['재단~생산(일)'].sum()}")

    st.markdown('##### 원본')
    st.dataframe(df_cut_date_base_time_org)
    st.write(len(df_cut_date_base_time_org))
    st.markdown('##### 전체업체 재단~생산 시간')
    st.dataframe(df_cut_date_base_time.style.background_gradient(subset=['타입~재단', '재단~봉제', '봉제~생산'], cmap='Greens', axis=1))
    
    st.markdown('---')

    # -------------------------------------------------------------- #
    st.markdown('#### 복종별 데드라인')
    
    deadline_dt = st.date_input('출고기준일을 지정하세요!', datetime.strptime(pk_deli(choosen_season_prod), '%Y-%m-%d')) # 납기일 변수
    # st.write(type(deadline_dt))

    st.markdown(f'''
    1. 출고기준일 : :red[**{deadline_dt}**]\n
    2. :green[**타입소요기간**] + :blue[**평균생산시간**]을 **출고기준일**부터 역으로 계산하여 데드라인을 구한다.\n
    3. **:red[데드라인 이후에 영업확정 할 경우 납기일을 못 맞출 확률이 매우 높다.]**\n
    ''')
    
    def get_deadline(df1: pd.DataFrame, df2: pd.DataFrame, dt: datetime) -> pd.DataFrame:
        df = pd.merge(df1, df2, how='left', on='복종').drop('대표생산처', axis=1)
        df['제작기간'] = df['타입소요기간(일)'] + df['평균생산시간(일)']
        df['데드라인(영업확정)'] = (pd.to_datetime(dt) - pd.to_timedelta(df['제작기간'], unit='D')).dt.date
        df['데드라인(타입)'] = (pd.to_datetime(dt) - pd.to_timedelta(df['평균생산시간(일)'], unit='D')).dt.date
        df = df.set_index('복종')
        return df
    
    df_deadline_per_bok = get_deadline(df_bok_per_time, df_rep_comp_time, deadline_dt)
    st.dataframe(df_deadline_per_bok)

    st.markdown('---')

    # -------------------------------------------------------------- #

    st.markdown('#### 지연오더 점검(ST03)')

    st.markdown(f'1. **{len(df_suju_order_merged)}** 개(ST03 ~ ST60)의 수주오더 중 낙찰일자가 확정된 오더 **:red[{len(df_suju_order_merged_true)}]** 개')
    st.markdown(f'''
    2. 낙찰일자 확정오더 **:red[{len(df_suju_order_merged_true)}]** 개 중
    **ST03**(HOLD)은 **:green[{len(df_suju_order_merged_true[df_suju_order_merged_true["STATUS"] == "03"])}]** 개
    ''')
        
    df_suju_order_merged_true_status_sum = df_suju_order_merged_true['STATUS'].value_counts().sort_index().reset_index()
    df_suju_order_merged_true_status_sum.columns = ['STATUS', '오더수']
    df_suju_order_merged_true_status_sum = df_suju_order_merged_true_status_sum.T
    df_suju_order_merged_true_status_sum.columns = df_suju_order_merged_true_status_sum.loc['STATUS']
    df_suju_order_merged_true_status_sum = df_suju_order_merged_true_status_sum.drop('STATUS')

    st.dataframe(df_suju_order_merged_true_status_sum)

    df_suju_order_merged_true_st03 = df_suju_order_merged_true[df_suju_order_merged_true['STATUS'] == '03']

    if len(df_suju_order_merged_true_st03) > 0: # ST03 오더가 있을 경우에만 실행
        st.markdown(f'''
        3. **ST03**(HOLD)오더 **:green[{len(df_suju_order_merged_true[df_suju_order_merged_true["STATUS"] == "03"])}]** 개를
        대리점, 학교명으로 그룹화하여 복종수가 가장 적은 학교 순으로 정렬
        ''')

        df_suju_order_merged_true_st03_bok = df_suju_order_merged_true_st03.groupby(['대리점명', '학교명', '학교코드'])[['복종']].agg(sum)['복종'].reset_index()
        df_suju_order_merged_true_st03_bok['복종수'] = df_suju_order_merged_true_st03_bok['복종'].str.len()
        df_suju_order_merged_true_st03_bok = df_suju_order_merged_true_st03_bok.sort_values('복종수').set_index('대리점명')

        st.dataframe(df_suju_order_merged_true_st03_bok)

        st.markdown(f'''
        4. 복종수가 2개 이상인 곳들은 제외 : 복종수가 2개 이상이면 학교요청으로 지연되었을 가능성이 높음
        ''')
        
        df_suju_order_merged_true_st03_bok_1 = df_suju_order_merged_true_st03_bok[df_suju_order_merged_true_st03_bok['복종수'] == 1]

        st.dataframe(df_suju_order_merged_true_st03_bok_1)
        # st.write(len(df_suju_order_merged_true_st03_bok_1))

        st.markdown(f'''
        5. 4번의 오더리스트에 :green[**타입소요기간**]과 :blue[**평균생산시간**]을 더한 날짜를 :violet[**예상생산일자**]로 가정한다.\n
        **:violet[예상생산일자] = 오늘날짜 + :green[타입소요기간] + :blue[평균생산시간]** \n
        또한 **:green[작지문구가 있는 오더는 납기여유가 있는 오더]** 이므로 목록에서 제외한다.
        ''')
        
        df_deli_list_st03 = pd.merge(df_suju_order_merged_true_st03_bok_1, df_rep_comp_time, on='복종', how='left') # 복종별 평균생산시간 추가
        df_deli_list_st03 = pd.merge(df_deli_list_st03, df_bok_per_time, on='복종', how='left') # 복종별 타입소요기간 추가
        df_deli_list_st03 = pd.merge(df_deli_list_st03, df_suju_order_merged_true_st03[['대리점명', '학교코드', '복종', '오더', '수주량', '작지문구구분', '작지문구', '개찰일자']], on=['학교코드', '복종'], how='left')
        df_deli_list_st03['개찰이후경과일'] = (datetime.today() - pd.to_datetime(df_deli_list_st03['개찰일자'])).dt.days
        df_deli_list_st03 = df_deli_list_st03.drop(['복종수'], axis=1)
        df_deli_list_st03['예상생산일자'] = datetime.today() + \
            pd.to_timedelta(df_deli_list_st03['타입소요기간(일)'], unit='d') + \
            pd.to_timedelta(df_deli_list_st03['평균생산시간(일)'], unit='d')
        df_deli_list_st03[f'납기준수여부({deadline_dt}까지)'] = df_deli_list_st03['예상생산일자'].apply(lambda x: 'X' if x > pd.Timestamp(deadline_dt) else 'O')

        st.dataframe(df_deli_list_st03)
        # st.write(len(df_deli_list_st03))

        df_total_cnt_st03 = df_deli_list_st03[(df_deli_list_st03[f'납기준수여부({deadline_dt}까지)'] == 'X') & (df_deli_list_st03['작지문구구분'] == 'N')]
        df_total_cnt_st03 = df_total_cnt_st03.drop(['작지문구구분'], axis=1)

        st.markdown(f'''
        6. **:red[주의가 필요한 오더리스트]**\n
        
        **:blue[- 복종수 1]**\n
        **:blue[- 작지문구 없음]**\n
        **:blue[- 예상일자 이후 출고]**\n
        \n
        **:red[총 오더수 : {len(df_total_cnt_st03)} 개]**
        ''')

        st.dataframe(df_total_cnt_st03)

        st.markdown('7. 복종별 수주량 합계')
        st.dataframe(df_total_cnt_st03.groupby(['복종'])[['수주량']].agg(sum).T)

    else: # ST03 오더가 없는 경우
        st.markdown('#### :red[ST03 오더가 없습니다.]')

    st.markdown('---')


    # ------------------------------------------------- ST03 끝 -------------------------------------------------------

    st.markdown('#### 지연오더 점검(ST04 ~ ST55)')

    st.markdown(f'1. **{len(df_suju_order_merged)}** 개(ST03 ~ ST60)의 수주오더 중 낙찰일자가 확정된 오더 **:red[{len(df_suju_order_merged_true)}]** 개')
    st.markdown(f'''
    2. 낙찰일자 확정오더 **:red[{len(df_suju_order_merged_true)}]** 개 중
    **ST04 ~ ST55**는 **:green[{len(df_suju_order_merged_true[(df_suju_order_merged_true["STATUS"] != "03") & (df_suju_order_merged_true["STATUS"] != "60")])}]** 개
    ''')
    
    st.dataframe(df_suju_order_merged_true_status_sum)

    # ST04 ~ ST55 오더만 추출 (개찰일자가 없는 오더는 제외)
    df_suju_true_st04_to_st55 = df_suju_order_merged_true[(df_suju_order_merged_true['STATUS'] != '60') & (df_suju_order_merged_true['STATUS'] != '03')]
    df_suju_true_st04_to_st55_1 = pd.merge(df_suju_true_st04_to_st55, df_bok_per_time, on='복종', how='left') # 복종별 타입소요기간 추가
    
    df_cust_per_prod_time = df_all_prod_comp_time[['복종', '봉제업체', f'평균({stand_prod[:2]})']]
    df_suju_true_st04_to_st55_2 = pd.merge(df_suju_true_st04_to_st55_1, df_cust_per_prod_time, on=['복종', '봉제업체'], how='left') # 봉제업체 매칭해서 평균생산시간 추가
    df_suju_true_st04_to_st55_2 = df_suju_true_st04_to_st55_2.rename(columns={f'평균({stand_prod[:2]})': '평균생산시간(일)'})

    df_suju_true_st04_to_st55_3_1 = df_suju_true_st04_to_st55_2[~df_suju_true_st04_to_st55_2['평균생산시간(일)'].isna()] # 생산시간 매칭된곳
    df_suju_true_st04_to_st55_3_2 = df_suju_true_st04_to_st55_2[df_suju_true_st04_to_st55_2['평균생산시간(일)'].isna()] # 생산시간 매칭안된곳 (스팟, 업체미정)
    
    df_suju_true_st04_to_st55_3_2 = df_suju_true_st04_to_st55_3_2.drop('평균생산시간(일)', axis=1) # 평균생산시간(일) 컬럼 삭제(안찍힌 컬럼이라서 삭제 후 재생성)
    df_suju_true_st04_to_st55_4_2 = pd.merge(df_suju_true_st04_to_st55_3_2, df_rep_comp_time.drop('대표생산처', axis=1), on='복종', how='left') # 매칭이 안된곳은 대표생산처 평균생산시간으로 대체(스팟, 업체미정)
    df_suju_true_st04_to_st55_4 = pd.concat([df_suju_true_st04_to_st55_3_1, df_suju_true_st04_to_st55_4_2]) # 날짜기입(타입시간, 생산시간) 완료

    
    # 예상생산일자 계산
    df_suju_true_st04_to_st55_5_1 = df_suju_true_st04_to_st55_4[~df_suju_true_st04_to_st55_4['타입일'].isna()].copy() # 타입일자가 있는 오더
    df_suju_true_st04_to_st55_5_2 = df_suju_true_st04_to_st55_4[df_suju_true_st04_to_st55_4['타입일'].isna()].copy() # 타입일자가 없는 오더
    df_suju_true_st04_to_st55_5_3 = df_suju_true_st04_to_st55_5_2[~df_suju_true_st04_to_st55_5_2['영업확정'].isna()].copy() # 타입일자가 없고, 영업확정일자가 있는 오더
    df_suju_true_st04_to_st55_5_4 = df_suju_true_st04_to_st55_5_2[df_suju_true_st04_to_st55_5_2['영업확정'].isna()].copy() # 타입일자도 없고, 영업확정일자가 없는 오더


    if len(df_suju_true_st04_to_st55_5_1) > 0: # 타입일자가 있는 오더 = 타입일 + 평균생산시간
        df_suju_true_st04_to_st55_5_1['예상생산일자'] = df_suju_true_st04_to_st55_5_1['타입일'] + \
            pd.to_timedelta(df_suju_true_st04_to_st55_5_1['평균생산시간(일)'], unit='d')
    
    if len(df_suju_true_st04_to_st55_5_3) > 0: # 타입일자가 없고, 영업확정일자가 있는 오더 = 영업확정일자 + 타입소요기간 + 평균생산시간
        df_suju_true_st04_to_st55_5_3['예상생산일자'] = df_suju_true_st04_to_st55_5_3['영업확정'] + \
            pd.to_timedelta(df_suju_true_st04_to_st55_5_3['타입소요기간(일)'], unit='d') + \
            pd.to_timedelta(df_suju_true_st04_to_st55_5_3['평균생산시간(일)'], unit='d')

    if len(df_suju_true_st04_to_st55_5_4) > 0: # 타입일자도 없고, 영업확정일자가 없는 오더 = 오늘 + 타입소요기간 + 평균생산시간
        df_suju_true_st04_to_st55_5_4['예상생산일자'] = datetime.today() + \
            pd.to_timedelta(df_suju_true_st04_to_st55_5_4['타입소요기간(일)'], unit='d') + \
            pd.to_timedelta(df_suju_true_st04_to_st55_5_4['평균생산시간(일)'], unit='d')
    
    if len(df_suju_true_st04_to_st55_5_1) > 0: 
        if len(df_suju_true_st04_to_st55_5_2) > 0:
            if len(df_suju_true_st04_to_st55_5_3) > 0:
                if len(df_suju_true_st04_to_st55_5_4) > 0:
                    df_suju_true_st04_to_st55_5 = pd.concat([df_suju_true_st04_to_st55_5_1, df_suju_true_st04_to_st55_5_3, df_suju_true_st04_to_st55_5_4])
                else:
                    df_suju_true_st04_to_st55_5 = pd.concat([df_suju_true_st04_to_st55_5_1, df_suju_true_st04_to_st55_5_3])
            else:
                df_suju_true_st04_to_st55_5 = pd.concat([df_suju_true_st04_to_st55_5_1, df_suju_true_st04_to_st55_5_4])
        else:
            df_suju_true_st04_to_st55_5 = df_suju_true_st04_to_st55_5_1.copy()
    else:
        st.write('### 오더가 없습니다.')

    df_suju_true_st04_to_st55_5[f'납기준수여부({deadline_dt}까지)'] = df_suju_true_st04_to_st55_5['예상생산일자'].apply(lambda x: 'X' if x > pd.Timestamp(deadline_dt) else 'O')
    

    st.markdown(f'''
    3. **:green[타입소요기간]** 과 **:red[평균생산시간]** 을 산입하여 **:blue[예상생산일자]** 를 계산합니다.\n\n
    **타입일자가 있는 오더 = 타입일 + 평균생산시간** \n
    **타입일자가 없고, 영업확정일자가 있는 오더 = 영업확정일자 + 타입소요기간 + 평균생산시간** \n
    **타입일자도 없고, 영업확정일자가 없는 오더 = 오늘 + 타입소요기간 + 평균생산시간** \n
    ''')

    st.dataframe(df_suju_true_st04_to_st55_5)
    st.write(len(df_suju_true_st04_to_st55_5))
    
    st.write(f'''
        타입일자가 있는 오더 : {len(df_suju_true_st04_to_st55_5_1)}개\n
        타입일자가 없는 오더 : {len(df_suju_true_st04_to_st55_5_2)}개\n
        타입일자가 없고, 영업확정일자가 있는 오더 : {len(df_suju_true_st04_to_st55_5_3)}개\n
        타입일자, 영업확정일자 없는 오더 : {len(df_suju_true_st04_to_st55_5_4)}개
    ''')


    df_suju_true_st04_to_st55_6 = df_suju_true_st04_to_st55_5[(df_suju_true_st04_to_st55_5[f'납기준수여부({deadline_dt}까지)'] == 'X') & (df_suju_true_st04_to_st55_5['작지문구구분'] == 'N')].copy()
    df_suju_true_st04_to_st55_6['개찰이후경과일'] = (df_suju_true_st04_to_st55_6['영업확정'] - df_suju_true_st04_to_st55_6['개찰일자']).dt.days
    df_suju_true_st04_to_st55_6['영업확정경과일'] = (datetime.now() - df_suju_true_st04_to_st55_6['영업확정']).dt.days
    df_suju_true_st04_to_st55_6['타입경과일'] = (datetime.now() - df_suju_true_st04_to_st55_6['타입일']).dt.days
    df_suju_true_st04_to_st55_6 = df_suju_true_st04_to_st55_6[[
        '오더', '상권명', '복종', '대리점명', '학교명',
        '봉제업체', '수주량', '개찰일자', '영업확정', '타입일',
        '타입소요기간(일)', '평균생산시간(일)', '개찰이후경과일', '영업확정경과일', '타입경과일',
        'STATUS', '예상생산일자', f'납기준수여부({deadline_dt}까지)',
        ]]
    
    
    df_suju_true_st04_to_st55_6 = df_suju_true_st04_to_st55_6.sort_values('예상생산일자').reset_index(drop=True)
    
    
    st.markdown(f'''
    4. 주의가 필요한 오더리스트 : **:red[{len(df_suju_true_st04_to_st55_6)}]** 개
    ''')
    st.dataframe(df_suju_true_st04_to_st55_6)
    st.markdown('---')


    st.write('5. 주의오더 복종별 수주량 합계')
    left_column, right_column = st.columns([1, 6])
    left_column.dataframe(df_suju_true_st04_to_st55_6.groupby(['복종'])[['수주량']].agg(sum))
    
    fig_deli_bok = px.bar(
        df_suju_true_st04_to_st55_6.groupby(['복종'])[['수주량']].agg(sum).reset_index(),
        x='복종',
        y='수주량',
        color='복종',
        text='수주량',
        )
    fig_deli_bok.update_xaxes(ticks='outside')
    fig_deli_bok.update_yaxes(ticks='inside')
    fig_deli_bok.update_layout(
        paper_bgcolor='rgba(233,233,233,233)',
        plot_bgcolor='rgba(0,0,0,0)',
        # height=800,
        title=f'복종별 수주량 합계',
        title_font_size = 30,
        # barmode='group',
        )
    fig_deli_bok.update_traces(
        textposition='outside',
        texttemplate='%{text:,}',
        ) 

    right_column.plotly_chart(fig_deli_bok, use_container_width=True, theme=None)
    st.markdown('---')

    st.write('6. 주의오더 상권, 복종별 수주량 집계')
    left_column, right_column = st.columns([1, 6])
    left_column.dataframe(df_suju_true_st04_to_st55_6.groupby(['상권명', '복종'])[['수주량']].agg(sum))

    fig_deli_tkyk = px.bar(
        df_suju_true_st04_to_st55_6.groupby(['상권명', '복종'])[['수주량']].agg(sum).reset_index(),
        x='상권명',
        y='수주량',
        color='복종',
        text='수주량',
        )
    fig_deli_tkyk.update_xaxes(ticks='outside', tickson='boundaries')
    fig_deli_tkyk.update_yaxes(ticks='inside')
    fig_deli_tkyk.update_layout(
        paper_bgcolor='rgba(233,233,233,233)',
        plot_bgcolor='rgba(0,0,0,0)',
        # height=800,
        title=f'상권, 복종별 수주량',
        title_font_size = 30,
        barmode='group',
        )
    fig_deli_tkyk.update_traces(
        textposition='outside',
        texttemplate='%{text:,}',
        ) 

    right_column.plotly_chart(fig_deli_tkyk, use_container_width=True, theme=None)
    st.markdown('---')

    st.write('7. 주의오더 일자별 생산예정량 집계')
    left_column, right_column = st.columns([1, 5])
    left_column.dataframe(df_suju_true_st04_to_st55_6.groupby(['예상생산일자', '복종'])[['수주량']].agg(sum))

    fig_prod_deli = px.bar(
        df_suju_true_st04_to_st55_6,
        x='예상생산일자',
        y='수주량',
        color='복종',
        # size='수주량',
        )
    fig_prod_deli.update_xaxes(ticks='outside', tickson='boundaries')
    fig_prod_deli.update_yaxes(ticks='inside')
    fig_prod_deli.update_layout(
        paper_bgcolor='rgba(233,233,233,233)',
        plot_bgcolor='rgba(0,0,0,0)',
        # height=800,
        title=f'일자별 생산예정량',
        title_font_size = 30,
        # barmode='group',
        )
    fig_prod_deli.update_xaxes(tickformat='%m-%d', dtick='day')
    
    right_column.plotly_chart(fig_prod_deli, use_container_width=True, theme=None)
    st.markdown('---')


    st.markdown('8. 주의오더 타임라인 (영업확정 기준)')
    
    bok_colors: list = px.colors.qualitative.Alphabet # plotly 알파벳 컬러셋
    alphabets: list = [chr(i) for i in range(65, 91)] # 알파벳 리스트
    bok_colors_dict: dict = dict(zip(alphabets, bok_colors)) # 알파벳과 컬러셋을 딕셔너리로 만들기
    # st.write(bok_colors)
    # st.write(alphabets)
    # st.write(bok_colors_dict)

    # bok_stick = st.multiselect(
    #     '**복종을 선택하세요!**',
    #     options=[bok for bok in df_suju_true_st04_to_st55_6['복종'].unique()],
    #     default=lambda ['N', 'Y', 'B'] : ,
    #     key='bok_stick',
    #     ) # 복종 선택 (멀티셀렉트)

    if choosen_season_prod[-1] == 'S':
        bok_stick = st.multiselect(
            '**복종을 선택하세요!**',
            options=[bok for bok in df_suju_true_st04_to_st55_6['복종'].unique()],
            # default=['N'],
            key='bok_stick',
            ) # 복종 선택 (멀티셀렉트)
    else:
        bok_stick = st.multiselect(
            '**복종을 선택하세요!**',
            options=[bok for bok in df_suju_true_st04_to_st55_6['복종'].unique()],
            # default=['H', 'W'],
            key='bok_stick',
            ) # 복종 선택 (멀티셀렉트)
    # st.write(bok_stick)

    fig_timeline = px.timeline(
        df_suju_true_st04_to_st55_6,
        x_start='영업확정',
        x_end='예상생산일자',
        y='오더',
        color='복종',
        )
    fig_timeline.update_xaxes(ticks='outside', tickformat='%Y-%m-%d', dtick='day')
    fig_timeline.update_layout(
        paper_bgcolor='rgba(233,233,233,233)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=700,
        title='오더별 타임라인 (영업확정 ~ 예상생산일)',
        title_font_size=30,
        )
    fig_timeline.add_vrect(
        x0=deadline_dt,
        x1=deadline_dt,
        line_width=2,
        line_dash='dash',
        fillcolor='black',
        annotation_text=f'출고기준일 : {deadline_dt}', 
        annotation_position='top left',
        annotation_textangle=90,
        annotation_font_size=20,
        annotation_font_color='black',
        )
    for bok in bok_stick:
        fig_timeline.add_vrect(
            x0=df_deadline_per_bok.loc[bok, '데드라인(영업확정)'],
            x1=df_deadline_per_bok.loc[bok, '데드라인(영업확정)'],
            line_width=2,
            line_color='black',
            # line_dash='dash',
            fillcolor=bok_colors_dict[bok],
            annotation_text=f'{bok} : {df_deadline_per_bok.loc[bok, "데드라인(영업확정)"]}', 
            annotation_position='top right',
            annotation_textangle=90,
            annotation_font_size=20,
            annotation_font_color='black',
            )   
    
    st.plotly_chart(fig_timeline, use_container_width=True, theme=None)

    st.dataframe(df_deadline_per_bok.reset_index().groupby(['데드라인(영업확정)'])[['복종']].agg(sum).reset_index().set_index('복종').T)
    st.markdown('---')

    st.markdown('9. 주의오더 타임라인 (타입일 기준)')

    if choosen_season_prod[-1] == 'S':
        bok_stick_taip = st.multiselect(
            '**복종을 선택하세요!**',
            options=[bok for bok in df_suju_true_st04_to_st55_6['복종'].unique()],
            # default=['J', 'H'],
            key='bok_stick_taip',
            ) # 복종 선택 (멀티셀렉트)
    else:
        bok_stick_taip = st.multiselect(
            '**복종을 선택하세요!**',
            options=[bok for bok in df_suju_true_st04_to_st55_6['복종'].unique()],
            # default=['H', 'W'],
            key='bok_stick_taip',
            ) # 복종 선택 (멀티셀렉트)

    fig_timeline_taip = px.timeline(
        df_suju_true_st04_to_st55_6,
        x_start='타입일',
        x_end='예상생산일자',
        y='오더',
        color='복종',
        )
    fig_timeline_taip.update_xaxes(ticks='outside', tickformat='%Y-%m-%d', dtick='day')
    fig_timeline_taip.update_layout(
        paper_bgcolor='rgba(233,233,233,233)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=700,
        title='오더별 타임라인 (타입일 ~ 예상생산일)',
        title_font_size=30,
        )
    fig_timeline_taip.add_vrect(
        x0=deadline_dt,
        x1=deadline_dt,
        line_width=2,
        line_dash='dash',
        fillcolor='black',
        annotation_text=f'출고기준일 : {deadline_dt}', 
        annotation_position='top left',
        annotation_textangle=90,
        annotation_font_size=20,
        annotation_font_color='black',
        )
    for bok in bok_stick_taip:
        fig_timeline_taip.add_vrect(
            x0=df_deadline_per_bok.loc[bok, '데드라인(타입)'],
            x1=df_deadline_per_bok.loc[bok, '데드라인(타입)'],
            line_width=2,
            line_color='black',
            # line_dash='dash',
            fillcolor=bok_colors_dict[bok],
            annotation_text=f'{bok} : {df_deadline_per_bok.loc[bok, "데드라인(타입)"]}', 
            annotation_position='top right',
            annotation_textangle=90,
            annotation_font_size=20,
            annotation_font_color='black',
            )   
    
    st.plotly_chart(fig_timeline_taip, use_container_width=True, theme=None)
    st.dataframe(df_deadline_per_bok.reset_index().groupby(['데드라인(타입)'])[['복종']].agg(sum).reset_index().set_index('복종').T)

    st.dataframe(
        df_suju_true_st04_to_st55_6[[
            '오더', '상권명', '복종', '봉제업체', '수주량', '타입일',
            '평균생산시간(일)', '타입경과일', 'STATUS', '예상생산일자',
            f'납기준수여부({deadline_dt}까지)',
            ]]
    )

    st.markdown(f'''
    #### 주의오더 : :red[{len(df_suju_true_st04_to_st55_6)}]건 중\n
    #### 평균생산시간 초과 오더 : :red[{len(df_suju_true_st04_to_st55_6[df_suju_true_st04_to_st55_6['타입경과일'] > df_suju_true_st04_to_st55_6['평균생산시간(일)']])}]건
    ''')
    st.markdown('---')

    st.markdown('10. 주의오더 업체, 복종, 상권별 정리')

    df_summ = df_suju_true_st04_to_st55_6.groupby(['복종', '봉제업체', '상권명', '평균생산시간(일)', '타입경과일'])[['수주량']].agg(sum).copy().reset_index()
    df_summ['평균생산시간(일)'] = df_summ['평균생산시간(일)'].astype(int)
    df_summ['타입경과일'] = df_summ['타입경과일'].astype(int)
    df_summ = df_summ.sort_values(['복종', '봉제업체', '타입경과일'], ascending=[True, True, False])
                
    st.dataframe(df_summ.style.background_gradient(cmap='Blues', subset=['타입경과일', '수주량']))


    # 사이드바 복종표
    df_bok_info = mod.cod_code('01').drop('cod_etc', axis=1).sort_values('cod_code')
    df_bok_info.columns = ['복종', '복종명']
    df_bok_info = df_bok_info.set_index('복종')

    # 사이드바 STATUS
    df_st_info = mod.cod_code('05').drop('cod_etc', axis=1)
    df_st_info.columns = ['STATUS', '구분']
    df_st_info['STATUS'] = 'ST' + df_st_info['STATUS']
    df_st_info = df_st_info.sort_values('STATUS').set_index('STATUS')
    
    left_column, right_column = st.sidebar.columns(2)
    left_column.dataframe(df_bok_info)
    right_column.dataframe(df_st_info)

    # st.dataframe(df_bok_info[['복종명']])


if selected == "시즌점검":
    df_code_date2 = get_bid_data(choosen_season_prod) # 학교코드 별 개찰일자
    df_delay_order2 = get_suju_data(choosen_season_prod) # 전체 수주데이터
    df_delay_order_merged2_j = get_suju_data(str(int(choosen_season_prod[:2])-1)+choosen_season_prod[-1]) # 전년도 전체 수주데이터
    
    df_delay_order_merged2 = df_delay_order2.merge(df_code_date2, how='left').copy()
    df_delay_order_merged2 = df_delay_order_merged2[[
        '오더', '상권명', 't.sort', '복종', '대리점코드',
        '대리점명', '학교코드', '학교명', '학년', '봉제업체', '수주등록자',
        '수주량', '생산량', 'STATUS', '공통학교코드', '홀드',
        '수주일', '수주확정', '개찰일자', '영업확정', '디자인확정',
        '부자재확정', '표준확정', '원단확정', '타입일', '재단일',
        '봉제일', '생산일', 'T/H지시일', 'T/H해제일', '홀드유지기간',
        '타입소요기간', '재봉기간', '작지문구구분', '작지문구',
        ]]
    
    df_delay_order_merged2_j = df_delay_order_merged2_j[[
        '오더', '상권명', 't.sort', '복종', '대리점코드',
        '대리점명', '학교코드', '학교명', '학년', '봉제업체', '수주등록자',
        '수주량', '생산량', 'STATUS', '공통학교코드', '홀드',
        '수주일', '수주확정', '영업확정', '디자인확정',
        '부자재확정', '표준확정', '원단확정', '타입일', '재단일',
        '봉제일', '생산일', 'T/H지시일', 'T/H해제일', '홀드유지기간',
        '타입소요기간', '재봉기간', '작지문구구분', '작지문구',
        ]]

    left_column, right_column = st.columns(2)
    left_column.write('##### 23N 총 오더수 (ST03 ~ ST60)')
    left_column.metric(
        '전년대비 오더 증감',
        format(len(df_delay_order_merged2), ','),
        format(len(df_delay_order_merged2)-len(df_delay_order_merged2_j), ','),
        delta_color='normal',
        )
    right_column.write('##### 23N 총 수주량 (ST03 ~ ST60)')
    right_column.metric(
        '전년대비 수주량 증감',
        format(df_delay_order_merged2["수주량"].sum(), ','),
        format(df_delay_order_merged2["수주량"].sum()-df_delay_order_merged2_j["수주량"].sum(), ','),
        delta_color='normal',
        )

    df_total_bok = df_delay_order_merged2.groupby(['복종'])[['수주량']].agg(sum).T.reset_index()
    df_total_bok = pd.concat([df_total_bok, df_delay_order_merged2_j.groupby(['복종'])[['수주량']].agg(sum).T.reset_index()])
    df_total_bok.iat[0, 0] = '23N'
    df_total_bok.iat[1, 0] = '22N'
    df_total_bok.rename(columns={'index':'시즌'}, inplace=True)
    df_total_bok = df_total_bok.set_index('시즌')
    df_total_bok.loc['23N-22N'] = df_total_bok.iloc[0] - df_total_bok.iloc[1]

    st.write('복종별 수주량')
    st.dataframe(df_total_bok)
    
    df_jacket = df_delay_order_merged2[df_delay_order_merged2['복종'] == 'J'].copy()
    df_hood = df_delay_order_merged2[df_delay_order_merged2['복종'] == 'H'].copy()
    df_jacket_j = df_delay_order_merged2_j[df_delay_order_merged2_j['복종'] == 'J'].copy()
    df_hood_j = df_delay_order_merged2_j[df_delay_order_merged2_j['복종'] == 'H'].copy()

    df_jacket['영업확정_Date'] = pd.to_datetime(df_jacket['영업확정'])
    df_jacket['영업확정_year'] = df_jacket['영업확정_Date'].dt.year
    df_jacket['영업확정_month'] = df_jacket['영업확정_Date'].dt.month
    df_jacket_j['영업확정_Date'] = pd.to_datetime(df_jacket_j['영업확정'])
    df_jacket_j['영업확정_year'] = df_jacket_j['영업확정_Date'].dt.year
    df_jacket_j['영업확정_month'] = df_jacket_j['영업확정_Date'].dt.month

    df_hood['영업확정_Date'] = pd.to_datetime(df_hood['영업확정'])
    df_hood['영업확정_year'] = df_hood['영업확정_Date'].dt.year
    df_hood['영업확정_month'] = df_hood['영업확정_Date'].dt.month
    df_hood_j['영업확정_Date'] = pd.to_datetime(df_hood_j['영업확정'])
    df_hood_j['영업확정_year'] = df_hood_j['영업확정_Date'].dt.year
    df_hood_j['영업확정_month'] = df_hood_j['영업확정_Date'].dt.month
    
    df_j_release = df_jacket.groupby(['영업확정_year', '영업확정_month'])[['수주량']].agg(sum).reset_index()
    df_h_release = df_hood.groupby(['영업확정_year', '영업확정_month'])[['수주량']].agg(sum).reset_index()
    df_j_release_j = df_jacket_j.groupby(['영업확정_year', '영업확정_month'])[['수주량']].agg(sum).reset_index()
    df_h_release_j = df_hood_j.groupby(['영업확정_year', '영업확정_month'])[['수주량']].agg(sum).reset_index()

    df_j_release['해제율'] = (df_j_release['수주량'] / df_j_release['수주량'].sum() * 100).round(2)
    df_h_release['해제율'] = (df_h_release['수주량'] / df_h_release['수주량'].sum() * 100).round(2)
    df_j_release_j['해제율'] = (df_j_release_j['수주량'] / df_j_release_j['수주량'].sum() * 100).round(2)
    df_h_release_j['해제율'] = (df_h_release_j['수주량'] / df_h_release_j['수주량'].sum() * 100).round(2)
    
    df_j_release['영업확정'] = df_j_release['영업확정_year'].astype(str) + '/' + df_j_release['영업확정_month'].astype(str)
    df_h_release['영업확정'] = df_h_release['영업확정_year'].astype(str) + '/' + df_h_release['영업확정_month'].astype(str)
    df_j_release_j['영업확정'] = df_j_release_j['영업확정_year'].astype(str) + '/' + df_j_release_j['영업확정_month'].astype(str)
    df_h_release_j['영업확정'] = df_h_release_j['영업확정_year'].astype(str) + '/' + df_h_release_j['영업확정_month'].astype(str)

    df_j_release.drop(['영업확정_year', '영업확정_month'], axis=1, inplace=True)
    df_h_release.drop(['영업확정_year', '영업확정_month'], axis=1, inplace=True)
    df_j_release_j.drop(['영업확정_year', '영업확정_month'], axis=1, inplace=True)
    df_h_release_j.drop(['영업확정_year', '영업확정_month'], axis=1, inplace=True)

    df_j_release = df_j_release[['영업확정', '수주량', '해제율']]
    df_h_release = df_h_release[['영업확정', '수주량', '해제율']]
    df_j_release_j = df_j_release_j[['영업확정', '수주량', '해제율']]
    df_h_release_j = df_h_release_j[['영업확정', '수주량', '해제율']]

    df_j_release.loc[1.5] = ['2022/6', 0, 0]
    df_j_release.loc[11] = ['2023/3', 0, 0]
    df_h_release.loc[1.5] = ['2022/6', 0, 0]
    df_h_release.loc[11] = ['2023/3', 0, 0]
    
    df_j_release_j.loc[-3] = ['2021/4', 0, 0]
    df_j_release_j.loc[-2] = ['2021/5', 0, 0]
    df_j_release_j.loc[-1] = ['2021/6', 0, 0]

    df_h_release_j.loc[-2] = ['2021/4', 0, 0]
    df_h_release_j.loc[-1] = ['2021/5', 0, 0]

    df_j_release = df_j_release.sort_index().reset_index(drop=True)
    df_h_release = df_h_release.sort_index().reset_index(drop=True)
    df_j_release_j = df_j_release_j.sort_index().reset_index(drop=True)
    df_h_release_j = df_h_release_j.sort_index().reset_index(drop=True)

    df_j_release['시즌'] = '23N'
    df_j_release_j['시즌'] = '22N'
    df_h_release['시즌'] = '23N'
    df_h_release_j['시즌'] = '22N'

    df_j_release = df_j_release[['시즌', '영업확정', '수주량', '해제율']]
    df_h_release = df_h_release[['시즌', '영업확정', '수주량', '해제율']]
    df_j_release_j = df_j_release_j[['시즌', '영업확정', '수주량', '해제율']]
    df_h_release_j = df_h_release_j[['시즌', '영업확정', '수주량', '해제율']]

    l1_column, l2_column, r1_column, r2_column = st.columns(4)
    l1_column.write('23N Jacket 해제량/해제율')
    l2_column.write('22N Jacket 해제량/해제율')
    r1_column.write('23N Hood 해제량/해제율')
    r2_column.write('22N Hood 해제량/해제율')
    l1_column.dataframe(df_j_release)
    l2_column.dataframe(df_j_release_j)
    r1_column.dataframe(df_h_release)
    r2_column.dataframe(df_h_release_j)

    df_j_release_j['영업확정'] = df_j_release['영업확정'].copy() # 그래프를 위해 영업확정 컬럼을 맞춰줌
    df_h_release_j['영업확정'] = df_h_release['영업확정'].copy()

    df_j_release_sum = pd.concat([df_j_release, df_j_release_j])
    df_h_release_sum = pd.concat([df_h_release, df_h_release_j])
    # st.dataframe(df_h_release_sum)

    # text=['{:,}<br>({:,})'.format(m, v) for m, v in zip(df_date_j['평균'], df_date_j['오더수'])],

    fig_j = px.bar(df_j_release_sum, x='영업확정', y='해제율', color='시즌',
                   title=f'J 해제량 (23N : {format(df_j_release["수주량"].sum(), ",d")} / 22N : {format(df_j_release_j["수주량"].sum(), ",d")})',
                   text=['{:,}%<br>({:,})'.format(m, v) for m, v in zip(df_j_release_sum['해제율'], df_j_release_sum['수주량'])],
                   )
    fig_j.update_yaxes(title_text='해제율(%)')
    fig_j.update_layout(barmode='group')

    fig_h = px.bar(df_h_release_sum, x='영업확정', y='해제율', color='시즌', color_discrete_sequence=['Green', 'LightGreen'],
                   title=f'H 해제량 (23N : {format(df_h_release["수주량"].sum(), ",d")} / 22N : {format(df_h_release_j["수주량"].sum(), ",d")})',
                   text=['{:,}%<br>({:,})'.format(m, v) for m, v in zip(df_h_release_sum['해제율'], df_h_release_sum['수주량'])],
                   )
    fig_h.update_yaxes(title_text='해제율(%)')
    fig_h.update_layout(barmode='group')
    
    st.plotly_chart(fig_j, use_container_width=True)
    st.plotly_chart(fig_h, use_container_width=True)


# -------------------------------------------------------------------------------------------------------
    df_j_release_tkyk = df_jacket.groupby(['상권명', '영업확정_year', '영업확정_month'])[['수주량']].agg(sum).reset_index()
    df_h_release_tkyk = df_hood.groupby(['상권명', '영업확정_year', '영업확정_month'])[['수주량']].agg(sum).reset_index()
    df_j_release_tkyk_j = df_jacket_j.groupby(['상권명', '영업확정_year', '영업확정_month'])[['수주량']].agg(sum).reset_index()
    df_h_release_tkyk_j = df_hood_j.groupby(['상권명', '영업확정_year', '영업확정_month'])[['수주량']].agg(sum).reset_index()

    df_j_release_tkyk = df_j_release_tkyk.sort_values(by=['상권명', '영업확정_year', '영업확정_month'])
    df_h_release_tkyk = df_h_release_tkyk.sort_values(by=['상권명', '영업확정_year', '영업확정_month'])
    df_j_release_tkyk_j = df_j_release_tkyk_j.sort_values(by=['상권명', '영업확정_year', '영업확정_month'])
    df_h_release_tkyk_j = df_h_release_tkyk_j.sort_values(by=['상권명', '영업확정_year', '영업확정_month'])

    # df_j_release_tkyk['해제율'] = (df_j_release_tkyk['수주량'] / df_j_release_tkyk['수주량'].sum() * 100).round(2)
    # df_h_release_tkyk['해제율'] = (df_h_release_tkyk['수주량'] / df_h_release_tkyk['수주량'].sum() * 100).round(2)
    # df_j_release_tkyk_j['해제율'] = (df_j_release_tkyk_j['수주량'] / df_j_release_tkyk_j['수주량'].sum() * 100).round(2)
    # df_h_release_tkyk_j['해제율'] = (df_h_release_tkyk_j['수주량'] / df_h_release_tkyk_j['수주량'].sum() * 100).round(2)

    # df_j_release_tkyk_j['영업확정_year'] = df_j_release_tkyk_j['영업확정_year'] + 1
    # df_h_release_tkyk_j['영업확정_year'] = df_h_release_tkyk_j['영업확정_year'] + 1
    
    df_j_release_tkyk['영업확정'] = df_j_release_tkyk['영업확정_year'].astype(str) + '/' + df_j_release_tkyk['영업확정_month'].astype(str)
    df_h_release_tkyk['영업확정'] = df_h_release_tkyk['영업확정_year'].astype(str) + '/' + df_h_release_tkyk['영업확정_month'].astype(str)
    df_j_release_tkyk_j['영업확정'] = (df_j_release_tkyk_j['영업확정_year']+1).astype(str) + '/' + df_j_release_tkyk_j['영업확정_month'].astype(str)
    df_h_release_tkyk_j['영업확정'] = (df_h_release_tkyk_j['영업확정_year']+1).astype(str) + '/' + df_h_release_tkyk_j['영업확정_month'].astype(str)

    df_j_release_tkyk['시즌'] = '23N'
    df_j_release_tkyk_j['시즌'] = '22N'
    df_h_release_tkyk['시즌'] = '23N'
    df_h_release_tkyk_j['시즌'] = '22N'

    df_j_release_tkyk = df_j_release_tkyk[['시즌', '상권명', '영업확정', '수주량']]
    df_j_release_tkyk_j = df_j_release_tkyk_j[['시즌', '상권명', '영업확정', '수주량']]
    df_h_release_tkyk = df_h_release_tkyk[['시즌', '상권명', '영업확정', '수주량']]
    df_h_release_tkyk_j = df_h_release_tkyk_j[['시즌', '상권명', '영업확정', '수주량']]

    df_j_release_tkyk_piv = df_j_release_tkyk.pivot_table(index='상권명', columns='영업확정', values='수주량', aggfunc='sum', fill_value=0)
    df_j_release_tkyk_piv['2022/6'] = 0
    df_j_release_tkyk_piv['2023/3'] = 0
    df_j_release_tkyk_piv = df_j_release_tkyk_piv[['2022/4', '2022/5', '2022/6', '2022/7', '2022/8', '2022/9', '2022/10', '2022/11', '2022/12', '2023/1', '2023/2', '2023/3']]
    df_j_release_tkyk_piv['sort'] = [3, 4, 2, 5, 0, 1]
    df_j_release_tkyk_piv.sort_values(by='sort', inplace=True)
    df_j_release_tkyk_piv.drop('sort', axis=1, inplace=True)

    df_h_release_tkyk_piv = df_h_release_tkyk.pivot_table(index='상권명', columns='영업확정', values='수주량', aggfunc='sum', fill_value=0)
    df_h_release_tkyk_piv['2022/6'] = 0
    df_h_release_tkyk_piv['2023/3'] = 0
    df_h_release_tkyk_piv = df_h_release_tkyk_piv[['2022/4', '2022/5', '2022/6', '2022/7', '2022/8', '2022/9', '2022/10', '2022/11', '2022/12', '2023/1', '2023/2', '2023/3']]
    df_h_release_tkyk_piv['sort'] = [3, 4, 2, 5, 0, 1]
    df_h_release_tkyk_piv.sort_values(by='sort', inplace=True)
    df_h_release_tkyk_piv.drop('sort', axis=1, inplace=True)
    
    df_j_release_tkyk_j_piv = df_j_release_tkyk_j.pivot_table(index='상권명', columns='영업확정', values='수주량', aggfunc='sum', fill_value=0)
    df_j_release_tkyk_j_piv['2022/4'] = 0
    df_j_release_tkyk_j_piv['2022/5'] = 0
    df_j_release_tkyk_j_piv['2022/6'] = 0
    df_j_release_tkyk_j_piv = df_j_release_tkyk_j_piv[['2022/4', '2022/5', '2022/6', '2022/7', '2022/8', '2022/9', '2022/10', '2022/11', '2022/12', '2023/1', '2023/2', '2023/3']]
    df_j_release_tkyk_j_piv['sort'] = [3, 4, 2, 5, 0, 1]
    df_j_release_tkyk_j_piv.sort_values(by='sort', inplace=True)
    df_j_release_tkyk_j_piv.drop('sort', axis=1, inplace=True)

    df_h_release_tkyk_j_piv = df_h_release_tkyk_j.pivot_table(index='상권명', columns='영업확정', values='수주량', aggfunc='sum', fill_value=0)
    df_h_release_tkyk_j_piv['2022/4'] = 0
    df_h_release_tkyk_j_piv['2022/5'] = 0
    df_h_release_tkyk_j_piv = df_h_release_tkyk_j_piv[['2022/4', '2022/5', '2022/6', '2022/7', '2022/8', '2022/9', '2022/10', '2022/11', '2022/12', '2023/1', '2023/2', '2023/3']]
    df_h_release_tkyk_j_piv['sort'] = [3, 4, 2, 5, 0, 1]
    df_h_release_tkyk_j_piv.sort_values(by='sort', inplace=True)
    df_h_release_tkyk_j_piv.drop('sort', axis=1, inplace=True)

 
    left_column, right_column = st.columns(2)
    left_column.write('23N J 상권별 해제량')
    left_column.dataframe(df_j_release_tkyk_piv.style.background_gradient(cmap='Blues', axis=1))
    right_column.write('23N H 상권별 해제량')
    right_column.dataframe(df_h_release_tkyk_piv.style.background_gradient(cmap='Greens', axis=1))
    left_column.write('22N J 상권별 해제량')
    left_column.dataframe(df_j_release_tkyk_j_piv.style.background_gradient(cmap='Blues', axis=1))
    right_column.write('22N H 상권별 해제량')
    right_column.dataframe(df_h_release_tkyk_j_piv.style.background_gradient(cmap='Greens', axis=1))


    df_j_release_tkyk_piv['시즌'] = '23N'
    df_h_release_tkyk_piv['시즌'] = '23N'
    df_j_release_tkyk_j_piv['시즌'] = '22N'
    df_h_release_tkyk_j_piv['시즌'] = '22N'

    df_j_release_tkyk_piv.reset_index(inplace=True)
    df_h_release_tkyk_piv.reset_index(inplace=True)
    df_j_release_tkyk_j_piv.reset_index(inplace=True)
    df_h_release_tkyk_j_piv.reset_index(inplace=True)

    # 그래프용(막대그래프)
    plot_temp_j = df_j_release_tkyk_piv.melt(id_vars=['상권명', '시즌'], var_name='영업확정', value_name='수주량')
    plot_temp_j_j = df_j_release_tkyk_j_piv.melt(id_vars=['상권명', '시즌'], var_name='영업확정', value_name='수주량')
    plot_temp_h = df_h_release_tkyk_piv.melt(id_vars=['상권명', '시즌'], var_name='영업확정', value_name='수주량')
    plot_temp_h_j = df_h_release_tkyk_j_piv.melt(id_vars=['상권명', '시즌'], var_name='영업확정', value_name='수주량')


    df_j_release_tkyk_piv_per = df_j_release_tkyk_piv.copy() # 비율 계산용
    df_h_release_tkyk_piv_per = df_h_release_tkyk_piv.copy()
    df_j_release_tkyk_j_piv_per = df_j_release_tkyk_j_piv.copy()
    df_h_release_tkyk_j_piv_per = df_h_release_tkyk_j_piv.copy()

    df_j_release_tkyk_piv_per['계'] = df_j_release_tkyk_piv_per.sum(numeric_only=True, axis=1)
    df_h_release_tkyk_piv_per['계'] = df_h_release_tkyk_piv_per.sum(numeric_only=True, axis=1)
    df_j_release_tkyk_j_piv_per['계'] = df_j_release_tkyk_j_piv_per.sum(numeric_only=True, axis=1)
    df_h_release_tkyk_j_piv_per['계'] = df_h_release_tkyk_j_piv_per.sum(numeric_only=True, axis=1)

    # 비율 계산
    df_j_release_tkyk_piv_per = (df_j_release_tkyk_piv_per.iloc[:, 1:13].div(df_j_release_tkyk_piv_per['계'], axis=0))
    df_h_release_tkyk_piv_per = (df_h_release_tkyk_piv_per.iloc[:, 1:13].div(df_h_release_tkyk_piv_per['계'], axis=0))
    df_j_release_tkyk_j_piv_per = (df_j_release_tkyk_j_piv_per.iloc[:, 1:13].div(df_j_release_tkyk_j_piv_per['계'], axis=0))
    df_h_release_tkyk_j_piv_per = (df_h_release_tkyk_j_piv_per.iloc[:, 1:13].div(df_h_release_tkyk_j_piv_per['계'], axis=0))

    df_j_release_tkyk_piv_per['상권명'] = df_j_release_tkyk_piv['상권명'].copy()
    df_h_release_tkyk_piv_per['상권명'] = df_h_release_tkyk_piv['상권명'].copy()
    df_j_release_tkyk_j_piv_per['상권명'] = df_j_release_tkyk_j_piv['상권명'].copy()
    df_h_release_tkyk_j_piv_per['상권명'] = df_h_release_tkyk_j_piv['상권명'].copy()

    # 그래프용(선그래프)
    plot_temp_per_j = df_j_release_tkyk_piv_per.melt(id_vars=['상권명'], var_name='영업확정', value_name='비율')
    plot_temp_per_h = df_h_release_tkyk_piv_per.melt(id_vars=['상권명'], var_name='영업확정', value_name='비율')
    plot_temp_per_j_j = df_j_release_tkyk_j_piv_per.melt(id_vars=['상권명'], var_name='영업확정', value_name='비율')
    plot_temp_per_h_j = df_h_release_tkyk_j_piv_per.melt(id_vars=['상권명'], var_name='영업확정', value_name='비율')

    plot_temp_per_j['시즌'] = '23N'
    plot_temp_per_h['시즌'] = '23N'
    plot_temp_per_j_j['시즌'] = '22N'
    plot_temp_per_h_j['시즌'] = '22N'

    # st.dataframe(df_j_release_tkyk_piv_per.style.background_gradient(cmap='Blues', axis=1))
    # st.dataframe(plot_temp_per_j.style.background_gradient(cmap='Blues', axis=1))

    # 시즌 격차 계산
    # df_j_per_minus = df_j_release_tkyk_piv_per.set_index('상권명') - df_j_release_tkyk_j_piv_per.set_index('상권명')
    # df_h_per_minus = df_h_release_tkyk_piv_per.set_index('상권명') - df_h_release_tkyk_j_piv_per.set_index('상권명')

    # left_column, right_column = st.columns(2)
    # left_column.dataframe(df_j_release_tkyk_piv_per.style.background_gradient(cmap='Blues', axis=1))
    # right_column.dataframe(df_h_release_tkyk_piv_per.style.background_gradient(cmap='Greens', axis=1))
    # left_column.dataframe(df_j_release_tkyk_j_piv_per.style.background_gradient(cmap='Blues', axis=1))
    # right_column.dataframe(df_h_release_tkyk_j_piv_per.style.background_gradient(cmap='Greens', axis=1))

    # left_column.dataframe(df_j_per_minus.style.background_gradient(cmap='reds', axis=1))
    # right_column.dataframe(df_h_per_minus.style.background_gradient(cmap='Reds', axis=1))


    for tkyk in ['서울상권', '중부상권', '대전상권', '광주상권', '대구상권', '부산상권']:
        # 바차트용
        df_plot_j = pd.concat([plot_temp_j[plot_temp_j['상권명'] == tkyk], plot_temp_j_j[plot_temp_j_j['상권명'] == tkyk]])
        df_plot_h = pd.concat([plot_temp_h[plot_temp_h['상권명'] == tkyk], plot_temp_h_j[plot_temp_h_j['상권명'] == tkyk]])
        
        df_plot_per_j = pd.concat([plot_temp_per_j[plot_temp_per_j['상권명'] == tkyk], plot_temp_per_j_j[plot_temp_per_j_j['상권명'] == tkyk]])
        df_plot_per_h = pd.concat([plot_temp_per_h[plot_temp_per_h['상권명'] == tkyk], plot_temp_per_h_j[plot_temp_per_h_j['상권명'] == tkyk]])

        df_plot_j_sum = df_plot_j.merge(df_plot_per_j, on=['상권명', '영업확정', '시즌'], how='left')
        df_plot_h_sum = df_plot_h.merge(df_plot_per_h, on=['상권명', '영업확정', '시즌'], how='left')        

        # st.dataframe(df_plot_j_sum.style.background_gradient(cmap='Blues', axis=1))

        fig_j_tkyk = px.bar(df_plot_j_sum, x='영업확정', y=(df_plot_j_sum['비율']*100).round(2), color='시즌', barmode='group',
                            title=f'{tkyk} J 해제율 (수주량 23N : {format(df_plot_j[df_plot_j["시즌"]=="23N"]["수주량"].sum(), ",d")} / 22N : {format(df_plot_j[df_plot_j["시즌"]=="22N"]["수주량"].sum(), ",d")})',
                            text=['{:,}%<br>({:,})'.format(m, v) for m, v in zip((df_plot_j_sum['비율']*100).round(2), df_plot_j_sum['수주량'])],
                            )
        fig_j_tkyk.update_yaxes(title_text='해제율(%)')
        fig_h_tkyk = px.bar(df_plot_h_sum, x='영업확정', y=(df_plot_h_sum['비율']*100).round(2), color='시즌', barmode='group',
                            title=f'{tkyk} H 해제율 (수주량 23N : {format(df_plot_h[df_plot_h["시즌"]=="23N"]["수주량"].sum(), ",d")} / 22N : {format(df_plot_h[df_plot_h["시즌"]=="22N"]["수주량"].sum(), ",d")})',
                            text=['{:,}%<br>({:,})'.format(m, v) for m, v in zip((df_plot_h_sum['비율']*100).round(2), df_plot_h_sum['수주량'])],
                            color_discrete_sequence=['Green', 'LightGreen'],
                            )
        fig_h_tkyk.update_yaxes(title_text='해제율(%)')
        

        st.markdown(f'##### {tkyk}')
        st.plotly_chart(fig_j_tkyk, use_container_width=True)
        st.plotly_chart(fig_h_tkyk, use_container_width=True)

        st.markdown('---')

if selected == "시즌점검2":
    df_code_date3 = get_bid_data(choosen_season_prod) # 학교코드 별 개찰일자
    df_delay_order3 = get_suju_data(choosen_season_prod) # 전체 수주데이터
    
    df_delay_order_merged3 = df_delay_order3.merge(df_code_date3, how='left').copy()
    df_delay_order_merged3 = df_delay_order_merged3[[
        '오더', '상권명', '복종', '대리점코드',
        '대리점명', '학교코드', '학교명', '학년', '봉제업체', '수주등록자',
        '수주량', '생산량', 'STATUS',
        '수주일', '수주확정', '개찰일자', '영업확정', '디자인확정',
        '부자재확정', '표준확정', '원단확정', '타입일', '재단일',
        '봉제일', '생산일', '홀드유지기간',
        '타입소요기간', '재봉기간', '작지문구구분', '작지문구',
        ]]

    # st.write(df_delay_order_merged2.shape)

    df_delay_order_merged3['차수'] = df_delay_order_merged3['오더'].str.split(' ').str[1].astype(int)

    # 제외조건
    over_cond1 = df_delay_order_merged3['차수'] > 3 # 4차 이상
    over_cond2 = df_delay_order_merged3['학교코드'].str[0] != 'D' # 본사공통 제외

    search_list = ['충남표준', '충북표준']
    over_cond3 = df_delay_order_merged3['학교명'].str.contains('|'.join(search_list)) # 충남표준, 충북표준 제외
    over_cond4 = df_delay_order_merged3['작지문구구분'] == 'N' # 3월납기 제외

    df_over_ser = df_delay_order_merged3[ over_cond1 & over_cond2 & ~over_cond3 & over_cond4 ]

    st.markdown(f'#### 4차 이상, 본사공통 제외, 충남표준, 충북표준 제외, 3월납기 제외 : {len(df_over_ser)}건')
    st.dataframe(df_over_ser.reset_index(drop=True))
    st.dataframe(df_over_ser.groupby('복종').agg({'수주량':'sum', '오더': 'count'}).T)
    st.markdown('---')

    # 분리조건
    div_cond1 = df_over_ser['학교명'].str.contains('공통') # 대리점 공통

    df_div_common = df_over_ser[ div_cond1 ] # 대리점 공통
    df_div_win = df_over_ser[ ~div_cond1 ] # 낙찰분
    df_div_no_hgb = df_div_win[ df_div_win['학년'] == 'N' ]  # 낙찰분 중 학년별 제외
    df_div_hgb = df_div_win[ df_div_win['학년'] != 'N' ]  # 낙찰분 중 학년별

    st.markdown(f'#### 대리점 공통 : {len(df_div_common)}건')
    st.dataframe(df_div_common.sort_values('차수', ascending=False).reset_index(drop=True))
    st.dataframe(df_div_common.groupby('복종').agg({'수주량': 'sum', '오더': 'count'}).T)
    st.markdown('---')

    st.markdown(f'#### 학년별 아닌 것 : {len(df_div_no_hgb)}건')
    st.dataframe(df_div_no_hgb.sort_values('차수', ascending=False).reset_index(drop=True))
    st.dataframe(df_div_no_hgb.groupby('복종').agg({'수주량': 'sum', '오더': 'count'}).T)
    st.markdown('---')

    st.markdown(f'#### 학년별 : {len(df_div_hgb)}건')
    st.dataframe(df_div_hgb.sort_values(['오더', '학년'], ascending=[True, True]).reset_index(drop=True))
    st.dataframe(df_div_hgb.groupby('복종').agg({'수주량': 'sum', '오더': 'count'}).T)
    st.markdown('---')

    # ------------------------------------------------------------------------------
    
    delay_cond1 = df_delay_order_merged3['차수'] == 1
    delay_cond2 = df_delay_order_merged3['개찰일자'].notna()
    delay_cond3 = df_delay_order_merged3['영업확정'] > '2023-01-31'
    delay_cond4 = df_delay_order_merged3['작지문구구분'] == 'N'

    df_delay_order_merged3['개찰_확정소요시간'] = (df_delay_order_merged3['수주확정'] - df_delay_order_merged3['개찰일자']).dt.days

    st.markdown(f'#### 2월 이후 영업확정, 수주 1차, 작지문구 없음 : {len(df_delay_order_merged3[ delay_cond1 & delay_cond2 & delay_cond3 &delay_cond4 ])}건')
    st.dataframe(df_delay_order_merged3[ delay_cond1 & delay_cond2 & delay_cond3 & delay_cond4 ].sort_values(['개찰_확정소요시간'], ascending=[False]).reset_index(drop=True))


# if selected == "공사중":
#     def sample_suju():
#         sql = f'''
#         SELECT  j.master2_tkyk,
#                 utl_raw.Cast_to_raw(a.agen_name) agen_name,
#                 utl_raw.Cast_to_raw(s.sch_name) sch_name,
#                 j.master2_bokjong,
#                 j.master2_suju_qty,
#                 To_char(j.master2_deli, 'yy/mm/dd'),
#                 j.master2_status,
#                 j.master2_order
#             FROM   i_tkyk_t t,
#                 i_agen_t a,
#                 i_sch_t s,
#                 i_suju_master2_t j,
#                 i_suju_fact_t f,
#                 i_suju_master_sample js,
#                 i_suju_stand_t s1,
#                 i_suju_stand_t s2,
#                 i_cust_t n,
#                 i_cod_t tt,
#                 i_cod_t PP,
#                 i_suju_stand_t s3,
#                 i_suju_stand_t s4,
#                 i_suju_stand_t s5,
#                 i_suju_stand_t s6,
#                 i_stand_bkjk_sample_t b
#             WHERE  js.smp_order = j.master2_order
#                 AND t.tkyk_code(+) = j.master2_tkyk
#                 AND a.agen_code(+) = j.master2_agent
#                 AND s.sch_code(+) = j.master2_school
#                 AND b.bkjk_squota(+) = j.master2_squota
#                 AND b.bkjk_school(+) = j.master2_school
#                 AND b.bkjk_bokjong(+) = j.master2_bokjong
#                 AND b.bkjk_ser(+) = j.master2_ser
#                 AND tt.cod_code = j.master2_bokjong
#                 AND tt.cod_gbn_code = '01'
#                 AND f.fact_order(+) = j.master2_order
#                 AND f.fact_year(+) = j.master2_year
#                 AND f.fact_season(+) = j.master2_season
#                 AND n.cust_code(+) = f.fact_code
#                 AND s1.stand_order(+) = j.master2_order
#                 AND s1.stand_sojae_gbn(+) = '1'
#                 AND s2.stand_order(+) = j.master2_order
#                 AND s2.stand_sojae_gbn(+) = '3'
#                 AND s3.stand_order(+) = j.master2_order
#                 AND s3.stand_sojae_gbn(+) = '4'
#                 AND s4.stand_order(+) = j.master2_order
#                 AND s4.stand_sojae_gbn(+) = '5'
#                 AND s5.stand_order(+) = j.master2_order
#                 AND s5.stand_sojae_gbn(+) = '6'
#                 AND s6.stand_order(+) = j.master2_order
#                 AND s6.stand_sojae_gbn(+) = '7'
#                 AND pp.cod_gbn_code(+) = 'PY'
#                 AND pp.cod_code(+) = j.master2_bokjong
#                 AND j.master2_remake = 'S'
#                 AND j.master2_status >= '03'
#                 AND j.master2_status <= '60'
#                 AND j.master2_jaepum IN( 'H', 'A', 'B' )
#                 AND j.master2_quota = '23N' 
#         '''
#         df = mod.select_data(sql)
#         return df
#     df1 = sample_suju()
#     st.dataframe(df1)

# ------------------------------------------------------------------------------

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

    S_E_L_TYPE_QTY = st.text_input('2. 스마트, 엘리트, 스쿨룩스 순으로 타입량을 입력하세요.', '19000, 17000, 16000')
    st.write('입력된 값 : ', S_E_L_TYPE_QTY)

    S_E_L_CHULGO_QTY = st.text_input('3. 스마트, 엘리트, 스쿨룩스 순으로 출고량을 입력하세요.', '8000, 9000, 4000')
    st.write('입력된 값 : ', S_E_L_CHULGO_QTY)


# -------------------- HIDE STREAMLIT STYLE --------------------
hide_st_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """
st.markdown(hide_st_style, unsafe_allow_html=True)
