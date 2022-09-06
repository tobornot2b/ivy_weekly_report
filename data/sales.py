import pandas as pd
from datetime import datetime, date, timedelta

from data import mod


# 주요업무
main_text = '''
---

### 주요업무
    
    - 22F 가을학기 수주 마감 (08/30)

    - 23N/S 악세사리 추가수주 진행 (~09/08)

    - 23N/S 주관구매 낙찰학교 1차분 수주 진행

---
'''

# 연간계획 (변경되면 입력해줘야 함)
year_plan: list = [38000, 49000, 26000, 21000, 23000, 28000]


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


# ---------- 수주/해제 관련 ----------

def make_sql_suju(bok: str, season: list, date: str) -> str:
    date = datetime.strftime(date, '%Y%m%d')

    if bok == 'J':
        jaepum = 'H' # 학생복
    elif bok == 'H':
        jaepum = 'F' # 체육복
    elif bok == '*':
        jaepum = 'H' # 학생복

    # 일단 고정변수    
    q1 = q2 = q3 = max(season)
    dt_gb = '1' # 날짜구분 1: 수주일, 2: 확정일, 3: 타입일, 4: 생산일
    
    bok2 = 'S' # 상하의
    if bok == '*':
        bok2 = 'H' # 상하의

    sel_gb = '1' # 이력 1: 정산분, 2: 삭제캔슬포함

    sql1 = f'''
    select  z.tkyk        agen_tkyk
        ,sort
        ,bok_sort
        ,z.school_cd   sch_gb
        ,z.sch_count
        ,z.suju_qty
        ,z.h_qty
        ,z.prod_qty
        ,z.j_sch_count
        ,z.j_suju_qty
        ,z.j_h_qty
        ,z.j_tot_qty
        ,z.j_prod_qty
    from (select    t.tkyk             tkyk
                    ,t.sch_gb           school_cd
                ,max(t.bok_sort)    bok_sort
                ,sum(t.sch_count)   sch_count
                ,sum(t.suju_qty)    suju_qty 
                ,sum(t.h_qty)       h_qty
                ,sum(t.prod_qty)    prod_qty
                ,sum(t.j_sch_count) j_sch_count
                ,sum(t.j_suju_qty)  j_suju_qty 
                ,sum(t.j_h_qty)     j_h_qty
                ,sum(t.j_tot_qty)   j_tot_qty
                ,sum(t.j_prod_qty)  j_prod_qty
        from (
            select  '기준시즌 수주.홀드량' msg
                    ,master_tkyk            tkyk
                    ,decode(MASTER_BOKJONG,'R','S','Q','P','Z','D',MASTER_BOKJONG) sch_gb
                    ,sort   bok_sort
                    ,0 sch_count
                    ,master_suju_qty suju_qty
                    ,decode(master_appv_end_gb,'Y' ,(case when master_appv_end_dt <= TO_DATE('{date}','YYYYMMDD') then master_suju_qty else 0 end),0) h_qty
                    ,(case when master_prodm_date <= TO_DATE('{date}','YYYYMMDD') and master_prodm_qty > 0  then master_suju_qty else 0 end) prod_qty
                    ,0 j_sch_count
                    ,0 j_suju_qty
                    ,0 j_h_qty
                    ,0 j_tot_qty
                    ,0 j_prod_qty
                FROM i_suju_master_t,I_SUJU_FACT_T,I_COD_T
                    where MASTER_BOKJONG = COD_CODE
                and COD_GBN_CODE   = '01'
                and MASTER_ORDER   = FACT_ORDER(+)
                and MASTER_REMAKE  IN ('M','C')
                and MASTER_JAEPUM  = '{jaepum}'
                and master_tkyk    in ('C','D','H','I','L','R')
                and MASTER_QUOTA   in ('{q1}','{q2}','{q3}')
                and decode('{dt_gb}','1', MASTER_SUJU_DATE,'2', MASTER_APPV_END_DT,'3', FACT_DATE,'4', MASTER_PRODM_DATE) <= TO_DATE('{date}','YYYYMMDD')
                and ('*' = '{bok}'  OR MASTER_BOKJONG     = '{bok}')
                and ('*' = '{bok2}' OR ( nvl(COD_ETC2,'') = '{bok2}' and (    (substr('{q1}',3,1)  = 'S' and nvl(COD_ETC3,'') IN ('S','T'))
                                                                                    or (substr('{q1}',3,1) <> 'S' and nvl(COD_ETC3,'') IN ('F','T'))
                                                                                )
                                            ) 
                    )
                and ( ('{sel_gb}' = '1' and MASTER_STATUS <> '00') or ('{sel_gb}' = '2' and (MASTER_STATUS <> '00' or (MASTER_STATUS = '00' and to_char(MASTER_ST00_DT,'YYYYMMDD') >= '{date}')))
                    )
            UNION ALL
            select  '기준시즌 수주.홀드량 삭제건' msg
                    ,master_tkyk        tkyk
                    ,decode(MASTER_BOKJONG,'R','S','Q','P','Z','D',MASTER_BOKJONG) sch_gb
                    ,sort   bok_sort
                    ,0 sch_count
                    ,master_suju_qty suju_qty
                    ,decode(master_appv_end_gb,'Y' ,(case when master_appv_end_dt <= TO_DATE('{date}','YYYYMMDD') then master_suju_qty else 0 end),0) h_qty
                    ,(case when master_prodm_date <= TO_DATE('{date}','YYYYMMDD') and master_prodm_qty > 0  then master_suju_qty else 0 end) prod_qty
                    ,0 j_sch_count
                    ,0 j_suju_qty
                    ,0 j_h_qty
                    ,0 j_tot_qty
                    ,0 j_prod_qty
                FROM I_SUJU_MASTER_DELETE_T,I_COD_T
                    where MASTER_BOKJONG = COD_CODE
                and COD_GBN_CODE   = '01'
                and MASTER_REMAKE  IN ('M','C')
                and MASTER_JAEPUM  = '{jaepum}'
                and master_tkyk    in ('C','D','H','I','L','R')
                and MASTER_QUOTA   in ('{q1}','{q2}','{q3}')
                and decode('{dt_gb}','1', MASTER_SUJU_DATE,'2', MASTER_APPV_END_DT) <= TO_DATE('{date}','YYYYMMDD')
                and to_char(MASTER_DELETE_DT,'YYYYMMDD') >= '{date}'
                and ('*' = '{bok}'  OR MASTER_BOKJONG     = '{bok}')
                and ('*' = '{bok2}' OR ( nvl(COD_ETC2,'') = '{bok2}' and (    (substr('{q1}',3,1)  = 'S' and nvl(COD_ETC3,'') IN ('S','T'))
                                                                                    or (substr('{q1}',3,1) <> 'S' and nvl(COD_ETC3,'') IN ('F','T'))
                                                                                )
                                            ) 
                    )
                and '{dt_gb}' in ('1','2')
                and '{sel_gb}' = '2'

            
            union all
            select  '기준 전시즌 수주.홀드량' msg
                    ,master_tkyk        tkyk
                    ,decode(MASTER_BOKJONG,'R','S','Q','P','Z','D',MASTER_BOKJONG) sch_gb
                    ,sort   bok_sort
                    ,0 sch_count
                    ,0 suju_qty
                    ,0 h_qty
                    ,0 prod_qty
                    ,0 j_sch_count
                    ,master_suju_qty j_suju_qty
                    ,decode(master_appv_end_gb,'Y' ,(case when master_appv_end_dt <= TO_DATE('{str(int(date[:4])-1)+date[4:]}','YYYYMMDD') then master_suju_qty else 0 end),0) j_h_qty
                    ,0 j_tot_qty
                    ,(case when master_prodm_date <= TO_DATE('{str(int(date[:4])-1)+date[4:]}','YYYYMMDD') and master_prodm_qty > 0  then master_suju_qty else 0 end) j_prod_qty
                FROM i_suju_master_t,I_SUJU_FACT_T,I_COD_T
                    where MASTER_BOKJONG = COD_CODE
                and COD_GBN_CODE   = '01'
                and MASTER_ORDER   = FACT_ORDER(+)
                and MASTER_REMAKE  IN ('M','C')
                and MASTER_JAEPUM  = '{jaepum}'
                and master_tkyk    in ('C','D','H','I','L','R')
                and MASTER_QUOTA   in ('{str(int(q1[:2])-1)+q1[-1]}','{str(int(q2[:2])-1)+q2[-1]}','{str(int(q3[:2])-1)+q3[-1]}')
                and decode('{dt_gb}','1', MASTER_SUJU_DATE,'2', MASTER_APPV_END_DT,'3', FACT_DATE,'4', MASTER_PRODM_DATE) <= TO_DATE('{str(int(date[:4])-1)+date[4:]}','YYYYMMDD')
                and ('*' = '{bok}'  OR MASTER_BOKJONG   = '{bok}')
                and ('*' = '{bok2}' OR ( nvl(COD_ETC2,'') = '{bok2}' and (    (substr('{str(int(q1[:2])-1)+q1[-1]}',3,1)  = 'S' and nvl(COD_ETC3,'') IN ('S','T'))
                                                                                    or (substr('{str(int(q1[:2])-1)+q1[-1]}',3,1) <> 'S' and nvl(COD_ETC3,'') IN ('F','T'))
                                                                                )
                                            ) 
                    )
                and ( ('{sel_gb}' = '1' and MASTER_STATUS <> '00') or ('{sel_gb}' = '2' and (MASTER_STATUS <> '00' or (MASTER_STATUS = '00' and to_char(MASTER_ST00_DT,'YYYYMMDD') >= '{str(int(date[:4])-1)+date[4:]}')))
                    )
            union all
            select  '기준 전시즌 수주.홀드량 삭제건' msg
                    ,master_tkyk        tkyk
                    ,decode(MASTER_BOKJONG,'R','S','Q','P','Z','D',MASTER_BOKJONG) sch_gb
                    ,sort   bok_sort
                    ,0 sch_count
                    ,0 suju_qty
                    ,0 h_qty
                    ,0 prod_qty
                    ,0 j_sch_count
                    ,master_suju_qty j_suju_qty
                    ,decode(master_appv_end_gb,'Y' ,(case when master_appv_end_dt <= TO_DATE('{str(int(date[:4])-1)+date[4:]}','YYYYMMDD') then master_suju_qty else 0 end),0) j_h_qty
                    ,0 j_tot_qty
                    ,(case when master_prodm_date <= TO_DATE('{str(int(date[:4])-1)+date[4:]}','YYYYMMDD') and master_prodm_qty > 0  then master_suju_qty else 0 end) j_prod_qty
                FROM I_SUJU_MASTER_DELETE_T,I_COD_T
                    where MASTER_BOKJONG = COD_CODE
                and COD_GBN_CODE   = '01'
                and MASTER_REMAKE  IN ('M','C')
                and MASTER_JAEPUM  = '{jaepum}'
                and master_tkyk    in ('C','D','H','I','L','R')
                and MASTER_QUOTA   in ('{str(int(q1[:2])-1)+q1[-1]}','{str(int(q2[:2])-1)+q2[-1]}','{str(int(q3[:2])-1)+q3[-1]}')
                and decode('{dt_gb}','1', MASTER_SUJU_DATE,'2', MASTER_APPV_END_DT) <= TO_DATE('{str(int(date[:4])-1)+date[4:]}','YYYYMMDD')
                and to_char(MASTER_DELETE_DT,'YYYYMMDD') >= '{str(int(date[:4])-1)+date[4:]}'
                and ('*' = '{bok}'  OR MASTER_BOKJONG     = '{bok}')
                and ('*' = '{bok2}' OR ( nvl(COD_ETC2,'') = '{bok2}' and (    (substr('{str(int(q1[:2])-1)+q1[-1]}',3,1)  = 'S' and nvl(COD_ETC3,'') IN ('S','T'))
                                                                                    or (substr('{str(int(q1[:2])-1)+q1[-1]}',3,1) <> 'S' and nvl(COD_ETC3,'') IN ('F','T'))
                                                                                )
                                            ) 
                    )
                and '{dt_gb}' in ('1','2')
                and '{sel_gb}' = '2'
            union all



            select  '기준 전시즌 최종 수주량' msg
                    ,master_tkyk        tkyk
                    ,decode(MASTER_BOKJONG,'R','S','Q','P','Z','D',MASTER_BOKJONG) sch_gb
                    ,sort   bok_sort
                    ,0 sch_count
                    ,0 suju_qty
                    ,0 h_qty
                    ,0 prod_qty
                    ,0 j_sch_count
                    ,0 j_suju_qty
                    ,0 j_h_qty
                    ,master_suju_qty j_tot_qty 
                    ,0 j_prod_qty
                FROM i_suju_master_t,I_COD_T
                    where MASTER_BOKJONG = COD_CODE
                and COD_GBN_CODE   = '01'
                and MASTER_REMAKE  IN ('M','C')
                and MASTER_JAEPUM  = '{jaepum}'
                and master_tkyk    in ('C','D','H','I','L','R')
                and MASTER_QUOTA   in ('{str(int(q1[:2])-1)+q1[-1]}','{str(int(q2[:2])-1)+q2[-1]}','{str(int(q3[:2])-1)+q3[-1]}')
                and master_status  = '60'
                and ('*' = '{bok}'  OR MASTER_BOKJONG     = '{bok}')
                and ('*' = '{bok2}' OR ( nvl(COD_ETC2,'') = '{bok2}' and (    (substr('{str(int(q1[:2])-1)+q1[-1]}',3,1)  = 'S' and nvl(COD_ETC3,'') IN ('S','T'))
                                                                                    or (substr('{str(int(q1[:2])-1)+q1[-1]}',3,1) <> 'S' and nvl(COD_ETC3,'') IN ('F','T'))
                                                                                )
                                            ) 
                    )

                ) t
    group by t.tkyk,t.sch_gb
    ) z,i_tkyk_t
    where z.tkyk = tkyk_code
    ORDER BY sort
    '''

    sql2 = f'''
    select  z.tkyk        agen_tkyk                      
        ,sort                                         
        ,bok_sort                                     
        ,z.school_cd   sch_gb                         
        ,z.sch_count                                  
        ,z.suju_qty                                   
        ,z.h_qty                                      
        ,z.prod_qty                                   
        ,z.j_sch_count                                
        ,z.j_suju_qty                                 
        ,z.j_h_qty                                    
        ,z.j_tot_qty                                  
        ,z.j_prod_qty                                 
    from (select    t.tkyk             tkyk              
                    ,t.sch_gb           school_cd          
                ,max(t.bok_sort)    bok_sort          
                ,sum(t.sch_count)   sch_count         
                ,sum(t.suju_qty)    suju_qty          
                ,sum(t.h_qty)       h_qty             
                ,sum(t.prod_qty)    prod_qty          
                ,sum(t.j_sch_count) j_sch_count       
                ,sum(t.j_suju_qty)  j_suju_qty        
                ,sum(t.j_h_qty)     j_h_qty           
                ,sum(t.j_tot_qty)   j_tot_qty         
                ,sum(t.j_prod_qty)  j_prod_qty        
        from (                                        
            select  '기준시즌 수주.홀드량' msg        
                    ,master_tkyk            tkyk       
                    ,decode(MASTER_BOKJONG,'R','S','Q','P','Z','D',MASTER_BOKJONG) sch_gb  
                    ,sort   bok_sort                   
                    ,0 sch_count                       
                    ,master_suju_qty suju_qty          
                    ,decode(master_appv_end_gb,'Y' ,(case when master_appv_end_dt <= TO_DATE('{date}','YYYYMMDD') then master_suju_qty else 0 end),0) h_qty  
                    ,(case when master_prodm_date <= TO_DATE('{date}','YYYYMMDD') and master_prodm_qty > 0  then master_suju_qty else 0 end) prod_qty  
                    ,0 j_sch_count                     
                    ,0 j_suju_qty                      
                    ,0 j_h_qty                         
                    ,0 j_tot_qty                       
                    ,0 j_prod_qty                      
                FROM i_suju_master_t,I_SUJU_FACT_T,I_COD_T,I_SCH_T                        
                where MASTER_BOKJONG = COD_CODE                                                  
                and cod_gbn_code    = '01'                                                 
                and sch_f_bokjong   = cod_code                                             
                and master_school  = sch_code                                              
                and MASTER_ORDER   = FACT_ORDER(+)                                         
                and MASTER_REMAKE  IN ('M','C')                                            
                and MASTER_JAEPUM  = '{jaepum}'                                            
                and master_tkyk    in ('C','D','H','I','L','R')                            
                and MASTER_QUOTA   in ('{q1}','{q2}','{q3}')                               
                and decode('{dt_gb}','1', MASTER_SUJU_DATE,'2', MASTER_APPV_END_DT,'3', FACT_DATE,'4', MASTER_PRODM_DATE) <= TO_DATE('{date}','YYYYMMDD')  
                and ('*' = '{bok}'  OR MASTER_BOKJONG     = '{bok}')  
                and ('*' = '{bok2}' OR ( nvl(COD_ETC2,'') = '{bok2}' and (    (substr('{q1}',3,1)  = 'S' and nvl(COD_ETC3,'') IN ('S','T'))  
                                                                                    or (substr('{q1}',3,1) <> 'S' and nvl(COD_ETC3,'') IN ('F','T'))  
                                                                                )  
                                            )   
                    )  
                and ( ('{sel_gb}' = '1' and MASTER_STATUS <> '00') or ('{sel_gb}' = '2' and (MASTER_STATUS <> '00' or (MASTER_STATUS = '00' and to_char(MASTER_ST00_DT,'YYYYMMDD') >= '{date}')))  
                    )  
            UNION ALL  
            select  '기준시즌 수주.홀드량 삭제건' msg  
                    ,master_tkyk        tkyk  
                    ,decode(MASTER_BOKJONG,'R','S','Q','P','Z','D',MASTER_BOKJONG) sch_gb  
                    ,sort   bok_sort  
                    ,0 sch_count  
                    ,master_suju_qty suju_qty  
                    ,decode(master_appv_end_gb,'Y' ,(case when master_appv_end_dt <= TO_DATE('{date}','YYYYMMDD') then master_suju_qty else 0 end),0) h_qty  
                    ,(case when master_prodm_date <= TO_DATE('{date}','YYYYMMDD') and master_prodm_qty > 0  then master_suju_qty else 0 end) prod_qty  
                    ,0 j_sch_count  
                    ,0 j_suju_qty  
                    ,0 j_h_qty  
                    ,0 j_tot_qty  
                    ,0 j_prod_qty  
                FROM I_SUJU_MASTER_DELETE_T,I_COD_T,I_SCH_T  
                where MASTER_BOKJONG = COD_CODE                     
                and cod_gbn_code    = '01'                    
                and sch_f_bokjong   = cod_code                
                and master_school  = sch_code                 
                and MASTER_REMAKE  IN ('M','C')               
                and MASTER_JAEPUM  = '{jaepum}'               
                and master_tkyk    in ('C','D','H','I','L','R')  
                and MASTER_QUOTA   in ('{q1}','{q2}','{q3}')  
                and decode('{dt_gb}','1', MASTER_SUJU_DATE,'2', MASTER_APPV_END_DT) <= TO_DATE('{date}','YYYYMMDD')  
                and to_char(MASTER_DELETE_DT,'YYYYMMDD') >= '{date}'  
                and ('*' = '{bok}'  OR MASTER_BOKJONG     = '{bok}')  
                and ('*' = '{bok2}' OR ( nvl(COD_ETC2,'') = '{bok2}' and (    (substr('{q1}',3,1)  = 'S' and nvl(COD_ETC3,'') IN ('S','T'))  
                                                                                    or (substr('{q1}',3,1) <> 'S' and nvl(COD_ETC3,'') IN ('F','T'))  
                                                                                )  
                                            )   
                    )  
                and '{dt_gb}' in ('1','2')  
                and '{sel_gb}' = '2'  
            union all  
            select  '기준 전시즌 수주.홀드량' msg  
                    ,master_tkyk        tkyk  
                    ,decode(MASTER_BOKJONG,'R','S','Q','P','Z','D',MASTER_BOKJONG) sch_gb  
                    ,sort   bok_sort  
                    ,0 sch_count  
                    ,0 suju_qty  
                    ,0 h_qty  
                    ,0 prod_qty  
                    ,0 j_sch_count  
                    ,master_suju_qty j_suju_qty  
                    ,decode(master_appv_end_gb,'Y' ,(case when master_appv_end_dt <= TO_DATE('{str(int(date[:4])-1)+date[4:]}','YYYYMMDD') then master_suju_qty else 0 end),0) j_h_qty  
                    ,0 j_tot_qty  
                    ,(case when master_prodm_date <= TO_DATE('{str(int(date[:4])-1)+date[4:]}','YYYYMMDD') and master_prodm_qty > 0  then master_suju_qty else 0 end) j_prod_qty  
                FROM i_suju_master_t,I_SUJU_FACT_T,I_COD_T,I_SCH_T  
                where MASTER_BOKJONG = COD_CODE  
                and cod_gbn_code    = '01'  
                and sch_f_bokjong   = cod_code  
                and master_school  = sch_code  
                and MASTER_ORDER   = FACT_ORDER(+)  
                and MASTER_REMAKE  IN ('M','C')  
                and MASTER_JAEPUM  = '{jaepum}'  
                and master_tkyk    in ('C','D','H','I','L','R')  
                and MASTER_QUOTA   in ('{str(int(q1[:2])-1)+q1[-1]}','{str(int(q2[:2])-1)+q2[-1]}','{str(int(q3[:2])-1)+q3[-1]}')  
                and decode('{dt_gb}','1', MASTER_SUJU_DATE,'2', MASTER_APPV_END_DT,'3', FACT_DATE,'4', MASTER_PRODM_DATE) <= TO_DATE('{str(int(date[:4])-1)+date[4:]}','YYYYMMDD')  
                and ('*' = '{bok}'  OR MASTER_BOKJONG   = '{bok}')  
                and ('*' = '{bok2}' OR ( nvl(COD_ETC2,'') = '{bok2}' and (    (substr('{str(int(q1[:2])-1)+q1[-1]}',3,1)  = 'S' and nvl(COD_ETC3,'') IN ('S','T'))  
                                                                                    or (substr('{str(int(q1[:2])-1)+q1[-1]}',3,1) <> 'S' and nvl(COD_ETC3,'') IN ('F','T'))  
                                                                                )  
                                            )   
                    )  
                and ( ('{sel_gb}' = '1' and MASTER_STATUS <> '00') or ('{sel_gb}' = '2' and (MASTER_STATUS <> '00' or (MASTER_STATUS = '00' and to_char(MASTER_ST00_DT,'YYYYMMDD') >= '{str(int(date[:4])-1)+date[4:]}')))  
                    )  
            union all  
            select  '기준 전시즌 수주.홀드량 삭제건' msg  
                    ,master_tkyk        tkyk  
                    ,decode(MASTER_BOKJONG,'R','S','Q','P','Z','D',MASTER_BOKJONG) sch_gb  
                    ,sort   bok_sort  
                    ,0 sch_count  
                    ,0 suju_qty  
                    ,0 h_qty  
                    ,0 prod_qty  
                    ,0 j_sch_count  
                    ,master_suju_qty j_suju_qty  
                    ,decode(master_appv_end_gb,'Y' ,(case when master_appv_end_dt <= TO_DATE('{str(int(date[:4])-1)+date[4:]}','YYYYMMDD') then master_suju_qty else 0 end),0) j_h_qty  
                    ,0 j_tot_qty  
                    ,(case when master_prodm_date <= TO_DATE('{str(int(date[:4])-1)+date[4:]}','YYYYMMDD') and master_prodm_qty > 0  then master_suju_qty else 0 end) j_prod_qty  
                FROM I_SUJU_MASTER_DELETE_T,I_COD_T,I_SCH_T  
                where MASTER_BOKJONG = COD_CODE  
                and cod_gbn_code    = '01'  
                and sch_f_bokjong   = cod_code  
                and master_school  = sch_code  
                and MASTER_REMAKE  IN ('M','C')  
                and MASTER_JAEPUM  = '{jaepum}'  
                and master_tkyk    in ('C','D','H','I','L','R')  
                and MASTER_QUOTA   in ('{str(int(q1[:2])-1)+q1[-1]}','{str(int(q2[:2])-1)+q2[-1]}','{str(int(q3[:2])-1)+q3[-1]}')  
                and decode('{dt_gb}','1', MASTER_SUJU_DATE,'2', MASTER_APPV_END_DT) <= TO_DATE('{str(int(date[:4])-1)+date[4:]}','YYYYMMDD')  
                and to_char(MASTER_DELETE_DT,'YYYYMMDD') >= '{str(int(date[:4])-1)+date[4:]}'  
                and ('*' = '{bok}'  OR MASTER_BOKJONG     = '{bok}')  
                and ('*' = '{bok2}' OR ( nvl(COD_ETC2,'') = '{bok2}' and (    (substr('{str(int(q1[:2])-1)+q1[-1]}',3,1)  = 'S' and nvl(COD_ETC3,'') IN ('S','T'))  
                                                                                    or (substr('{str(int(q1[:2])-1)+q1[-1]}',3,1) <> 'S' and nvl(COD_ETC3,'') IN ('F','T'))  
                                                                                )  
                                            )   
                    )  
                and '{dt_gb}' in ('1','2')  
                and '{sel_gb}' = '2'  
            union all   
            select  '기준 전시즌 최종 수주량' msg  
                    ,master_tkyk        tkyk  
                    ,decode(MASTER_BOKJONG,'R','S','Q','P','Z','D',MASTER_BOKJONG) sch_gb  
                    ,sort   bok_sort  
                    ,0 sch_count  
                    ,0 suju_qty  
                    ,0 h_qty  
                    ,0 prod_qty  
                    ,0 j_sch_count  
                    ,0 j_suju_qty  
                    ,0 j_h_qty  
                    ,master_suju_qty j_tot_qty   
                    ,0 j_prod_qty  
                FROM i_suju_master_t,I_COD_T,I_SCH_T  
                where MASTER_BOKJONG = COD_CODE  
                and cod_gbn_code    = '01'  
                and sch_f_bokjong   = cod_code  
                and master_school  = sch_code  
                and MASTER_REMAKE  IN ('M','C')  
                and MASTER_JAEPUM  = '{jaepum}'  
                and master_tkyk    in ('C','D','H','I','L','R')  
                and MASTER_QUOTA   in ('{str(int(q1[:2])-1)+q1[-1]}','{str(int(q2[:2])-1)+q2[-1]}','{str(int(q3[:2])-1)+q3[-1]}')  
                and master_status  = '60'  
                and ('*' = '{bok}'  OR MASTER_BOKJONG     = '{bok}')  
                and ('*' = '{bok2}' OR ( nvl(COD_ETC2,'') = '{bok2}' and (    (substr('{str(int(q1[:2])-1)+q1[-1]}',3,1)  = 'S' and nvl(COD_ETC3,'') IN ('S','T'))  
                                                                                    or (substr('{str(int(q1[:2])-1)+q1[-1]}',3,1) <> 'S' and nvl(COD_ETC3,'') IN ('F','T'))  
                                                                                )  
                                            )   
                    )  
                ) t  
    group by t.tkyk,t.sch_gb  
    ) z,i_tkyk_t  
    where z.tkyk = tkyk_code
    ORDER BY sort
    '''

    if (bok == 'J') and (max(season)[-1] != 'S'):
        return sql1
    elif (bok == 'H') and (max(season)[-1] != 'S'):
        return sql2
    else:
        return sql1


