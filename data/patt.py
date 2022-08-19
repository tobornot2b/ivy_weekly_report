import pandas as pd

# 패턴팀 SQL문
def make_sql(season1: str, season2: str, jaepum: str) -> str:
    sql = f'''
    SELECT '{season1}/{season2}'           season,
        '1'                                gubun,
        Decode('Y', 'Y', Substr(cod_etc, 1, 1),
                    a.master_bokjong)       master_bokjong,
        Max(sort) sort,
        Rawtohex(utl_raw.Cast_to_raw(c.cust_name)) cust_name,
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
        Rawtohex(utl_raw.Cast_to_raw(c.cust_name)) cust_name,
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
def data_preprocess(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = ['시즌', '구분', '복종', '정렬', '봉제업체', '타입건수', '지시량', '작업건수', '작업량']
    df['작업율'] = df['작업량'] / df['지시량']
    df['작업율(%)'] = round((df['작업량'] / df['지시량']) * 100, 1) # 소숫점 1자리까지
    df['작업율(%)'] = df['작업율(%)'].astype(str)
    df['작업율(%)'] = df['작업율(%)'] + '%'
    df['구분'] = df['구분'].str.replace('1', '남').replace('2', '여')
    df = df.sort_values(['구분', '복종', '봉제업체']).reset_index(drop=True)
    df = df.drop('정렬', axis=1)

    df_M = df[df['구분'] == '남'].reset_index(drop=True)
    df_F = df[df['구분'] == '여'].reset_index(drop=True)

    return df_M, df_F


# 특이사항
main_text = '''
---

### 특이사항
    - 22F/23N 동복 타입분 메인 패턴 출고
    - 23N 동복 타입분 샘플 패턴 출고
    - 23S 하복 타입분 메인 패턴 출고

---
'''

if __name__ == "__main__":
    print('패턴팀 데이터 모듈파일입니다.')
    