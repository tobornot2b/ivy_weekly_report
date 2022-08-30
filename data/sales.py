import pandas as pd
from datetime import datetime, date, timedelta


# 사이드바에서 선택된 시즌의 데이터를 가공하는 함수
def make_season_data(df: pd.DataFrame, seasons: list) -> pd.DataFrame:
    df['보고일자'] = pd.to_datetime(df['보고일자'])
    df['요일'] = df['보고일자'].dt.weekday
    df['주차'] = df['보고일자'].dt.isocalendar().week
    df['연도'] = df['보고일자'].dt.year
    df['주차_문자열'] = df['주차'].astype(str)
    df['주차_문자열'] = df['주차_문자열'].str.zfill(2)
    df['연도_문자열'] = df['연도'].astype(str)
    df['연도_주차'] = df['연도_문자열'] + df['주차_문자열']
    df['연도_주차'] = df['연도_주차'].astype(int)

    df_weekly_report = pd.DataFrame()

    for i in list(df['연도_주차'].unique()):
        df_temp = df[df['연도_주차'] == i].copy()
        df_temp2 = df_temp[df_temp['요일'] == df_temp['요일'].min()]
        df_weekly_report = pd.concat([df_weekly_report, df_temp2])

    df_last_season = df_weekly_report[df_weekly_report['시즌'] == seasons[0]]
    df_last_season = df_last_season[['상권', '수주량', '해제량', '보고일자', '시즌', '주차']]
    df_last_season['보고일자'] = df_last_season['보고일자'] + pd.DateOffset(years=1) # x축 맞추기 위해 1년 추가

    df_this_season = df_weekly_report[df_weekly_report['시즌'] == seasons[1]]
    df_this_season = df_this_season[['상권', '수주량', '해제량', '보고일자', '시즌', '주차']]

    df_2seasons = pd.concat([df_last_season, df_this_season])
    df_2seasons = df_2seasons.set_index('보고일자')

    return df_2seasons

# 각종 변수 만들기
def make_arg(df: pd.DataFrame) -> int:
    # 최종 주차
    week = df['주차'][-1]

    # 금주 수주량 합계
    week_suju_sum = df.groupby(['시즌', '보고일자'])[['수주량']].agg(sum)['수주량'][-1]

    # 금주 해제량 합계
    week_haje_sum = df.groupby(['시즌', '보고일자'])[['해제량']].agg(sum)['해제량'][-1]

    # 전주 수주량 합계
    j_week_suju_sum = df.groupby(['시즌', '보고일자'])[['수주량']].agg(sum)['수주량'][-2]

    # 전주 해제량 합계
    j_week_haje_sum = df.groupby(['시즌', '보고일자'])[['해제량']].agg(sum)['해제량'][-2]
    
    # 금주 수주변동량
    week_suju_qty = (df.groupby(['시즌', '보고일자'])[['수주량']].agg(sum)['수주량'][-1]) -\
        (df.groupby(['시즌', '보고일자'])[['수주량']].agg(sum)['수주량'][-2])
    
    # 금주 해제변동량
    week_haje_qty = (df.groupby(['시즌', '보고일자'])[['해제량']].agg(sum)['해제량'][-1]) -\
        (df.groupby(['시즌', '보고일자'])[['해제량']].agg(sum)['해제량'][-2])

    # 전주 수주변동량
    j_week_suju_qty = (df.groupby(['시즌', '보고일자'])[['수주량']].agg(sum)['수주량'][-2]) -\
        (df.groupby(['시즌', '보고일자'])[['수주량']].agg(sum)['수주량'][-3])
    
    # 전주 해제변동량
    j_week_haje_qty = (df.groupby(['시즌', '보고일자'])[['해제량']].agg(sum)['해제량'][-2]) -\
        (df.groupby(['시즌', '보고일자'])[['해제량']].agg(sum)['해제량'][-3])

    return week, week_suju_sum, week_haje_sum, j_week_suju_sum, j_week_haje_sum, week_suju_qty, week_haje_qty, j_week_suju_qty, j_week_haje_qty


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


# ---------- 낙찰현황 관련 ----------

