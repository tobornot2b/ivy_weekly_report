from ssl import DER_cert_to_PEM_cert
import pandas as pd

from data.mod import us7ascii_to_cp949

# SQL문 작성 함수
def make_sql(F_season: str, S_season: str, jaepum: str) -> str:
    sql_1 = f'''
    SELECT Max(s.sub_sojae_saib_gb),
        Max(To_char(s.sub_buking_cnt)),
        Rawtohex(utl_raw.Cast_to_raw(Max(s.sub_cf_ref))),
        cod_etc2,
        Max(s.sub_cf_honcolor),
        Max(S.sub_out_dt_gb),
        Max(To_char(s.sub_out_date, 'yyyy-mm-dd')),
        '0',
        Max(s.sub_cf_yn),
        Max(Decode(s.sub_remark, NULL, Decode(s.sub_cust_remark, NULL, 'N',
                                                                    'Y'),
                                    'Y')),
        Max(s.sub_prodgbn),
        s.sub_order,
        Max(s.sub_paitem),
        Max(s.sub_sojae),
        Max(s.sub_price),
        Max(s.sub_pok),
        Max(s.sub_cqty),
        Max(s.sub_qty),
        SUM(Decode(i.ipgo_bal_year
                    ||i.ipgo_bal_season, NULL, 0,
                                        i.ipgo_year
                                        ||i.ipgo_season, i.ipgo_qty,
                                        0)),
        Max(To_char(s.sub_date, 'yyyy-mm-dd')),
        Max(
        Decode(To_char(s.sub_date, 'yyyy-mm-dd'),
        To_char(s.sub_list_date, 'yyyy-mm-dd'), '',
        To_char(s.sub_list_date, 'yyyy-mm-dd'))),
        Max(To_char(s.sub_deli, 'yyyy-mm-dd')),
        Nvl(Max(To_char(s.sub_ideli, 'yyyy-mm-dd')), Min(
        To_char(i.ipgo_date, 'yyyy-mm-dd'))),
        Max(To_char(i.ipgo_date, 'yyyy-mm-dd')),
        Max(s.sub_cust),
        Rawtohex(utl_raw.Cast_to_raw(Max(tkyk_name))),
        Nvl(Max(i.ipgo_millon), 'N'),
        Max(s.sub_cnt),
        Substr(s.sub_order, 1, 3),
        s.sub_quota,
        ''
    FROM   i_sub_textile_t s,
        i_ipgo_t i,
        i_cust_v2,
        i_soje_t,
        i_cod_t
    WHERE  s.sub_millon = i.ipgo_millon(+)
        AND s.sub_sojae = soje_code(+)
        AND s.sub_paitem = cod_code(+)
        AND cod_gbn_code(+) = '36'
        AND s.sub_cust = tkyk_code(+)
        AND s.sub_quota IN ( '{F_season}', '{S_season}', '{str(int(F_season[:2])-1) + F_season[-1]}', '{str(int(S_season[:2])-1) + S_season[-1]}' )
        AND s.sub_jaepum = '{jaepum}'
    GROUP  BY cod_etc2,
            s.sub_order,
            s.sub_quota
    ORDER  BY Max(s.sub_sojae),
            s.sub_order
    '''

    sql_2 = f'''
    SELECT Max(s.sub_sojae_saib_gb),
        Max(To_char(s.sub_buking_cnt)),
        Rawtohex(utl_raw.Cast_to_raw(Max(s.sub_cf_ref))),
        cod_etc2,
        Max(s.sub_cf_honcolor),
        Max(S.sub_out_dt_gb),
        Max(To_char(s.sub_out_date, 'yyyy-mm-dd')),
        To_char(Max(subd_seq)),
        Max(s.sub_cf_yn),
        Max(Decode(s.sub_remark, NULL, Decode(s.sub_cust_remark, NULL, 'N',
                                                                    'Y'),
                                    'Y')),
        Max(s.sub_prodgbn),
        s.sub_order,
        Max(s.sub_paitem),
        Max(s.sub_sojae),
        Max(s.sub_price),
        Max(s.sub_pok),
        Max(subd_old_qty),
        Max(subd_new_qty),
        To_char(Nvl(SUM(i.ipgo_qty), 0)),
        Max(To_char(s.sub_date, 'yyyy-mm-dd')),
        Max(
        Decode(To_char(s.sub_date, 'yyyy-mm-dd'),
        To_char(s.sub_list_date, 'yyyy-mm-dd'), '',
        To_char(s.sub_list_date, 'yyyy-mm-dd'))),
        Max(To_char(subd_deli, 'yyyy-mm-dd')),
        Nvl(Max(To_char(s.sub_ideli, 'yyyy-mm-dd')), Min(
        To_char(i.ipgo_date, 'yyyy-mm-dd'))),
        Max(To_char(i.ipgo_date, 'yyyy-mm-dd')),
        Max(s.sub_cust),
        Rawtohex(utl_raw.Cast_to_raw(Max(tkyk_name))),
        Nvl(Max(i.ipgo_millon), 'N'),
        Max(s.sub_cnt),
        Substr(s.sub_order, 1, 3),
        subd_quota,
        i.ipgo_bal_quota
    FROM   i_sub_textile_t s,
        i_ipgo_t i,
        i_cust_v2,
        i_soje_t,
        i_sub_textile_det_t,
        i_cod_t
    WHERE  s.sub_millon = i.ipgo_millon
        AND subd_order = i.ipgo_millon
        AND subd_order = s.sub_millon
        AND subd_save_gb = '2'
        AND s.sub_paitem = cod_code(+)
        AND cod_gbn_code(+) = '36'
        AND s.sub_sojae = soje_code
        AND s.sub_cust = tkyk_code(+)
        AND i.ipgo_bal_quota IN ( '{F_season}', '{S_season}', '{str(int(F_season[:2])-1) + F_season[-1]}', '{str(int(S_season[:2])-1) + S_season[-1]}' )
        AND subd_quota IN ( '{F_season}', '{S_season}', '{str(int(F_season[:2])-1) + F_season[-1]}', '{str(int(S_season[:2])-1) + S_season[-1]}' )
        AND subd_quota = i.ipgo_bal_quota
        AND i.ipgo_quota <> i.ipgo_bal_quota
        AND s.sub_jaepum = '{jaepum}'
    GROUP  BY cod_etc2,
            s.sub_order,
            subd_quota,
            i.ipgo_bal_quota
    ORDER  BY Max(s.sub_sojae),
            s.sub_order
    '''

    return sql_1, sql_2


