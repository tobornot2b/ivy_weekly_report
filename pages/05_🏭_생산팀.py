import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
S_E_L_type_qty: list = [135000, 130000, 108000]
S_E_L_chulgo_qty: list = [107000, 106000, 89000]


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
    if season[-1] != 'S':
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
    else:
        pass



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
# @st.cache_data
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
           AND j.master_jaepum IN( 'H', 'A', 'B' )
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
    df['타입소요기간'] = df['타입일'] - df['원단확정']
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
           AND j.master_jaepum IN( 'H', 'A', 'B' )
           AND j.master_quota = '{season}'
    ORDER  BY t.sort, agen_name, tt.sort
    '''
    
    df_suju_data = mod.select_data(sql)

    df_suju_data.columns = [
        '오더', '상권명', 't.sort' ,'복종', '대리점코드',
        '대리점명', '학교코드', '학교명', '봉제업체', '수주등록자',
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
    df_suju_data['타입소요기간'] = df_suju_data['타입일'] - df_suju_data['원단확정']
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
    options=['23N', '23S'],
)


# 조회조건 변수들
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


# 업체별 동복 자켓 진행 현황
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
                options=['진행현황', '진행현황(상세)', '생산시간', '체크리스트'],  # required
                icons=['forward-fill', 'speedometer', 'play-fill', 'list-check'],  # optional
                menu_icon="cast",  # optional
                default_index=0,  # optional
            )
        return selected

    if example == 2:
        # 2. horizontal menu w/o custom style
        selected = option_menu(
            menu_title=None,  # required
            options=['진행현황', '진행현황(상세)', '생산시간', '체크리스트'],  # required
            icons=['forward-fill', 'speedometer', 'play-fill', 'list-check'],  # optional
            menu_icon="cast",  # optional
            default_index=0,  # optional
            orientation="horizontal",
        )
        return selected

    if example == 3:
        # 2. horizontal menu with custom style
        selected = option_menu(
            menu_title=None,  # required
            options=['진행현황', '진행현황(상세)', '생산시간', '체크리스트'],  # required
            icons=['forward-fill', 'speedometer', 'play-fill', 'list-check'],  # optional
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
                "nav-link-selected": {"background-color": "#B6D317"},
            },
        )
        return selected


selected = streamlit_menu(example=EXAMPLE_NO)


if selected == "진행현황":

    st.markdown('##### ◆ 23년 동복 생산진행 현황 (23N/22F)')
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


    st.markdown("##### ◆ 업체별 동복 자켓 진행 현황")

    st.dataframe(df_major4, use_container_width=True)
    left_column, right_column = st.columns(2)
    left_column.plotly_chart(fig2, use_container_width=True, theme=None)
    right_column.plotly_chart(fig3, use_container_width=True, theme=None)

    # st.dataframe(df_major4_graph)


if selected == "진행현황(상세)":
    st.markdown('##### ◆ STATUS별 진행현황')
    
    df_status = data_preprocess2(df_base)

    # st.dataframe(df_base, use_container_width=True)
    # st.dataframe(df_status.set_index(['제품']), use_container_width=True)
    st.dataframe(df_status.style.background_gradient(subset=["ST03"]), use_container_width=True)
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
    
    left_column, right_column = st.columns([1, 4])
    sel_bj = left_column.select_slider(
        '복종을 선택하세요',
        options=sorted(plot_df_8['복종'].unique()),
        )
    # left_column.write(f'{sel_bj} 선택')

    # 업체가 1개면 select_slider는 에러난다. 1 ~ 1을 찾는 꼴.
    sel_comp = left_column.selectbox(
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



if selected == "체크리스트":
    st.markdown('##### 지연오더 체크')

    df_code_date = get_bid_data(choosen_season_prod) # 학교코드 별 개찰일자
    df_delay_order = get_suju_data(choosen_season_prod) # 학교코드 별 수주일자
    
    # st.dataframe(df_delay_order)
    # st.write(df_delay_order.shape)
    
    df_delay_order_merged = df_delay_order.merge(df_code_date, how='left')
    df_delay_order_merged = df_delay_order_merged[[
        '오더', '상권명', 't.sort', '복종', '대리점코드',
        '대리점명', '학교코드', '학교명', '봉제업체', '수주등록자',
        '수주량', '생산량', 'STATUS', '공통학교코드', '홀드',
        '수주일', '수주확정', '개찰일자', '영업확정', '디자인확정',
        '부자재확정', '표준확정', '원단확정', '타입일', '재단일',
        '봉제일', '생산일', 'T/H지시일', 'T/H해제일', '홀드유지기간',
        '타입소요기간', '재봉기간', '작지문구구분', '작지문구',
        ]]

    # st.dataframe(df_delay_order_merged)
    # st.write(df_delay_order_merged.shape)

    df_bid_date_true = df_delay_order_merged[~df_delay_order_merged['개찰일자'].isna()]
    # df_bid_date_false = df_delay_order_merged[df_delay_order_merged['개찰일자'].isna()] # 개찰일자에 없는 것들

    # st.dataframe(df_delay_order_merged, use_container_width=True)
    # st.write(df_delay_order_merged.shape)

    # st.markdown('This text is :red[colored red], and this is **:blue[colored]** and bold.') # 텍스트 컬러적용 예시
    st.markdown(f'1. **{len(df_delay_order_merged)}** 개(ST03 ~ ST60)의 수주오더 중 낙찰일자가 확정된 오더 **:red[{len(df_bid_date_true)}]** 개')
    st.markdown(f'''
    2. 낙찰일자 확정오더 **:red[{len(df_bid_date_true)}]** 개 중
    **ST03**(HOLD)은 **:green[{len(df_bid_date_true[df_bid_date_true["STATUS"] == "03"])}]** 개
    ''')
        
    df_bid_date_true_not60 = df_bid_date_true['STATUS'].value_counts().sort_index().reset_index()
    df_bid_date_true_not60.columns = ['STATUS', '오더수']
    df_bid_date_true_not60 = df_bid_date_true_not60.T
    df_bid_date_true_not60.columns = df_bid_date_true_not60.loc['STATUS']
    df_bid_date_true_not60 = df_bid_date_true_not60.drop('STATUS')

    st.dataframe(df_bid_date_true_not60)


    st.markdown(f'''
    3. **ST03**(HOLD)오더 **:green[{len(df_bid_date_true[df_bid_date_true["STATUS"] == "03"])}]** 개를
    대리점, 학교명으로 그룹화하여 복종수가 가장 적은 학교 순으로 정렬
    ''')

    df_true_st03 = df_bid_date_true[df_bid_date_true['STATUS'] == '03']
    df_true_st03_bok = df_true_st03.groupby(['대리점명', '학교명', '학교코드'])[['복종']].agg(sum)['복종'].reset_index()
    df_true_st03_bok['복종수'] = df_true_st03_bok['복종'].str.len()
    df_true_st03_bok = df_true_st03_bok.sort_values('복종수').set_index('대리점명')

    st.dataframe(df_true_st03_bok)

    st.markdown(f'''
    4. 복종수가 1개 이상인 곳들은 제외 : 복종수가 2개 이상이면 학교요청으로 지연되었을 가능성이 높음
    ''')
    
    df_true_st03_bok_1 = df_true_st03_bok[df_true_st03_bok['복종수'] == 1]

    st.dataframe(df_true_st03_bok_1)

    st.markdown(f'''
    5. 앞서 계산한 복종별 봉제업체 평균생산시간. 가장 많은 오더를 받은 봉제업체를 해당 복종의 메인업체로 가정한다.
    ''')
    df_date_rank = df_date[['시즌', '복종', '봉제업체', '오더수', '평균']].copy() # 생산일자 평균값 merge하기 위해 복사
    df_date_rank['오더수순위'] = df_date_rank.groupby(['복종'])[['오더수']].rank(method='min', ascending=False) # 오더수 순위
    df_date_rank = df_date_rank[df_date_rank['오더수순위'] == 1] # 오더수 순위 1위만
    df_date_rank = df_date_rank.drop(['시즌', '오더수', '오더수순위'], axis=1).reset_index(drop=True)
    df_date_rank.columns = ['복종', '대표생산처', '평균생산기간(일)']
    
    st.dataframe(df_date_rank.style.background_gradient())
    

    st.markdown(f'''
    6. 4번의 오더리스트에 5번의 생산시간을 더한 날짜를 예상생산일자로 가정한다.\n
    **:red[예상생산일자 = 오늘날짜 + 평균생산기간(일)]**
    ''')

    st.markdown('#### 납기일 지정')

    df_deli_list = pd.merge(df_true_st03_bok_1, df_date_rank, on='복종', how='left')
    df_deli_list = pd.merge(df_deli_list, df_true_st03[['대리점명', '학교코드', '복종', '오더', '수주량', '작지문구구분', '작지문구', '개찰일자']], on=['학교코드', '복종'], how='left')
    # df_deli_list['개찰이후경과일'] = (datetime.today() - pd.to_datetime(df_deli_list['개찰일자'])).dt.days
    df_deli_list = df_deli_list.drop(['복종수'], axis=1)
    df_deli_list['예상생산일자'] = datetime.today() + pd.to_timedelta(df_deli_list['평균생산기간(일)'], unit='d')
    df_deli_list['3월 7일 이전 출고'] = df_deli_list['예상생산일자'].apply(lambda x: 'X' if x > datetime.strptime('2023-03-07', '%Y-%m-%d') else 'O')
    # df_deli_list['차수'] = df_deli_list['오더'].str[-1]

    st.dataframe(df_deli_list)

    df_tt_cnt = df_deli_list[(df_deli_list['3월 7일 이전 출고'] == 'X') & (df_deli_list['작지문구구분'] == 'N')]
    df_tt_cnt = df_tt_cnt.drop(['작지문구구분'], axis=1)

    st.markdown(f'''
    7. **:red[주의가 필요한 오더리스트]**\n
    
    **:blue[- 복종 1개]**\n
    **:blue[- 작지문구 없음]**\n
    **:blue[- 예상일자 이후 출고]**\n
    \n
    **:red[총 오더수 : {len(df_tt_cnt)} 개]**
    ''')

    st.dataframe(df_tt_cnt)

    st.markdown('8. 복종별 수주량 합계')
    st.dataframe(df_tt_cnt.groupby(['복종'])[['수주량']].agg(sum).T)

    
    

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