def make_sql(season1: str, date: str) -> str:
    date = datetime.strftime(date, '%Y%m%d')

    sql = f'''
    SELECT z.tkyk,
        Rawtohex(utl_raw.Cast_to_raw(tkyk_name)) tkyk_name,
        sort,
        SUM(z.i_cnt)       i_cnt,
        SUM(z.e_cnt)       e_cnt,
        SUM(z.s_cnt)       s_cnt,
        SUM(z.l_cnt)       l_cnt,
        SUM(z.etc_cnt)     etc_cnt,
        SUM(z.i_qty)       i_qty,
        SUM(z.e_qty)       e_qty,
        SUM(z.s_qty)       s_qty,
        SUM(z.l_qty)       l_qty,
        SUM(z.etc_qty)     etc_qty,
        SUM(z.j_i_cnt)     j_i_cnt,
        SUM(z.j_e_cnt)     j_e_cnt,
        SUM(z.j_s_cnt)     j_s_cnt,
        SUM(z.j_l_cnt)     j_l_cnt,
        SUM(z.j_etc_cnt)   j_etc_cnt,
        SUM(z.j_i_qty)     j_i_qty,
        SUM(z.j_e_qty)     j_e_qty,
        SUM(z.j_s_qty)     j_s_qty,
        SUM(z.j_l_qty)     j_l_qty,
        SUM(z.j_etc_qty)   j_etc_qty,
        SUM(z.j_i_cnt_tot) j_i_cnt_tot,
        SUM(z.j_i_qty_tot) j_i_qty_tot
    FROM   (SELECT a.g2b_tkyk                   tkyk,
                Decode(a.g2b_co_gb, 'I', 1,
                                    0)       i_cnt,
                Decode(a.g2b_co_gb, 'E', 1,
                                    0)       e_cnt,
                Decode(a.g2b_co_gb, 'S', 1,
                                    0)       s_cnt,
                Decode(a.g2b_co_gb, 'L', 1,
                                    0)       l_cnt,
                Decode(a.g2b_co_gb, 'I', 0,
                                    'E', 0,
                                    'S', 0,
                                    'L', 0,
                                    1)       etc_cnt,
                Decode(a.g2b_co_gb, 'I', g2b_qty,
                                    0)       i_qty,
                Decode(a.g2b_co_gb, 'E', g2b_qty,
                                    0)       e_qty,
                Decode(a.g2b_co_gb, 'S', g2b_qty,
                                    0)       s_qty,
                Decode(a.g2b_co_gb, 'L', g2b_qty,
                                    0)       l_qty,
                Decode(a.g2b_co_gb, 'I', 0,
                                    'E', 0,
                                    'S', 0,
                                    'L', 0,
                                    g2b_qty) etc_qty,
                0                            j_i_cnt,
                0                            j_e_cnt,
                0                            j_s_cnt,
                0                            j_l_cnt,
                0                            j_etc_cnt,
                0                            j_i_qty,
                0                            j_e_qty,
                0                            j_s_qty,
                0                            j_l_qty,
                0                            j_etc_qty,
                0                            j_i_cnt_tot,
                0                            j_i_qty_tot
            FROM   i_sale_g2b_t a,
                i_sch_com_t
            WHERE  schc_code (+) = a.g2b_school
                AND a.g2b_end_gb = '9'
                AND a.g2b_date <= To_date('{date}', 'yyyymmdd')
                AND ( a.g2b_quota1 IN ( '{season1}', '{season1}' )
                        OR a.g2b_quota2 IN ( '{season1}', '{season1}' ) )
            UNION ALL
            SELECT a.g2b_tkyk tkyk,
                0          i_cnt,
                0          e_cnt,
                0          s_cnt,
                0          l_cnt,
                0          etc_cnt,
                0          i_qty,
                0          e_qty,
                0          s_qty,
                0          l_qty,
                0          etc_qty,
                CASE
                    WHEN a.g2b_date <= To_date('{str(int(date[:4])-1)+date[4:]}', 'yyyymmdd') THEN
                    Decode(a.g2b_co_gb, 'I', 1,
                                        0)
                    ELSE 0
                END        j_i_cnt,
                CASE
                    WHEN a.g2b_date <= To_date('{str(int(date[:4])-1)+date[4:]}', 'yyyymmdd') THEN
                    Decode(a.g2b_co_gb, 'E', 1,
                                        0)
                    ELSE 0
                END        j_e_cnt,
                CASE
                    WHEN a.g2b_date <= To_date('{str(int(date[:4])-1)+date[4:]}', 'yyyymmdd') THEN
                    Decode(a.g2b_co_gb, 'S', 1,
                                        0)
                    ELSE 0
                END        j_s_cnt,
                CASE
                    WHEN a.g2b_date <= To_date('{str(int(date[:4])-1)+date[4:]}', 'yyyymmdd') THEN
                    Decode(a.g2b_co_gb, 'L', 1,
                                        0)
                    ELSE 0
                END        j_l_cnt,
                CASE
                    WHEN a.g2b_date <= To_date('{str(int(date[:4])-1)+date[4:]}', 'yyyymmdd') THEN
                    Decode(a.g2b_co_gb, 'I', 0,
                                        'E', 0,
                                        'S', 0,
                                        'L', 0,
                                        1)
                    ELSE 0
                END        j_etc_cnt,
                CASE
                    WHEN a.g2b_date <= To_date('{str(int(date[:4])-1)+date[4:]}', 'yyyymmdd') THEN
                    Decode(a.g2b_co_gb, 'I', g2b_qty,
                                        0)
                    ELSE 0
                END        j_i_qty,
                CASE
                    WHEN a.g2b_date <= To_date('{str(int(date[:4])-1)+date[4:]}', 'yyyymmdd') THEN
                    Decode(a.g2b_co_gb, 'E', g2b_qty,
                                        0)
                    ELSE 0
                END        j_e_qty,
                CASE
                    WHEN a.g2b_date <= To_date('{str(int(date[:4])-1)+date[4:]}', 'yyyymmdd') THEN
                    Decode(a.g2b_co_gb, 'S', g2b_qty,
                                        0)
                    ELSE 0
                END        j_s_qty,
                CASE
                    WHEN a.g2b_date <= To_date('{str(int(date[:4])-1)+date[4:]}', 'yyyymmdd') THEN
                    Decode(a.g2b_co_gb, 'L', g2b_qty,
                                        0)
                    ELSE 0
                END        j_l_qty,
                CASE
                    WHEN a.g2b_date <= To_date('{str(int(date[:4])-1)+date[4:]}', 'yyyymmdd') THEN
                    Decode(a.g2b_co_gb, 'I', 0,
                                        'E', 0,
                                        'S', 0,
                                        'L', 0,
                                        g2b_qty)
                    ELSE 0
                END        j_etc_qty,
                1          j_i_cnt_tot,
                a.g2b_qty  j_i_qty_tot
            FROM   i_sale_g2b_t a,
                i_sch_com_t
            WHERE  schc_code (+) = a.g2b_school
                AND a.g2b_end_gb = '9'
                AND ( a.g2b_quota1 IN ( '{str(int(season1[:2])-1)+season1[-1]}', '{str(int(season1[:2])-1)+season1[-1]}' )
                        OR a.g2b_quota2 IN ( '{str(int(season1[:2])-1)+season1[-1]}', '{str(int(season1[:2])-1)+season1[-1]}' ) )) z,
        i_tkyk_t
    WHERE  z.tkyk = tkyk_code
    GROUP  BY z.tkyk,
            tkyk_name,
            sort
    '''

    return sql