def make_suju_tkyk(df :pd.DataFrame) -> pd.DataFrame:
    df.columns = ['상권', 'sort', 'bok_sort', '복종', 'sch_count', '수주량', '해제량', '생산량', 'j_sch_count', '전년 동기 수주량', '전년 동기 해제량', '전년최종', '전년 생산량']

    df1 = df.groupby(['sort', '상권'])[['수주량', '해제량', '전년 동기 수주량', '전년 동기 해제량', '전년최종']].agg(sum)

    df1 = df1.reset_index().drop('sort', axis=1)

    # df1 = pd.concat([df1, pd.Series(year_plan, name='연간계획')], axis=1) # 연간계획 추가

    df_tkyk = mod.tkyk_code() # 특약명 merge
    df_tkyk.columns = ['상권', '상권명']
    df1 = df1.merge(df_tkyk, how='left').set_index('상권명').drop('상권', axis=1)

    df1['전년비증감(수주)'] = df1['수주량'] - df1['전년 동기 수주량']
    df1['전년비증감(해제)'] = df1['해제량'] - df1['전년 동기 해제량']
    df1['전년비수주율(%)'] = (df1['수주량'] / df1['전년 동기 수주량'] * 100).round(1).astype(str) + '%'
    df1['수주대비율(%)'] = (df1['해제량'] / df1['수주량'] * 100).round(1).astype(str) + '%'
    df1['전년최종비(%)'] = (df1['수주량'] / df1['전년최종'] * 100).round(1).astype(str) + '%'

    df2 = df1[['수주량', '전년비수주율(%)', '전년최종비(%)', '전년 동기 수주량', '해제량', '수주대비율(%)']].copy()

    df_graph = df2[['수주량', '해제량']].copy()
    df_graph = df_graph.reset_index().melt(id_vars='상권명', var_name='구분', value_name='수량')

    df_graph2 = df1[['전년 동기 수주량', '전년 동기 해제량']].copy()
    df_graph2.columns = ['수주량', '해제량']
    df_graph2 = df_graph2.reset_index().melt(id_vars='상권명', var_name='구분', value_name='수량')

    return df2, df_graph, df_graph2