# 전처리 함수 : 데이터프레임 만들고 한글변환
def data_preprocess(df1:pd.DataFrame, df2:pd.DataFrame) -> pd.DataFrame:
    df1.columns = df2.columns = ['사입구분', 
    '완제품오더_부킹건수',
    '참조',
    '구입원단발주조회',
    '원단혼용율정보',
    '출고예정일구분',
    '업체출고예정일',
    '변경순번',
    '색상컨펌여부',
    '비고',
    '품종코드',
    '밀넘버',
    'CPC',
    '소재',
    '단가',
    '원단폭',
    '당초발주',
    '변경발주',
    '입고량',
    '최초발주',
    '최종발주',
    '납기일',
    '최초입고',
    '최종입고',
    '사입처코드',
    '사입처',
    '입고밀넘버',
    '납기변경횟수',
    '밀넘버시즌',
    '발주시즌',
    '입고시즌'
    ]

    # 한글 컬럼
    df_byte1 = df1.copy()["참조"]
    df_byte2 = df1.copy()["사입처"]
    df_byte3 = df2.copy()["참조"]
    df_byte4 = df2.copy()["사입처"]

    df1["참조"] = us7ascii_to_cp949(df_byte1)
    df1["사입처"] = us7ascii_to_cp949(df_byte2)
    df2["참조"] = us7ascii_to_cp949(df_byte3)
    df2["사입처"] = us7ascii_to_cp949(df_byte4)

    # 타입변환 (이 부분은 이 전단계에서 해도 되나 공통함수 건드리기 싫음)
    df2['당초발주'] = df2['당초발주'].astype('float')
    df2['입고량'] = df2['입고량'].astype('float')

    df = pd.concat([df1, df2])

    return df


# CPC 분류에 쓰이는 SQL문
soje_cpc_sql = f'''
SELECT cod_code,
       Rawtohex(utl_raw.Cast_to_raw(cod_name)) cod_name,
       Rawtohex(utl_raw.Cast_to_raw(cod_etc)) cod_etc
FROM   i_cod_t
WHERE  cod_gbn_code = '36'
       AND del_yn = 'Y'
ORDER  BY sort, cod_name 
'''

# 품종 분류에 쓰이는 데이터프레임 (merge용)
soje_kind = {
    '품종코드' : ['E', 'F', 'T', 'V', 'W', 'X', 'Y', 'Z'],
    '품종' : ['생활복', '체육복', '타소재', '방모', '소모', 'COAT', '편사', '기타']
}
df_soje_kind = pd.DataFrame(soje_kind) # 원단 구분


