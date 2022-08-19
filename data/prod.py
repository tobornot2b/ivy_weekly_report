import pandas as pd

# 생산팀 SQL문
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
    df_prod_report['본사진행'] = df_prod_report['ST05'] + df_prod_report['ST10'] + df_prod_report['ST11'] + df_prod_report['ST12'] + df_prod_report['ST13'] + df_prod_report['ST14'] + df_prod_report['ST15']
    df_prod_report['원단'] = df_prod_report['ST20']
    df_prod_report['생산타입'] = df_prod_report['ST50'] + df_prod_report['ST55'] + df_prod_report['ST60']
    df_prod_report['생산완료'] = df_prod_report['ST60']
    df_prod_report['출고율'] = df_prod_report['생산완료'] / df_prod_report['생산타입']
    # df_prod_report['출고율(%)'] = (df_prod_report['출고율'] * 100).astype(str)
    # df_prod_report['출고율(%)'] = df_prod_report['출고율(%)'].str.split('.')

    df_prod_report2 = df_prod_report[['성별', '복종', '홀드', '본사진행', '원단', '생산타입', '생산완료', '출고율']]

    return df_prod_report2


# 생산진행 관련
main_text = '''
---

### 생산진행 관련
    : 상권별 동복 수주 입력 및 홀드 해제 독려 요청
    : 동복 정기 타입 진행

---
'''


if __name__ == "__main__":
    print('생산팀 데이터 모듈파일입니다.')
    