def make_suju_data(df :pd.DataFrame) -> pd.DataFrame:
    df.columns = ['상권', 'sort', 'bok_sort', '복종', 'sch_count', '수주량', '해제량', '생산량', 'j_sch_count', '전년 동기 수주량', '전년 동기 해제량', '전년최종', '전년 생산량']

    df1 = df.groupby(['bok_sort', '복종'])[['수주량', '해제량', '전년 동기 수주량', '전년 동기 해제량', '전년최종']].agg(sum)

    df1 = df1.reset_index().drop('bok_sort', axis=1)
    
    df1['전년비증감(수주)'] = df1['수주량'] - df1['전년 동기 수주량']
    df1['전년비증감(해제)'] = df1['해제량'] - df1['전년 동기 해제량']
    df1['전년비수주율(%)'] = (df1['수주량'] / df1['전년 동기 수주량'] * 100).round(1).astype(str) + '%'
    df1['전년대비 해제율(%)'] = (df1['해제량'] / df1['전년 동기 해제량'] * 100).round(1).astype(str) + '%'

    df_bok = mod.cod_code('01').drop('cod_etc', axis=1) # 복종명 merge
    df_bok.columns = ['복종', '복종명']
    df1 = df1.merge(df_bok, how='left').set_index('복종명')

    df1 = df1[['수주량', '전년 동기 수주량', '전년비증감(수주)', '전년비수주율(%)', '해제량', '전년 동기 해제량', '전년비증감(해제)', '전년대비 해제율(%)', '전년최종']]

    df_graph = df1[['수주량', '해제량']].copy()
    df_graph = df_graph.reset_index().melt(id_vars='복종명', var_name='구분', value_name='수량')

    df_graph2 = df1[['전년 동기 수주량', '전년 동기 해제량']].copy()
    df_graph2.columns = ['수주량', '해제량']
    df_graph2 = df_graph2.reset_index().melt(id_vars='복종명', var_name='구분', value_name='수량')


    return df1, df_graph, df_graph2


# ---------- 낙찰현황 관련 ----------

def make_sql(season1: str, date: datetime.date) -> str:
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


# 주관구매 낙찰현황 전처리
def make_bid_data(df: pd.DataFrame, season: str) -> pd.DataFrame:
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





if __name__ == "__main__":
    print('영업팀 데이터 모듈파일입니다.')
    