# 전처리 함수2 : 분류기준 머지, 분류용 컬럼 생성
def data_preprocess2(df1:pd.DataFrame, df2:pd.DataFrame, season: str, jaepum: str) -> pd.DataFrame:
    df_temp = df1.merge(df2, how='left', left_on='CPC', right_on='cod_code')
    df = df_temp.merge(df_soje_kind, how='left')

    df['제품'] = df['cod_etc'].str[:3]
    df['미입고량'] = df['변경발주'] - df['입고량']

    df['납기월'] = df['납기일'].str[:7]
    # df['납기월'] = df['납기일'].dt.to_period(freq = 'M')   # 연월까지

    df['업체출고예정일'] = pd.to_datetime(df['업체출고예정일'])
    df['최초발주'] = pd.to_datetime(df['최초발주'])
    df['최종발주'] = pd.to_datetime(df['최종발주'])
    df['납기일'] = pd.to_datetime(df['납기일'])
    df['최초입고'] = pd.to_datetime(df['최초입고'])
    df['최종입고'] = pd.to_datetime(df['최종입고'])
    


    # ---------- 원단 분류기준 ----------
    # 동복 학생복 기준 : 타소재, 방모, 소모(DU, [DD,DZ]), 생활복(분리)
    # 하복 학생복 기준 : 타소재, 나머지(사방, 이방 젠트라)
    # 동하복 체육복/생활복 기준 : 시보리(AZ)/티카라(AE)[시보리, 요꼬카라], 테이프/나염(AT)[테이프], 원단(나머지)

    df['구분'] = df['품종'] # 타소재, 방모, 소모, 생활복
    
    df_E = df[df['구분'] == '생활복'].copy() # 생활복 분리
    df_E.loc[(df_E['cod_name'] == '시보리') | (df_E['cod_name'] == '요꼬카라'), '구분'] = '시보리(AZ)/티카라(AE)'
    df_E.loc[(df_E['cod_name'] == '테이프'), '구분'] = '테이프/나염(AT)'
    df_E.loc[(df_E['cod_name'] != '테이프') & (df_E['cod_name'] != '시보리') & (df_E['cod_name'] != '요꼬카라'), '구분'] = '원단'
    
    df = df[df['구분'] != '생활복'].copy() # 타소재, 방모, 소모

    if (season == 'F') and (jaepum == 'H'):
        df.loc[(df['구분'] == '소모') & (df['cod_code'] == 'DU'), '구분'] = '사방 스트레치' # 소모 and DU
        df.loc[(df['구분'] == '소모') & ((df['cod_code'] == 'DZ') | (df['cod_code'] == 'DD')), '구분'] = '이방 젠트라' # 소모 and (DD or DZ)
    elif (season == 'S') and (jaepum == 'H'):
        df.loc[df['구분'] != '타소재', '구분'] = '사방/이방 젠트라' # 타소재와 나머지
    else:
        df.loc[(df['cod_name'] == '시보리') | (df['cod_name'] == '요꼬카라'), '구분'] = '시보리(AZ)/티카라(AE)'
        df.loc[(df['cod_name'] == '테이프'), '구분'] = '테이프/나염(AT)'
        df.loc[(df['cod_name'] != '테이프') & (df['cod_name'] != '시보리') & (df['cod_name'] != '요꼬카라'), '구분'] = '원단'


    # df.to_excel('abc.xlsx', index=False)
    # df_E.to_excel('abc_E.xlsx', index=False)

    return df, df_E

# 전처리 함수3 : 필요없는 항목 제거 및 조정
def data_preprocess3(df:pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={'변경발주':'발주량'})

    df_total = df.groupby(['발주시즌', '구분'])[['발주량', '입고량', '미입고량']].agg(sum)
    df_total['입고율'] = df_total['입고량'] / df_total['발주량'] * 100
    df_total = df_total.round(0).astype(int)
    df_total['입고율'] = df_total['입고율'].astype(str) + '%'

    df_total = df_total.reset_index(drop=False)

    # df_month = df.pivot_table(['발주량', '입고량', '미입고량'], index=['납기월'], columns=['구분'], aggfunc='sum') # 멀티인덱스 (컬럼도 멀티가 가능하다)
    # # df_month = df_month.stack(level=[0, 1]).reset_index().set_index('납기월')
    # df_month = df_month.stack(level=[0, 1]).reset_index()
    # df_month.columns = ['납기월', '구분', '원단종류', '원단량']
    # df_month['원단량'] = df_month['원단량'].round(0).astype(int).copy()

    return df_total

    



# 주요업무
main_text = '''
---

#### 23년 동복 원단 진행 현황 점검
    : 주간단위 소재별 과부족 현황 점검 및 추가발주
    : 가을학기 메인 원단 종결 완료
    : 신학기 원단 납기 점검

---
'''


if __name__ == "__main__":
    print('구매팀 데이터 모듈파일입니다.')
    