# 
def make_bid_data(df :pd.DataFrame, season: str) -> pd.DataFrame:
    df.columns = ['특약코드',
    '특약명',
    'sort',
    '아이비_학교수',
    '엘리트_학교수',
    '스마트_학교수',
    '스쿨룩스_학교수',
    '일반업체 학교수',
    '아이비_학생수',
    '엘리트_학생수',
    '스마트_학생수',
    '스쿨룩스_학생수',
    '일반업체_학생수',
    '지난해_아이비_학교수',
    '지난해_엘리트_학교수',
    '지난해_스마트_학교수',
    '지난해_스쿨룩스_학교수',
    '지난해_일반업체 학교수',
    '지난해_아이비_학생수',
    '지난해_엘리트_학생수',
    '지난해_스마트_학생수',
    '지난해_스쿨룩스_학생수',
    '지난해_일반업체_학생수',
    '전년최종_아이비_학교수',
    '전년최종_아이비_학생수'
    ]

    df1 = df[['특약명', '아이비_학생수', '스마트_학생수', '엘리트_학생수', '스쿨룩스_학생수', '일반업체_학생수']].copy()
    df1['시즌'] = season
    df1.columns = ['특약명', '아이비클럽', '스마트', '엘리트', '스쿨룩스', '일반업체', '시즌']

    df1_j = df[['특약명', '지난해_아이비_학생수', '지난해_스마트_학생수', '지난해_엘리트_학생수', '지난해_스쿨룩스_학생수', '지난해_일반업체_학생수']].copy()
    df1_j['시즌'] = str(int(season[:2])-1) + season[-1]
    df1_j.columns = ['특약명', '아이비클럽', '스마트', '엘리트', '스쿨룩스', '일반업체', '시즌']

    df_bid_graph = pd.concat([df1, df1_j])
    df_bid_graph = df_bid_graph[['시즌', '특약명', '아이비클럽', '스마트', '엘리트', '스쿨룩스', '일반업체']]
    
    df_bid = df_bid_graph.copy()
    df_bid = df_bid.groupby(['시즌'])[['아이비클럽', '스마트', '엘리트', '스쿨룩스', '일반업체']].agg(sum).copy()
    
    df_bid_graph = df_bid_graph.melt(id_vars=['시즌', '특약명'], var_name='업체구분', value_name='학생수')

    return df_bid, df_bid_graph


# 인자1: 이번주 데이터, 인자2: 전주 데이터, 인자3: 선택한 시즌
def make_bid_data2(df :pd.DataFrame, df_j :pd.DataFrame, seasons: list) -> pd.DataFrame:
    df_last_week_diff = df - df_j
    df_last_week_diff.index = ['1', '증감(전주대비)']

    df.loc['증감(전년대비)'] = df.loc[max(seasons)] - df.loc[min(seasons)].copy()

    df = pd.concat([df, df_last_week_diff])
    df = df.drop(index='1')

    df['합계'] = df.sum(axis=1)

    df['sort'] = [3, 1, 4, 2]
    df = df.sort_values('sort').drop('sort', axis=1)

    return df


def make_bid_data3(df: pd.DataFrame) -> int:
    pass


# 주요업무
main_text = '''
---

### 5. 주요업무
    
    - 22F 가을학기 수주 마감 (08/30)

    - 23N/S 주관구매 낙찰학교 1차분 수주 진행

    - 굿네이버스 기부작업 진행 (08/29 ~ 09/07)

---
'''


if __name__ == "__main__":
    print('영업팀 데이터 모듈파일입니다.')
    