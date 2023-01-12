import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta, time

from data import * # 패키지 불러오기


# emojis: https://www.webfx.com//tools/emoji-cheat-sheet/
st.set_page_config(
    page_title='주간업무보고',
    page_icon=":chart_with_upwards_trend:",
    layout="wide"
)


# 연간계획 (변경되면 입력해줘야 함)
# year_plan: list = [38000, 49000, 26000, 21000, 23000, 28000]


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
    
    df_2seasons = df_2seasons.melt(id_vars=['상권', '보고일자', '시즌', '주차'], var_name='수주_해제_구분', value_name='수량') # 수동그래프 변경이후 추가

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


# 낙찰추이용 쿼리
def make_sql2(season1: str) -> str:
    sql = f'''
    SELECT a.g2b_date,
        Rawtohex(utl_raw.Cast_to_raw(tkyk_name)) tkyk_name,
        sort,
        Rawtohex(utl_raw.Cast_to_raw(schc_small_name)) schc_small_name,
        Round(a.g2b_end_amt / a.g2b_stand_amt, 3) * 100   bid_rate,
        a.g2b_co_gb,
        g2b_qty
    FROM   i_sale_g2b_t a, i_sch_com_t, i_tkyk_t
    WHERE  schc_code (+) = a.g2b_school
        AND a.g2b_tkyk = tkyk_code
        AND a.g2b_end_gb = '9'
        AND ( a.g2b_quota1 IN ( '{season1}', '{season1}' )
                OR a.g2b_quota2 IN ( '{season1}', '{season1}' ) ) 
    '''
    return sql


# 4사 낙찰집계 쿼리
def make_sql3(season1: str, date: str) -> str:
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
            SUM(z.etc_qty)     etc_qty
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
                                        g2b_qty) etc_qty
                FROM   i_sale_g2b_t a,
                    i_sch_com_t
                WHERE  schc_code (+) = a.g2b_school
                    AND a.g2b_end_gb = '9'
                    AND a.g2b_date  <= To_date('{date}', 'yyyy-mm-dd')
                    AND ( a.g2b_quota1 IN ( '{season1}', '{season1}' )
                            OR a.g2b_quota2 IN ( '{season1}', '{season1}' ) )) z,
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


def make_bid_data3(df: pd.DataFrame, date: str) -> pd.DataFrame:
    df['개찰일자'] = date
    df = df.sort_values('sort')
    df.columns = [
        '특약코드',
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
        '개찰일자'
        ]
    
    # 퍼센트 계산용 컬럼
    df['ISELZ_SUM'] = df['아이비_학생수'] + df['엘리트_학생수'] + df['스마트_학생수']  + df['스쿨룩스_학생수'] + df['일반업체_학생수']

    df = df[[
        '개찰일자',
        '특약명',
        '아이비_학생수',
        '스마트_학생수',
        '엘리트_학생수',        
        '스쿨룩스_학생수',
        '일반업체_학생수',
        'ISELZ_SUM'
        ]]

    df = df.melt(id_vars=['개찰일자', '특약명', 'ISELZ_SUM'], var_name='업체구분', value_name='학생수')
    df['업체구분'] = df['업체구분'].str.replace('_학생수','')
    df['업체구분'] = df['업체구분'].str.replace('아이비','아이비클럽')

    return df


def make_bid_data4(season1: str) -> pd.DataFrame:
    # 1. 최초일자 부터
    # sql1 = f'''
    # SELECT Min(g2b_date)
    #   FROM i_sale_g2b_t
    #  WHERE g2b_date IS NOT NULL
    #    AND g2b_end_gb = '9'
    #    AND ( g2b_quota1 IN ( '{season1}', '{season1}' )
    #       OR g2b_quota2 IN ( '{season1}', '{season1}' ) )
    # ''' # 해당시즌의 최초 개찰(낙찰)일자
    # min_date = mod.select_data(sql1).iloc[0][0] # 1 X 1 데이터프레임 형태로 반환됨
    
    # 2. 일단위 (70일)
    # min_date = datetime.today() - timedelta(days=70)
    
    # 3. 주단위 (10주)
    min_date = datetime.today() - timedelta(weeks=10)

    max_date = datetime.today()

    date_list = pd.date_range(start=min_date, end=max_date, freq='W-MON').to_list() # 월요일 기준 주단위 집계 (date_range는 str or datetime-like 다 쓸 수 있음)
    # date_list2 = pd.date_range(start=min_date, end=max_date, freq='D').to_list() # 매일 집계
    # date_list2 = date_list[-10:] # 오늘 기준 이전 10주
    
    df = pd.DataFrame()    
    
    for q_dt in date_list: # 집계 쿼리를 10주치 돌린다
        dt = str(q_dt).split(' ')[0]
        df = pd.concat([df, make_bid_data3(mod.select_data(make_sql3(season1, dt)), dt)])

    df['개찰일자'] = pd.to_datetime(df['개찰일자'])

    return df


def make_bid_data5(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [
        '개찰일자',
        '특약명',
        'sort',
        '학교명',
        '투찰율',
        '업체구분',
        '학생수',
        ]
    
    # 조건
    cond1 = df['업체구분']=='I'
    cond2 = df['업체구분']=='S'
    cond3 = df['업체구분']=='E'
    cond4 = df['업체구분']=='L'

    df['업체명'] = df['업체구분']
    df['업체명'] = df['업체명'].mask(cond1, '아이비클럽').mask(cond2, '스마트').mask(cond3, '엘리트').mask(cond4, '스쿨룩스').mask(~cond1&~cond2&~cond3&~cond4, '일반업체')
    df['sort2'] = df['업체구분']
    df['sort2'] = df['sort2'].mask(cond1, '1').mask(cond2, '2').mask(cond3, '3').mask(cond4, '4').mask(~cond1&~cond2&~cond3&~cond4, '5')
    df = df.sort_values(['sort2', 'sort', '투찰율'], ascending=[True, True, False])
    df = df[['개찰일자', '특약명', 'sort', '학교명', '투찰율', '업체명', '학생수']].copy()

    # 구간 분할
    df['구간'] = ''
    df['구간'] = df['구간'].mask((df['투찰율'] // 10) >= 9, '90%~100%').mask((df['투찰율'] // 10) == 8, '80%~89%').mask((df['투찰율'] // 10) == 7, '70%~79%').mask((df['투찰율'] // 10) == 6, '60%~69%').mask((df['투찰율'] // 10) == 5, '50%~59%').mask((df['투찰율'] // 10) <= 4, '0%~49%')
    # df = df.sort_values(['구간', 'sort'])

    return df


def make_bid_data6(df: pd.DataFrame) -> pd.DataFrame:
    df1 = df.pivot_table('학생수', index='구간', columns='업체명', aggfunc='sum', fill_value=0).sort_index(ascending=False)
    df1['I_비율'] = round((df1['아이비클럽'] / df1['아이비클럽'].sum()) * 100, 1).astype(str)
    df1['S_비율'] = round((df1['스마트'] / df1['스마트'].sum()) * 100, 1).astype(str)
    df1['E_비율'] = round((df1['엘리트'] / df1['엘리트'].sum()) * 100, 1).astype(str)
    df1['L_비율'] = round((df1['스쿨룩스'] / df1['스쿨룩스'].sum()) * 100, 1).astype(str)
    df1['Z_비율'] = round((df1['일반업체'] / df1['일반업체'].sum()) * 100, 1).astype(str)
    df1 = df1[['아이비클럽', 'I_비율', '스마트', 'S_비율', '엘리트', 'E_비율','스쿨룩스', 'L_비율', '일반업체', 'Z_비율']]

    return df1




# SQLITE3 SQL
sales_sql_1 = f'''
select * from sales_suju_haje_t
'''

# 기본 데이터프레임 만들기
df_sales_base = mod.connect_sqlite3(mod.db_file, sales_sql_1)


# ---------- 사이드바 (영업팀) ----------

st.sidebar.header('시즌')

# 사이드바 시즌 선택
choosen_season_sales = st.sidebar.selectbox(
    '시즌을 선택하세요 : ',
    # options=['N+F시즌', 'N시즌', 'S시즌', 'F시즌'],
    options=['N시즌', 'S시즌', 'F시즌'],

)

st.sidebar.header('조건')
# query_date = st.sidebar.date_input('기준일자를 선택하세요 : ', datetime.strptime(mod.last_fri, "%Y/%m/%d")) # 지난주 금요일
query_date = st.sidebar.date_input('기준일자를 선택하세요 : ', datetime.today()) # 오늘
query_date_j = (datetime.combine(query_date, time()) - timedelta(weeks=1)).date() # 선택한 날짜에서 1주전



if choosen_season_sales == 'N시즌':
    season_list: list = [x for x in (df_sales_base['시즌'].unique()) if x[-1]=='N'][-2:]
elif choosen_season_sales == 'S시즌':
    season_list: list = [x for x in (df_sales_base['시즌'].unique()) if x[-1]=='S'][-2:]
elif choosen_season_sales == 'F시즌':
    season_list: list = [x for x in (df_sales_base['시즌'].unique()) if x[-1]=='F'][-2:]
elif choosen_season_sales == 'N+F시즌':
    season_list: list = [x for x in (df_sales_base['시즌'].unique()) if x[-1]=='N'][-2:]
    season_list_NF: list = [x for x in (df_sales_base['시즌'].unique()) if x[-1]=='N' or x[-1]=='F'][-2:]


df_sales = make_season_data(df_sales_base, season_list) # 베이스 데이터, 선택된 시즌

# 추이 상권통합
df_sales_total_sum = df_sales.reset_index().groupby(['보고일자', '시즌', '주차', '수주_해제_구분'])[['수량']].agg(sum).reset_index().set_index('보고일자')



# 최종 주차, 수주량 합계, 해제량 합계, 주간 수주량, 주간 해제량, 전주 수주량, 전주 해제량
# week, week_suju_sum, week_haje_sum, j_week_suju_sum, j_week_haje_sum, week_suju_qty, week_haje_qty, j_week_suju_qty, j_week_haje_qty = make_arg(df_sales)


# left_column, middle1_column, middle2_column, right_column = st.columns(4)
# with left_column:
#     st.metric('수주량 합계', week_suju_sum, delta=f'{week_suju_sum - j_week_suju_sum}', delta_color="normal", help=f'전주 수주량 합계 : {j_week_suju_sum}')
# with middle1_column:
#     st.metric('해제량 합계', week_haje_sum, delta=f'{week_haje_sum - j_week_haje_sum}', delta_color="normal", help=f'전주 해제량 합계 : {j_week_haje_sum}')
# with middle2_column:
#     st.metric('수주 변동량', week_suju_qty, delta=f'{week_suju_qty - j_week_suju_qty}', delta_color="normal", help=f'전주 수주 변동량 : {j_week_suju_qty}')
# with right_column:
#     st.metric('해제 변동량', week_haje_qty, delta=f'{week_haje_qty - j_week_haje_qty}', delta_color="normal", help=f'전주 해제 변동량 : {j_week_haje_qty}')


# st.markdown('''---''')


# -------------------- 그래프 (영업팀) --------------------

colors_basic = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3'] # 상권별 색깔 (공용)
colors = ['#4C78A8', '#F58518', '#E45756', '#72B7B2', '#54A24B', '#EECA3B'] # 상권별 색깔 (공용)

# Plotly GO Ver.
fig1 = go.Figure()

for ss in (df_sales['시즌'].unique()):
    for i, ar in enumerate(df_sales['상권'].unique()):
        for gn in (df_sales['수주_해제_구분'].unique()):
            if ss == max(df_sales['시즌'].unique()):
                # fig1.add_scatter(
                #     x=[fig1.data[0].x[5]],
                #     y=[fig1.data[0].y[-1]],
                #     text=[fig1.data[0].y[-1]],
                #     mode = 'markers+text',
                #     line=dict(color=colors[i], width=4),
                #     marker=dict(size=10),
                #     showlegend = False,
                #     textposition='middle right',
                #     )
                if gn == '수주량':
                    fig1.add_trace(
                        go.Scatter(
                            x=df_sales[(df_sales['시즌']==ss) & (df_sales['상권']==ar) & (df_sales['수주_해제_구분']==gn)].index,
                            y=df_sales[(df_sales['시즌']==ss) & (df_sales['상권']==ar) & (df_sales['수주_해제_구분']==gn)]['수량'],
                            mode='markers+lines',
                            name=f'{ss} {ar}상권 {gn}',
                            legendgroup=f'{ar}상권',
                            legendgrouptitle_text=f'{ar}상권',
                            line=dict(color=colors[i], width=4),
                            marker=dict(size=10),
                            ))
                else:
                    fig1.add_trace(
                        go.Scatter(
                            x=df_sales[(df_sales['시즌']==ss) & (df_sales['상권']==ar) & (df_sales['수주_해제_구분']==gn)].index,
                            y=df_sales[(df_sales['시즌']==ss) & (df_sales['상권']==ar) & (df_sales['수주_해제_구분']==gn)]['수량'],
                            mode='markers+lines',
                            name=f'{ss} {ar}상권 {gn}',
                            legendgroup=f'{ar}상권',
                            legendgrouptitle_text=f'{ar}상권',
                            line=dict(color=colors[i], width=4),
                            marker=dict(size=10),
                            marker_symbol='star', # 별 마커
                            ))
            else:
                if gn == '수주량':
                    fig1.add_trace(
                        go.Scatter(
                            x=df_sales[(df_sales['시즌']==ss) & (df_sales['상권']==ar) & (df_sales['수주_해제_구분']==gn)].index,
                            y=df_sales[(df_sales['시즌']==ss) & (df_sales['상권']==ar) & (df_sales['수주_해제_구분']==gn)]['수량'],
                            mode='lines',
                            name=f'{ss} {ar}상권 {gn}',
                            legendgroup=f'{ar}상권',
                            legendgrouptitle_text=f'{ar}상권',
                            line=dict(color=colors[i], dash='dot'), # 점선
                            ))
                else:
                    fig1.add_trace(
                        go.Scatter(
                            x=df_sales[(df_sales['시즌']==ss) & (df_sales['상권']==ar) & (df_sales['수주_해제_구분']==gn)].index,
                            y=df_sales[(df_sales['시즌']==ss) & (df_sales['상권']==ar) & (df_sales['수주_해제_구분']==gn)]['수량'],
                            mode='lines',
                            name=f'{ss} {ar}상권 {gn}',
                            legendgroup=f'{ar}상권',
                            legendgrouptitle_text=f'{ar}상권',
                            line=dict(color=colors[i], dash='dash'), # 긴 점선
                            opacity=0.5, # 투명도
                            ))
fig1.update_xaxes(dtick='M1', tickformat='%Y/%m')
fig1.update_yaxes(tickformat=',d')
fig1.update_layout(
    paper_bgcolor='rgba(233,233,233,233)',
    plot_bgcolor='rgba(0,0,0,0)',
    height=850,
    title=f'{max(season_list)}/{min(season_list)} 수주량, 해제량 시즌 비교 (상권)',
    title_font_size=30,
    legend=dict(
        bgcolor='#D6E487',
        # bordercolor='lightgreen',
        # borderwidth=1,
        # orientation='h',
        traceorder='grouped+reversed', # 그룹화된 역정렬
        groupclick='toggleitem' # 개별토글 (더블클릭기능과 별개)
        ),
    )
# fig1.add_annotation(
#     x=max(df_sales[(df_sales['시즌']=='23N') & (df_sales['상권']=='서울') & (df_sales['수주_해제_구분']=='수주량')].index),
#     y=max(df_sales[(df_sales['시즌']=='23N') & (df_sales['상권']=='서울') & (df_sales['수주_해제_구분']=='수주량')]['수량']),
#     text=max(df_sales[(df_sales['시즌']=='23N') & (df_sales['상권']=='서울') & (df_sales['수주_해제_구분']=='수주량')]['수량']),
#     showarrow=True,
#     arrowhead=1,
#     )
    

# Plotly PX ver.

# fig1 = px.line(df_sales[df_sales['시즌']=='22N'],
#             y='수주량',
#             color='상권',
#             # title=f'{season_list} 시즌 상권별 수주/해제 현황',
#             # text='주차',
#             markers=True,
#             # facet_row='시즌',
#             height=700,
#             # template='plotly_white'
#             )
# fig1.add_trace(go.Scatter(
#     mode='line',
#     x=df_sales[(df_sales['시즌']=='22N') & (df_sales['상권']=='서울')].index,
#     y=df_sales[(df_sales['시즌']=='22N') & (df_sales['상권']=='서울')]['해제량'],

# ))

# fig1.update_layout(paper_bgcolor='rgba(233,233,233,233)', plot_bgcolor='rgba(0,0,0,0)')

# fig1.update_xaxes(
#     rangeslider=dict(
#         visible=True,
#         thickness=0.02,
#         )) # 슬라이드 조절바


fig1_1 = go.Figure()

for ss in (df_sales_total_sum['시즌'].unique()):
    for gn in (df_sales_total_sum['수주_해제_구분'].unique()):
        if ss == max(df_sales_total_sum['시즌'].unique()):
            if gn == '수주량':
                fig1_1.add_trace(
                    go.Scatter(
                        x=df_sales_total_sum[(df_sales_total_sum['시즌']==ss) & (df_sales_total_sum['수주_해제_구분']==gn)].index,
                        y=df_sales_total_sum[(df_sales_total_sum['시즌']==ss) & (df_sales_total_sum['수주_해제_구분']==gn)]['수량'],
                        text=df_sales_total_sum[(df_sales_total_sum['시즌']==ss) & (df_sales_total_sum['수주_해제_구분']==gn)]['수량'],
                        textposition='middle right',
                        textfont=dict(
                            color=colors_basic[0],
                            size=18,
                        ),
                        mode='markers+lines+text',
                        name=f'{ss} {gn}',
                        legendgroup=gn,
                        legendgrouptitle_text=gn,
                        line=dict(color=colors_basic[0], width=4),
                        marker=dict(size=10),
                        ))
            else:
                fig1_1.add_trace(
                    go.Scatter(
                        x=df_sales_total_sum[(df_sales_total_sum['시즌']==ss) & (df_sales_total_sum['수주_해제_구분']==gn)].index,
                        y=df_sales_total_sum[(df_sales_total_sum['시즌']==ss) & (df_sales_total_sum['수주_해제_구분']==gn)]['수량'],
                        text=df_sales_total_sum[(df_sales_total_sum['시즌']==ss) & (df_sales_total_sum['수주_해제_구분']==gn)]['수량'],
                        textposition='middle right',
                        textfont=dict(
                            color=colors_basic[1],
                            size=18,
                        ),
                        mode='markers+lines+text',                    
                        name=f'{ss} {gn}',
                        legendgroup=gn,
                        legendgrouptitle_text=gn,
                        line=dict(color=colors_basic[1], width=4),
                        marker=dict(size=10),
                        marker_symbol='star', # 별 마커
                        ))
        else:
            if gn == '수주량':
                fig1_1.add_trace(
                    go.Scatter(
                        x=df_sales_total_sum[(df_sales_total_sum['시즌']==ss) & (df_sales_total_sum['수주_해제_구분']==gn)].index,
                        y=df_sales_total_sum[(df_sales_total_sum['시즌']==ss) & (df_sales_total_sum['수주_해제_구분']==gn)]['수량'],
                        mode='lines',
                        name=f'{ss} {gn}',
                        legendgroup=gn,
                        legendgrouptitle_text=gn,
                        line=dict(color=colors_basic[0], dash='dot'), # 점선
                        ))
            else:
                fig1_1.add_trace(
                    go.Scatter(
                        x=df_sales_total_sum[(df_sales_total_sum['시즌']==ss) & (df_sales_total_sum['수주_해제_구분']==gn)].index,
                        y=df_sales_total_sum[(df_sales_total_sum['시즌']==ss) & (df_sales_total_sum['수주_해제_구분']==gn)]['수량'],
                        mode='lines',
                        name=f'{ss} {gn}',
                        legendgroup=gn,
                        legendgrouptitle_text=gn,
                        line=dict(color=colors_basic[1], dash='dash'), # 긴 점선
                        opacity=0.5, # 투명도
                        ))
fig1_1.update_traces(texttemplate='%{text:,}')
fig1_1.update_xaxes(dtick='M1', tickformat='%Y/%m')
fig1_1.update_yaxes(tickformat=',d')
fig1_1.update_layout(
    paper_bgcolor='rgba(233,233,233,233)',
    plot_bgcolor='rgba(0,0,0,0)',
    height=850,
    title=f'{max(season_list)}/{min(season_list)} 수주량, 해제량 시즌 비교 (전체)',
    title_font_size=30,
    legend=dict(
        # bgcolor='#D6E487',
        # bordercolor='lightgreen',
        # borderwidth=1,
        # orientation='h',
        traceorder='grouped+reversed', # 그룹화된 역정렬
        groupclick='toggleitem' # 개별토글 (더블클릭기능과 별개)
        ),
    )


# ---------- 수주/해제 데이터(전체) ----------

if choosen_season_sales == 'S시즌':
    suju_bok1 = '*'
    df_sales_suju_base1 = mod.select_data(make_sql_suju(suju_bok1, season_list, query_date))
    df_sales_suju, df_sales_suju_graph, df_sales_suju_graph2 = make_suju_data(df_sales_suju_base1)
else:
    suju_bok1 = 'J'
    suju_bok2 = 'H'
    df_sales_suju_base1 = mod.select_data(make_sql_suju(suju_bok1, season_list, query_date))
    df_sales_suju_base2 = mod.select_data(make_sql_suju(suju_bok2, season_list, query_date))
    df_sales_suju, df_sales_suju_graph, df_sales_suju_graph2 = make_suju_data(pd.concat([df_sales_suju_base1, df_sales_suju_base2]))

# 신규그래프용
df_sales_suju_graph['시즌'] = max(season_list)
df_sales_suju_graph2['시즌'] = min(season_list)
df_sales_suju_graph3 = pd.concat([df_sales_suju_graph, df_sales_suju_graph2])


# ---------- 수주/해제 데이터(상권) ----------

if choosen_season_sales == 'S시즌':
    df_sales_suju_tkyk, df_sales_suju_tkyk_graph, df_sales_suju_tkyk_graph2 = make_suju_tkyk(df_sales_suju_base1) # 하복
else:
    df_sales_suju_tkyk, df_sales_suju_tkyk_graph, df_sales_suju_tkyk_graph2 = make_suju_tkyk(pd.concat([df_sales_suju_base1, df_sales_suju_base2])) # J, H


# ---------- 낙찰현황 데이터 ----------

df_sales_base_bid = mod.select_data(make_sql(max(season_list), query_date)).sort_values('sort').reset_index(drop=True) # 베이스
df_sales_base_bid_j = mod.select_data(make_sql(max(season_list), query_date_j)).sort_values('sort').reset_index(drop=True) # 베이스 (1주일전)


df_sales_bid, df_sales_bid_graph = make_bid_data(df_sales_base_bid.copy(), max(season_list))
df_sales_bid_j, df_sales_bid_graph_j = make_bid_data(df_sales_base_bid_j.copy(), max(season_list)) # 1주일전


df_sales_bid_flow = make_bid_data4(max(season_list))


# ---------- 상권 낙찰 정리 데이터 ----------

df_bid_tkyk = df_sales_base_bid.copy()

df_bid_tkyk.columns = [
        '상권코드', '상권명', 'sort',
        'I_학교', 'E_학교', 'S_학교', 'L_학교', '일반_학교',
        'I_학생', 'E_학생', 'S_학생', 'L_학생', '일반_학생',
        'I_학교', 'E_학교', 'S_학교', 'L_학교', '일반_학교',
        'I_학생', 'E_학생', 'S_학생', 'L_학생', '일반_학생',
        '전년최종학교', '전년최종학생'
    ]
df_bid_tkyk = df_bid_tkyk.set_index('상권명').drop(['상권코드', 'sort', '전년최종학교', '전년최종학생'], axis=1)

df_bid_tkyk_1 = df_bid_tkyk.iloc[:, :10].copy()
df_bid_tkyk_2 = df_bid_tkyk.iloc[:, 10:].copy()

df_bid_tkyk_1 = df_bid_tkyk_1[[
    'I_학교', 'S_학교', 'E_학교', 'L_학교', '일반_학교',
    'I_학생', 'S_학생', 'E_학생', 'L_학생', '일반_학생',
]]
df_bid_tkyk_2 = df_bid_tkyk_2[[
    'I_학교', 'S_학교', 'E_학교', 'L_학교', '일반_학교',
    'I_학생', 'S_학생', 'E_학생', 'L_학생', '일반_학생',
]]


# 투찰율 관련
df_rate = mod.select_data(make_sql2(max(season_list)))
df_bid_rate_graph = make_bid_data5(df_rate) # 전국
df_bid_rate = make_bid_data6(df_bid_rate_graph)

# df_bid_rate_C, df_bid_rate_graph_C = make_bid_data5(df_rate['특약명']=='서울상권')
# df_bid_rate_H, df_bid_rate_graph_H = make_bid_data5(df_rate['특약명']=='중부상권')
# df_bid_rate_D, df_bid_rate_graph_D = make_bid_data5(df_rate['특약명']=='대전상권')
# df_bid_rate_L, df_bid_rate_graph_L = make_bid_data5(df_rate['특약명']=='광주상권')
# df_bid_rate_I, df_bid_rate_graph_I = make_bid_data5(df_rate['특약명']=='대구상권')
# df_bid_rate_R, df_bid_rate_graph_R = make_bid_data5(df_rate['특약명']=='부산상권')


# ---------- 그래프 (영업팀) ----------

# Plotly PX Ver.

colors2 = {'(?)': '#EECA3B', '아이비클럽': '#9BBA53', '스마트': '#6183BF', '엘리트': '#BB534A', '스쿨룩스': '#E36C0E', '일반업체': '#BFBFBF'}
colors3 = ['#9BBA53', '#6183BF', '#BB534A', '#E36C0E', '#BFBFBF']

# fig2 = px.sunburst(df_sales_bid_graph,
#             path=['시즌', '업체구분', '특약명'],
#             values='학생수',
#             color='업체구분',
#             height=500,
#             color_discrete_map=colors2,
#             )
# fig2.update_layout(
#     # plot_bgcolor="rgba(0,0,0,0)",
#     margin = dict(t=0, l=0, r=0, b=0),
# )


# fig3 = px.sunburst(df_sales_bid_graph,
#             path=['업체구분', '특약명', '시즌'],
#             values='학생수',
#             color='업체구분',
#             height=500,
#             color_discrete_map=colors2,
#             )
# fig3.update_layout(
#     # plot_bgcolor="rgba(0,0,0,0)",
#     margin = dict(t=0, l=0, r=0, b=0),
# )


# Plotly GO Ver.
fig4 = go.Figure()

for ss in (df_sales_bid_graph['시즌'].unique()):
    # for ar, c in zip((reversed(df_sales_bid_graph['특약명'].unique())), reversed(colors)):
    for ar, c in zip(df_sales_bid_graph['특약명'].unique(), colors):
        plot_df_4 = df_sales_bid_graph[ (df_sales_bid_graph['시즌']==ss) & (df_sales_bid_graph['특약명']==ar) ]
        if ss == max((df_sales_bid_graph['시즌'].unique())):
            fig4.add_trace(
                go.Bar(
                    y=[plot_df_4['업체구분'], plot_df_4['시즌']],
                    x=plot_df_4['학생수'],
                    name=ar,
                    legendgroup=ss,
                    legendgrouptitle_text=ss,
                    text=plot_df_4['학생수'],
                    orientation='h',
                    marker_color=c,
                    offset=-0.3,
                    hovertemplate=
                    '<b>%{text:,}</b><br>' + '%{y}<br>',
                    ))
        else:
            fig4.add_trace(
                go.Bar(
                    y=[plot_df_4['업체구분'], plot_df_4['시즌']],
                    x=plot_df_4['학생수'],
                    name=ar,
                    legendgroup=ss,
                    legendgrouptitle_text=ss,
                    text=plot_df_4['학생수'],
                    orientation='h',
                    marker_color=c,
                    offset=-0.5,
                    marker_pattern_shape='/',
                    opacity=0.8, # 투명도
                    hovertemplate=
                    '<b>%{text:,}</b><br>' + '%{y}<br>',
                    ))
fig4.update_xaxes(tickformat=',d')
fig4.update_yaxes(dividerwidth=3)
fig4.update_layout(
    paper_bgcolor='rgba(233,233,233,233)',
    plot_bgcolor='rgba(0,0,0,0)',
    height=600,
    barmode='stack',
    # bargap=0.1,
    bargroupgap=0.1,
    title=f'{max(season_list)}/{min(season_list)} 주관구매 낙찰 시즌 비교',
    title_font_size=30,
    legend=dict(
        traceorder='grouped', # legend 뒤집기
        groupclick='toggleitem' # 개별토글 (더블클릭기능과 별개)
        ),
    # uniformtext_minsize=18, # 균일폰트 (텍스트만)
    # uniformtext_mode='hide',
    font_size=16, # 전체폰트 (틱, 텍스트 모두)
    hoverlabel_font_size=20,
)
fig4.update_traces(texttemplate='%{text:,}')
fig4['layout']['yaxis']['autorange'] = 'reversed' # Y축 값 뒤집기
# fig4.add_annotation(
#     x=df_sales_bid_graph.groupby(['시즌','업체구분'])[['학생수']].agg(sum)['학생수'].agg(max)//2,
#     y=-1,
#     showarrow=True,
#     arrowsize=1,
#     arrowwidth=3,
#     ax=-500,
#     ay=-0.6,
#     arrowhead=2
#     )
# fig4.add_annotation(
#     x=df_sales_bid_graph.groupby(['시즌','업체구분'])[['학생수']].agg(sum)['학생수'].agg(max)//4,
#     y=-1.4,
#     showarrow=False,
#     text='순서 : 서울 → 중부 → 대전 → 광주 → 대구 → 부산',
#     bgcolor='#B6D317',
#     # opacity=0.7,
#     )
x_pos_2 = 0
for ar, c in zip(df_sales_bid_graph['특약명'].unique(), colors):
    x_pos_1 = df_sales_bid_graph[(df_sales_bid_graph['시즌']==max(season_list)) & (df_sales_bid_graph['업체구분']=='아이비클럽') & (df_sales_bid_graph['특약명']==ar)]['학생수'].agg(sum)
    fig4.add_annotation(
        x=x_pos_2 + x_pos_1,
        y=-0.25,
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        text=ar,
        bgcolor=c,
        axref='x',
        ayref='y',
        ax = x_pos_2 + (x_pos_1 / 2),
        ay = -1,
        )
    x_pos_2 = x_pos_2 + x_pos_1



# Plotly PX Ver.

# fig4 = px.bar(df_sales_bid_graph,
#             x='학생수',
#             y='업체구분',
#             color='특약명',
#             orientation='h',
#             title=f'상권별 낙찰 현황 시즌비교',
#             text='학생수',
#             height=700,
#             # template='plotly_white',
#             facet_row='시즌',
#             facet_row_spacing=0.1,
#             )

# fig4.update_layout(
#     paper_bgcolor='rgba(233,233,233,233)',
#     plot_bgcolor='rgba(0,0,0,0)',
#     uniformtext=dict(minsize=10, mode='hide'),
# )


# # 통합 수주량

# fig5 = px.bar(df_sales_suju_graph2,
#             x='복종명',
#             y='수량',
#             color='구분',
#             title=f'{min(season_list)} 수주량/해제량 (전체)',
#             text='수량',
#             barmode='group',
#             height=500,
#             # template='plotly_white',
#             )
# fig5.update_traces(texttemplate='%{text:,}', width=0.25, textposition='outside',) # 바 두께 (0 ~ 1)
# fig5.update_yaxes(tickformat=',d')
# fig5.update_layout(
#     paper_bgcolor='rgba(233,233,233,233)', plot_bgcolor='rgba(0,0,0,0)',
#     uniformtext=dict(minsize=10, mode='hide'),
#     yaxis_range=[0, max(df_sales_suju_graph['수량'])*1.1],
#     title_font_size=30,
# )

# fig6 = px.bar(df_sales_suju_graph,
#             x='복종명',
#             y='수량',
#             color='구분',
#             title=f'{max(season_list)} 수주량/해제량 (전체)',
#             text='수량',
#             barmode='group',
#             height=500,
#             # template='plotly_white',
#             )
# fig6.update_traces(texttemplate='%{text:,}', width=0.25, textposition='outside',) # 바 두께 (0 ~ 1)
# fig6.update_yaxes(tickformat=',d')
# fig6.update_layout(
#     paper_bgcolor='rgba(233,233,233,233)', plot_bgcolor='rgba(0,0,0,0)',
#     uniformtext=dict(minsize=10, mode='hide'),
#     yaxis_range=[0, max(df_sales_suju_graph['수량'])*1.1],
#     title_font_size=30,
# )



# 상권별 수주
df_sales_suju_tkyk_graph['시즌'] = max(season_list)
df_sales_suju_tkyk_graph2['시즌'] = min(season_list)
plot_df_7 = pd.concat([df_sales_suju_tkyk_graph, df_sales_suju_tkyk_graph2])


fig7_1 = go.Figure()

for ss in plot_df_7['시즌'].unique():
    for gb, c in zip(plot_df_7['구분'].unique(), colors_basic):
        plot_df_7_1 = plot_df_7[ (plot_df_7['시즌']==ss) & (plot_df_7['구분']==gb) ]
        if ss == max((plot_df_7['시즌'].unique())):
            fig7_1.add_trace(
                go.Bar(
                    x=plot_df_7_1['상권명'],
                    y=plot_df_7_1['수량'],
                    name=f'{ss} {gb}',
                    legendgroup=gb,
                    legendgrouptitle_text=gb,
                    text=plot_df_7_1['수량'],
                    marker_color=c,
                    hovertemplate=
                    '<b>%{text:,}</b><br>' + '%{y}<br>',
                    ))
        else:
            fig7_1.add_trace(
                go.Bar(
                    x=plot_df_7_1['상권명'],
                    y=plot_df_7_1['수량'],
                    name=f'{ss} {gb}',
                    legendgroup=gb,
                    legendgrouptitle_text=gb,
                    text=plot_df_7_1['수량'],
                    marker_color=c,
                    marker_pattern_shape='/',
                    opacity=0.8, # 투명도
                    hovertemplate=
                    '<b>%{text:,}</b><br>' + '%{y}<br>',
                    ))
fig7_1.update_yaxes(tickformat=',d')
fig7_1.update_layout(
    paper_bgcolor='rgba(233,233,233,233)',
    plot_bgcolor='rgba(0,0,0,0)',
    height=500,
    barmode='group',
    title=f'{max(season_list)}/{min(season_list)} 수주량/해제량 (상권별)',
    title_font_size=30,
    legend=dict(
        traceorder='grouped', # legend 뒤집기
        groupclick='toggleitem' # 개별토글 (더블클릭기능과 별개)
        ),
    font_size=18, # 전체폰트 (틱, 텍스트 모두)
    hoverlabel_font_size=20,
    yaxis_range=[0, max(plot_df_7['수량'])*1.1],
)
fig7_1.update_traces(texttemplate='%{text:,}', textposition='outside')


# # 시즌 나눈 그래프
# fig7 = px.bar(df_sales_suju_tkyk_graph2,
#             x='상권명',
#             y='수량',
#             color='구분',
#             title=f'{min(season_list)} 수주량/해제량 (상권별)',
#             text='수량',
#             barmode='group',
#             height=500,
#             pattern_shape_sequence='/',
#             # template='plotly_white',
#             )
# fig7.update_yaxes(tickformat=',d')
# fig7.update_layout(
#     paper_bgcolor='rgba(233,233,233,233)', plot_bgcolor='rgba(0,0,0,0)',
#     uniformtext=dict(minsize=10, mode='hide'),
#     yaxis_range=[0, max(df_sales_suju_graph['수량']/2)],
#     title_font_size=30,
# )
# fig7.update_traces(texttemplate='%{text:,}', textposition='outside')


# fig8 = px.bar(df_sales_suju_tkyk_graph,
#             x='상권명',
#             y='수량',
#             color='구분',
#             title=f'{max(season_list)} 수주량/해제량 (상권별)',
#             text='수량',
#             barmode='group',
#             height=500,
#             # template='plotly_white',
#             )
# fig8.update_yaxes(tickformat=',d')
# fig8.update_layout(
#     paper_bgcolor='rgba(233,233,233,233)', plot_bgcolor='rgba(0,0,0,0)',
#     uniformtext=dict(minsize=10, mode='hide'),
#     yaxis_range=[0, max(df_sales_suju_graph['수량']/2)],
#     title_font_size=30,
# )
# fig8.update_traces(texttemplate='%{text:,}', textposition='outside')


# PX Ver.

fig9 = px.line(df_sales_bid_flow[df_sales_bid_flow['업체구분']!='일반업체'],
            x='개찰일자',
            y='학생수',
            color='업체구분',
            title=f'{max(season_list)} 상권별 4사 낙찰추이',
            # text='학생수',
            height=700,
            facet_col='특약명',
            facet_col_wrap=3,
            markers=True,
            color_discrete_map=colors2,
            )
fig9.update_traces(
    textposition='top right',
    texttemplate='%{text:,}',
    # textfont_size=14,
    )
fig9.update_layout(
    title_font_size=30,
    paper_bgcolor='rgba(233,233,233,233)', plot_bgcolor='rgba(0,0,0,0)',
    # uniformtext=dict(minsize=10, mode='hide'),
)
fig9.update_xaxes(tickformat='%Y-%m-%d')
fig9.update_yaxes(tickformat=',d')


# GO Ver.

fig10 = go.Figure()

for i, ar in enumerate(df_sales_bid_flow['특약명'].unique()):
    for gn in (df_sales_bid_flow['업체구분'].unique()):
        plot_df_10 = df_sales_bid_flow[ (df_sales_bid_flow['특약명']==ar) & (df_sales_bid_flow['업체구분']==gn)] 
        if ar == '서울상권':
            fig10.add_trace(
                go.Scatter(
                    x=plot_df_10['개찰일자'],
                    y=plot_df_10['학생수'],
                    mode='markers+lines+text',
                    name=f'{ar} {gn}',
                    legendgroup=ar,
                    legendgrouptitle_text=ar,
                    line=dict(color=colors2[gn], width=4),
                    marker=dict(size=10),
                    text=plot_df_10['학생수'],
                    textposition='top right',
                    textfont=dict(
                        color=colors2[gn],
                        size=18,
                    )))
        else:
            fig10.add_trace(
                go.Scatter(
                    x=plot_df_10['개찰일자'],
                    y=plot_df_10['학생수'],
                    mode='markers+lines+text',
                    name=f'{ar} {gn}',
                    legendgroup=ar,
                    legendgrouptitle_text=ar,
                    visible='legendonly',
                    line=dict(color=colors2[gn], width=4),
                    marker=dict(size=10),
                    text=plot_df_10['학생수'],
                    textposition='top right',
                    textfont=dict(
                        color=colors2[gn],
                        size=18,
                    )))
fig10.update_layout(
    paper_bgcolor='rgba(233,233,233,233)',
    plot_bgcolor='rgba(0,0,0,0)',
    height=800,
    title=f'{max(season_list)} 상권별 낙찰추이 (상세)',
    title_font_size=30,
    legend=dict(
        orientation='h',
        groupclick='toggleitem', # 개별토글 (더블클릭기능과 별개)
        x=0, y=0,
        ),
    )
fig10.update_traces(texttemplate='%{text:,}')
fig10.update_xaxes(tickformat='%Y-%m-%d')
fig10.update_yaxes(tickformat=',d')


# GO Ver.

# fig11 = go.Figure()

# for i, ar in enumerate(df_sales_bid_flow['특약명'].unique()):
#     for gn in (df_sales_bid_flow['업체구분'].unique()):
#         plot_df_11 = df_sales_bid_flow[ (df_sales_bid_flow['특약명']==ar) & (df_sales_bid_flow['업체구분']==gn)]
#         if ar == '서울상권':
#             fig11.add_trace(
#                 go.Funnel(
#                     # x=(plot_df_11['학생수'] / plot_df_11['ISELZ_SUM'] * 100).round(1),
#                     x=plot_df_11['학생수'],
#                     y=plot_df_11['개찰일자'],
#                     name=f'{ar} {gn}',
#                     legendgroup=ar,
#                     legendgrouptitle_text=ar,
#                     marker = {"colorscale": colors3,},
#                     text=(plot_df_11['학생수'] / plot_df_11['ISELZ_SUM'] * 100).round(1).astype(str) + '%',
#                     # texttemplate='%{x}%'
#                     ))
#         else:
#             fig11.add_trace(
#                 go.Funnel(
#                     # x=(plot_df_11['학생수'] / plot_df_11['ISELZ_SUM'] * 100).round(1),
#                     x=plot_df_11['학생수'],
#                     y=plot_df_11['개찰일자'],
#                     name=f'{ar} {gn}',
#                     legendgroup=ar,
#                     legendgrouptitle_text=ar,
#                     visible='legendonly',
#                     marker = {"colorscale": colors3,},
#                     text=(plot_df_11['학생수'] / plot_df_11['ISELZ_SUM'] * 100).round(1).astype(str) + '%',
#                     # texttemplate='%{x}%'
#                     ))
# fig11.update_layout(
#     paper_bgcolor='rgba(233,233,233,233)',
#     plot_bgcolor='rgba(0,0,0,0)',
#     height=800,
#     title=f'{max(season_list)} 상권별 낙찰 점유율 변화 (주단위)',
#     title_font_size = 30,
#     font_size=16,
#     legend=dict(
#         orientation='h',
#         # groupclick='toggleitem', # 개별토글 (더블클릭기능과 별개)
#         x=0, y=0,
#         ),
#     # yaxis_tickformat = '%Y-%m-%d',
# )
# fig11.update_yaxes(
#     tickmode = 'array',
#     tickvals = plot_df_11['개찰일자'],
#     tickformat='%Y-%m-%d',
# )
# # fig11['layout']['yaxis']['autorange'] = 'reversed' # Y축 값 뒤집기


fig11 = go.Figure()

for ar in (df_sales_bid_flow['특약명'].unique()):
    for c, gn in zip(reversed(colors3), reversed(df_sales_bid_flow['업체구분'].unique())):
        plot_df_11 = df_sales_bid_flow[ (df_sales_bid_flow['특약명']==ar) & (df_sales_bid_flow['업체구분']==gn)]
        if ar == '서울상권':
            fig11.add_trace(
                go.Bar(
                    y=plot_df_11['학생수'],
                    x=plot_df_11['개찰일자'],
                    name=f'{ar} {gn}',
                    legendgroup=ar,
                    legendgrouptitle_text=ar,
                    marker_color=c,
                    text=['{:.2%}<br>({:,})</br>'.format(p, v) for p, v in zip((plot_df_11['학생수'] / plot_df_11['ISELZ_SUM']), plot_df_11['학생수'])],
                    ))
        else:
            fig11.add_trace(
                go.Bar(
                    y=plot_df_11['학생수'],
                    x=plot_df_11['개찰일자'],
                    name=f'{ar} {gn}',
                    legendgroup=ar,
                    legendgrouptitle_text=ar,
                    visible='legendonly',
                    marker_color=c,
                    text=['{:.2%}<br>({:,})</br>'.format(p, v) for p, v in zip((plot_df_11['학생수'] / plot_df_11['ISELZ_SUM']), plot_df_11['학생수'])],
                    ))
fig11.update_layout(
    paper_bgcolor='rgba(233,233,233,233)',
    plot_bgcolor='rgba(0,0,0,0)',
    height=800,
    title=f'{max(season_list)} 상권별 낙찰 점유율 변화 (주단위)',
    title_font_size=30,
    barmode='stack',
    font_size=16,
    legend=dict(
        grouptitlefont_size=13,
        font_size=12,
        orientation='h',
        # groupclick='toggleitem', # 개별토글 (더블클릭기능과 별개)
        ),
    # yaxis_tickformat = '%Y-%m-%d',
)
fig11.update_xaxes(
    tickmode = 'array',
    tickvals = plot_df_11['개찰일자'],
    tickformat='%Y-%m-%d',
    # title='개찰일자',
)
fig11.update_yaxes(tickformat=',d', title='학생수')



# fig12 = go.Figure()

# for ss in (df_sales_suju_graph3['시즌'].unique()):
#     for suhe in (df_sales_suju_graph3['구분'].unique()):
#         for bok in (df_sales_suju_graph3['복종명'].unique()):        
#             plot_df12 = df_sales_suju_graph3[(df_sales_suju_graph3['시즌']==ss) & (df_sales_suju_graph3['구분']==suhe) & (df_sales_suju_graph3['복종명']==bok)]
#             if ss == max(season_list):
#                 fig12.add_trace(
#                     go.Bar(
#                         x=plot_df12['복종명'],
#                         y=plot_df12['수량'],
#                         # color=suhe,
#                         name=f'{ss} {bok} {suhe}',
#                         legendgroup=f'{ss} {suhe}',
#                         legendgrouptitle_text=f'{ss} {suhe}',
#                         text=plot_df12['수량'],
#                         ))
#             else:
#                 fig12.add_trace(
#                     go.Bar(
#                         x=plot_df12['복종명'],
#                         y=plot_df12['수량'],
#                         # color=suhe,
#                         name=f'{ss} {bok} {suhe}',
#                         legendgroup=f'{ss} {suhe}',
#                         legendgrouptitle_text=f'{ss} {suhe}',
#                         text=plot_df12['수량'],
#                         marker_pattern_shape='+',
#                         ))
# fig12.update_yaxes(tickformat=',d')
# # fig12.update_yaxes(dividerwidth=5)
# fig12.update_layout(
#     paper_bgcolor='rgba(233,233,233,233)',
#     plot_bgcolor='rgba(0,0,0,0)',
#     # height=700,
#     width=1500,
#     barmode='group',
#     # bargap=0,
#     # bargroupgap=0.1,
#     title=f'< {max(season_list)}/{min(season_list)} 대표복종 수주현황>',
#     # title_font_size=30,
#     legend=dict(
#         # traceorder='normal', # legend 뒤집기
#         # groupclick='toggleitem' # 개별토글 (더블클릭기능과 별개)
#         ),
#     uniformtext_minsize=18,
#     uniformtext_mode='hide',
# )
# fig12.update_traces(texttemplate='%{text:,}')
# # fig12['layout']['yaxis']['autorange'] = 'reversed' # Y축 값 뒤집기



fig12 = go.Figure()

for bok in (df_sales_suju_graph3['복종명'].unique()):
    # plot_df12 = df_sales_suju_graph3[(df_sales_suju_graph3['시즌']==ss) & (df_sales_suju_graph3['구분']==suhe) & (df_sales_suju_graph3['복종명']==bok)]
    fig12.add_trace(
        go.Bar(
            x=df_sales_suju_graph3[(df_sales_suju_graph3['시즌']==max(season_list)) & (df_sales_suju_graph3['구분']=='해제량') & (df_sales_suju_graph3['복종명']==bok)]['복종명'],
            y=df_sales_suju_graph3[(df_sales_suju_graph3['시즌']==max(season_list)) & (df_sales_suju_graph3['구분']=='해제량') & (df_sales_suju_graph3['복종명']==bok)]['수량'],
            offset=-0.2,
            marker_color='#EF553B',
            name=f'{max(season_list)} {bok} 해제량',
            legendgroup=f'해제량',
            legendgrouptitle_text=f'해제량',
            text=df_sales_suju_graph3[(df_sales_suju_graph3['시즌']==max(season_list)) & (df_sales_suju_graph3['구분']=='해제량') & (df_sales_suju_graph3['복종명']==bok)]['수량'],
            ))
    fig12.add_trace(
        go.Bar(
            x=df_sales_suju_graph3[(df_sales_suju_graph3['시즌']==max(season_list)) & (df_sales_suju_graph3['구분']=='수주량') & (df_sales_suju_graph3['복종명']==bok)]['복종명'],
            y=df_sales_suju_graph3[(df_sales_suju_graph3['시즌']==max(season_list)) & (df_sales_suju_graph3['구분']=='수주량') & (df_sales_suju_graph3['복종명']==bok)]['수량'],
            offset=-0.1,
            marker_color='#636EFA',
            name=f'{max(season_list)} {bok} 수주량',
            legendgroup=f'수주량',
            legendgrouptitle_text=f'수주량',
            text=df_sales_suju_graph3[(df_sales_suju_graph3['시즌']==max(season_list)) & (df_sales_suju_graph3['구분']=='수주량') & (df_sales_suju_graph3['복종명']==bok)]['수량'],
            ))
    fig12.add_trace(
        go.Bar(
            x=df_sales_suju_graph3[(df_sales_suju_graph3['시즌']==min(season_list)) & (df_sales_suju_graph3['구분']=='수주량') & (df_sales_suju_graph3['복종명']==bok)]['복종명'],
            y=df_sales_suju_graph3[(df_sales_suju_graph3['시즌']==min(season_list)) & (df_sales_suju_graph3['구분']=='수주량') & (df_sales_suju_graph3['복종명']==bok)]['수량'],
            offset=0,
            marker_color='#636EFA',
            name=f'{min(season_list)} {bok} 수주량',
            legendgroup=f'수주량',
            legendgrouptitle_text=f'수주량',
            text=df_sales_suju_graph3[(df_sales_suju_graph3['시즌']==min(season_list)) & (df_sales_suju_graph3['구분']=='수주량') & (df_sales_suju_graph3['복종명']==bok)]['수량'],
            marker_pattern_shape='/',
            ))
    fig12.add_trace(
        go.Bar(
            x=df_sales_suju_graph3[(df_sales_suju_graph3['시즌']==min(season_list)) & (df_sales_suju_graph3['구분']=='해제량') & (df_sales_suju_graph3['복종명']==bok)]['복종명'],
            y=df_sales_suju_graph3[(df_sales_suju_graph3['시즌']==min(season_list)) & (df_sales_suju_graph3['구분']=='해제량') & (df_sales_suju_graph3['복종명']==bok)]['수량'],
            offset=0.1,
            marker_color='#EF553B',
            name=f'{min(season_list)} {bok} 해제량',
            legendgroup=f'해제량',
            legendgrouptitle_text=f'해제량',
            text=df_sales_suju_graph3[(df_sales_suju_graph3['시즌']==min(season_list)) & (df_sales_suju_graph3['구분']=='해제량') & (df_sales_suju_graph3['복종명']==bok)]['수량'],
            marker_pattern_shape='/',
            ))
fig12.update_xaxes(
    tickfont=dict(
        size=25,
    ),
    )
fig12.update_yaxes(
    tickformat=',d',
    # title='수량',
    # tickfont=dict(
    #     size=15,
    # ),
    )
fig12.update_layout(
    paper_bgcolor='rgba(233,233,233,233)',
    plot_bgcolor='rgba(0,0,0,0)',
    height=600,
    barmode='group',
    # bargap=0.1,
    # bargroupgap=0.1,
    title=f'{max(season_list)}/{min(season_list)} 수주량/해제량 (전체)',
    title_font_size=30,
    # font_size=18,
    legend=dict(
        # traceorder='grouped+reversed', # legend 뒤집기
        groupclick='toggleitem' # 개별토글 (더블클릭기능과 별개)
        ),
    uniformtext_minsize=8,
    uniformtext_mode='hide',
)
fig12.update_traces(
    texttemplate='%{text:,}',
    textposition='outside',
    width=0.1,
    ) # 바 두께 (0 ~ 1)\
# fig12['layout']['yaxis']['autorange'] = 'reversed' # Y축 값 뒤집기



# fig13 = px.area(
#     df_sales_bid_flow,
#     x='개찰일자',
#     y=(df_sales_bid_flow['학생수'] / df_sales_bid_flow['ISELZ_SUM'] * 100),
#     color='업체구분',
#     # line_group='특약명',
#     text=(df_sales_bid_flow['학생수'] / df_sales_bid_flow['ISELZ_SUM'] * 100).round(2).astype(str) + '%',
#     markers=True,
#     color_discrete_map=colors2,
#     facet_col='특약명',
#     facet_col_wrap=3,
#     )
# fig13.update_yaxes(title='점유율')
# fig13.update_xaxes(tickformat='%Y-%m-%d')
# fig13.update_layout(
#     paper_bgcolor='rgba(233,233,233,233)',
#     plot_bgcolor='rgba(0,0,0,0)',
#     height=800,
#     title=f'{max(season_list)} 상권별 낙찰 점유율 변화 (주단위)',
#     title_font_size=30,
#     hovermode='x unified',
#     # font_size=16,
#     # legend=dict(
#     #     orientation='h',
#     #     # groupclick='toggleitem', # 개별토글 (더블클릭기능과 별개)
#     #     x=0, y=0,
#     #     ),
#     # xaxis_tickformat = '%Y-%m-%d',
# )


# fig14 = go.Figure()

# for i, ar in enumerate(df_sales_bid_flow['특약명'].unique()):
#     for gn in (df_sales_bid_flow['업체구분'].unique()):
#         plot_df_11 = df_sales_bid_flow[ (df_sales_bid_flow['특약명']==ar) & (df_sales_bid_flow['업체구분']==gn)]
#         fig14.add_trace(
#             go.Bar(
#                 # x=(plot_df_11['학생수'] / plot_df_11['ISELZ_SUM'] * 100).round(1),
#                 x=plot_df_11['학생수'],
#                 y=plot_df_11['개찰일자'],
#                 name=f'{ar} {gn}',
#                 legendgroup=ar,
#                 legendgrouptitle_text=ar,
#                 # visible='legendonly',
#                 marker = {"colorscale": colors3,},
#                 # text=(plot_df_11['학생수'] / plot_df_11['ISELZ_SUM'] * 100).round(1).astype(str) + '%',
#                 # texttemplate='%{x}%'
#                 ))
# fig14.update_layout(
#     paper_bgcolor='rgba(233,233,233,233)',
#     plot_bgcolor='rgba(0,0,0,0)',
#     height=800,
#     title=f'{max(season_list)} 상권별 낙찰 점유율 변화 (주단위)',
#     title_font_size = 30,
#     font_size=16,
#     legend=dict(
#         orientation='h',
#         # groupclick='toggleitem', # 개별토글 (더블클릭기능과 별개)
#         x=0, y=0,
#         ),
#     # yaxis_tickformat = '%Y-%m-%d',
# )
# fig14.update_yaxes(
#     tickmode = 'array',
#     tickvals = plot_df_11['개찰일자'],
#     tickformat='%Y-%m-%d',
# )
# # fig14['layout']['yaxis']['autorange'] = 'reversed' # Y축 값 뒤집기


# 투찰율 전체 그래프
fig15 = px.scatter(
    df_bid_rate_graph,
    x='개찰일자',
    y='투찰율',
    color='업체명',
    # symbol='업체명',
    color_discrete_map=colors2,
    # size='학생수',
    marginal_x='histogram',
    marginal_y='rug',
    hover_data = [ '특약명', '학교명' ],
    # size_max=30,
    opacity=0.7,
    # facet_col='특약명',
    # facet_col_wrap=2,
    )
fig15.update_traces(
    marker=dict(
        size=12,
        line=dict(
            width=1,
            color='DarkSlateGrey')
        ),
    selector=dict(mode='markers')
    )
fig15.update_layout(
    paper_bgcolor='rgba(233,233,233,233)',
    plot_bgcolor='rgba(0,0,0,0)',
    height=800,
    yaxis_range=[30, 110],
    # xaxis_range=[
    #     (datetime.today() - timedelta(days=70)).strftime('%Y-%m-%d'), # 7일전
    #     datetime.today().strftime('%Y-%m-%d') # 오늘
    #     ],
    title=f'{max(season_list)} 업체별 낙찰건 투찰율 산점도',
    title_font_size = 30,
    )
fig15.update_xaxes(tickformat='%Y-%m-%d')


fig16 = px.scatter(
    df_bid_rate_graph,
    x='개찰일자',
    y='투찰율',
    color='업체명',
    # symbol='업체명',
    color_discrete_map=colors2,
    # size='학생수',
    # marginal_x='histogram',
    # marginal_y='rug',
    hover_data = [ '특약명', '학교명' ],
    # size_max=30,
    opacity=0.7,
    facet_col='특약명',
    facet_col_wrap=2,
    facet_col_spacing=0.1,
    )
fig16.update_traces(
    marker=dict(
        size=20,
        symbol='diamond-wide',
        # symbol='x',
        # line=dict(
        #     width=2,
        #     color='DarkSlateGrey')
        ),
    selector=dict(mode='markers')
    )
fig16.update_layout(
    paper_bgcolor='rgba(233,233,233,233)',
    plot_bgcolor='rgba(0,0,0,0)',
    height=800,
    yaxis_range=[30, 110],
    xaxis_range=[
        (datetime.today() - timedelta(days=10)).strftime('%Y-%m-%d'), # 7일전
        datetime.today().strftime('%Y-%m-%d') # 오늘
        ],
    title=f'{max(season_list)} 업체별 낙찰건 투찰율 산점도 (상권별, 기간: 10일전 ~ 오늘)',
    title_font_size = 30,
    # hovermode='x unified',
    )
fig16.update_xaxes(tickformat='%Y-%m-%d')



# go.pie 그래프 시작
cust_list = list(df_bid_rate_graph['업체명'].unique())
pie_xpos = [0.08, 0.28, 0.5, 0.72, 0.92] # pie chart x 간격

fig17 = make_subplots(
    1, 5,
    specs=[[{'type':'domain'}, {'type':'domain'}, {'type':'domain'}, {'type':'domain'}, {'type':'domain'}],],
    subplot_titles=cust_list,
    horizontal_spacing=0,
    )
for i, gn in enumerate(cust_list):
    plot_df_17 = df_bid_rate.reset_index()
    plot_df_17 = plot_df_17[['구간', gn]]
    fig17.add_trace(
        go.Pie(
            labels=plot_df_17['구간'],
            values=plot_df_17[gn],
            # scalegroup='one',
            pull=[0, 0.05, 0.1, 0.15, 0.2, 0.25],
            name=gn,
            hole=.4,
            sort=False,
            ), 1, i+1)
    fig17.add_annotation(
        xref='paper',
        yref='paper',
        x=pie_xpos[i],
        y=0.5,
        # bgcolor=colors3[i],
        text=str(format(plot_df_17[gn].sum(), ',')),
        font_size=20,
        align='center',
        showarrow=False
        )

fig17.update_traces(textposition='inside', textinfo='percent', textfont_size=20,)
fig17.update_layout(
    paper_bgcolor='rgba(233,233,233,233)',
    plot_bgcolor='rgba(0,0,0,0)',
    height=450,
    title=f'{max(season_list)} 업체별 투찰율 구성 비율 (전국)',
    title_font_size=30,
    uniformtext_minsize=25,
    # uniformtext_mode='hide',
    )



# -------------------- 메인페이지 (영업팀) --------------------

st.markdown('#### 영업팀 주간업무 보고')
st.markdown(f"주요업무 ({mod.this_mon} ~ {mod.this_fri})")


# -------------------- 탭 (영업팀) --------------------

EXAMPLE_NO = 3


def streamlit_menu(example=1):
    if example == 1:
        # 1. as sidebar menu
        with st.sidebar:
            selected = option_menu(
                menu_title="Main Menu",  # required
                options=['시즌추이', '수주현황', '상권별수주', '낙찰현황', '낙찰추이', '투찰율'],  # required
                icons=['graph-up-arrow', 'stack', 'diagram-3-fill', 'bell-fill', 'bar-chart-line-fill', 'tag-fill'],  # optional
                menu_icon="cast",  # optional
                default_index=0,  # optional
            )
        return selected

    if example == 2:
        # 2. horizontal menu w/o custom style
        selected = option_menu(
            menu_title=None,  # required
            options=['시즌추이', '수주현황', '상권별수주', '낙찰현황', '낙찰추이', '투찰율'],  # required
            icons=['graph-up-arrow', 'stack', 'diagram-3-fill', 'bell-fill', 'bar-chart-line-fill', 'tag-fill'],  # optional
            menu_icon="cast",  # optional
            default_index=0,  # optional
            orientation="horizontal",
        )
        return selected

    if example == 3:
        # 2. horizontal menu with custom style
        selected = option_menu(
            menu_title=None,  # required
            options=['시즌추이', '수주현황', '상권별수주', '낙찰현황', '낙찰추이', '투찰율'],  # required
            icons=['graph-up-arrow', 'stack', 'diagram-3-fill', 'bell-fill', 'bar-chart-line-fill', 'tag-fill'],  # optional
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

if selected == "시즌추이":
    # st.markdown(f'##### {season_list[1]}/{season_list[0]} 수주량, 해제량 시즌 비교')
    st.plotly_chart(fig1, use_container_width=True, theme=None)
    # st.dataframe(df_sales)
    # st.write(df_sales['시즌'].unique())
    
    with st.expander('주단위 실데이터, 일일보고 기반 (클릭해서 열기)'):
        st.markdown('##### 상권별 수주량, 해제량 시즌 비교')
        st.dataframe(df_sales, use_container_width=True)

    st.plotly_chart(fig1_1, use_container_width=True, theme=None)
    with st.expander('주단위 실데이터, 일일보고 기반 (클릭해서 열기)'):
        st.markdown('##### 통합 수주량, 해제량 시즌 비교')
        st.dataframe(df_sales_total_sum, use_container_width=True)

if selected == "수주현황":
    suju_sum = int(df_sales_suju['수주량'].sum())
    suju_diff_sum = int(df_sales_suju['전년비증감(수주)'].sum())
    haje_sum = int(df_sales_suju['해제량'].sum())
    haje_diff_sum = int(df_sales_suju['전년비증감(해제)'].sum())

    tot_j_qty = int(df_sales_suju['전년최종'].sum())

    st.markdown('##### 주간 현황판')
    column_1, column_2, column_3 = st.columns(3)  
    with column_1:
        st.metric(f'{max(season_list)} 총 수주량', f'{suju_sum:,}', delta=f'{suju_diff_sum:,} (전년동기비)', delta_color="normal", help='자켓 + 후드')
    with column_2:
        st.metric(f'{max(season_list)} 총 해제량', f'{haje_sum:,}', delta=f'{haje_diff_sum:,} (전년동기비)', delta_color="normal", help='자켓 + 후드')
    with column_3:
        st.metric('전년 최종', f'{tot_j_qty:,}', delta=None, delta_color="normal", help='자켓 + 후드')

    st.markdown('''---''')

    st.markdown('##### 수주현황')
    st.dataframe(df_sales_suju, use_container_width=True)
    # st.dataframe(df_sales_suju)
    st.plotly_chart(fig12, use_container_width=True, theme=None)
    # st.plotly_chart(fig12)

    # st.markdown('''---''')
    # st.dataframe(df_sales_suju, use_container_width=True)

    # left_column, right_column = st.columns(2)
    # left_column.plotly_chart(fig6, use_container_width=True, theme=None)
    # left_column.dataframe(df_sales_suju_graph, use_container_width=True)
    # right_column.plotly_chart(fig5, use_container_width=True, theme=None)
    # right_column.dataframe(df_sales_suju_graph2, use_container_width=True)
    # st.dataframe(df_sales_suju)
    


    # # 월간 / 주간 계획
    # st.write('##### 23년 동복 월간계획 (10月)')
    # plan_data = {
    #     '구분': ['월간', '주간'],
    #     '수주계획': [50000, 10000],
    #     '수주실적': [29940, 11676],
    #     '수주계획(%)': [0, 0],
    #     '해제계획': [32000, 7000],
    #     '해제실적': [16566, 7544],
    #     '해제계획(%)': [0, 0],
    #     }
    # df_plan = pd.DataFrame(plan_data).set_index('구분')
    # df_plan['수주계획(%)'] = df_plan['수주실적'] / df_plan['수주계획']
    # df_plan['해제계획(%)'] = df_plan['해제실적'] / df_plan['해제계획']
    # df_plan = df_plan.style.format({
    #     '수주계획(%)': '{:,.0%}'.format,
    #     '해제계획(%)': '{:,.0%}'.format,
    #     })
    # st.dataframe(df_plan, use_container_width=True)

    # fig21 = px.pie(df_plan,
    #             values='수주계획(%)',
    #             names=df_plan.index,
    #             # color='업체구분',
    #             # # title=f'{max(season_list)}',
    #             # # text='학생수',
    #             # height=700,
    #             # facet_col='특약명',
    #             # facet_col_wrap=3,
    #             # markers=True,
    #             # color_discrete_map=colors2,
    #             )
    # fig21.update_traces(
    #     textposition='top right',
    #     texttemplate='%{text:,}',
    #     # textfont_size=14,
    #     )
    # fig21.update_layout(
    #     paper_bgcolor='rgba(233,233,233,233)', plot_bgcolor='rgba(0,0,0,0)',
    #     # uniformtext=dict(minsize=10, mode='hide'),
    # )
    # fig21.update_xaxes(tickformat='%Y-%m-%d')
    # fig21.update_yaxes(tickformat=',d')

    # st.plotly_chart(fig21, theme=None)



if selected == "상권별수주":
    st.markdown('##### 상권별수주')
    st.dataframe(df_sales_suju_tkyk, use_container_width=True)
    # st.markdown('''---''')
    # st.dataframe(df_sales_suju_tkyk_graph, use_container_width=True)  
    
    # left_column, right_column = st.columns(2)
    # left_column.plotly_chart(fig8, use_container_width=True, theme=None)
    # left_column.dataframe(df_sales_suju_tkyk_graph, use_container_width=True)
    # right_column.plotly_chart(fig7, use_container_width=True, theme=None)
    # right_column.dataframe(df_sales_suju_tkyk_graph2, use_container_width=True)
    st.plotly_chart(fig7_1, use_container_width=True, theme=None)
    # st.plotly_chart(fig7_1, theme=None)
    

if selected == "낙찰현황":
    st.markdown('##### 주간 현황판')

    bid_qty_sum = (((df_sales_base_bid['i_qty'].sum() +\
                    df_sales_base_bid['s_qty'].sum() +\
                    df_sales_base_bid['e_qty'].sum() +\
                    df_sales_base_bid['l_qty'].sum() +\
                    df_sales_base_bid['etc_qty'].sum()) / df_sales_base_bid['j_i_qty_tot'].sum())*100).round(2)
    bid_qty_sum_j = (((df_sales_base_bid_j['i_qty'].sum() +\
                    df_sales_base_bid_j['s_qty'].sum() +\
                    df_sales_base_bid_j['e_qty'].sum() +\
                    df_sales_base_bid_j['l_qty'].sum() +\
                    df_sales_base_bid_j['etc_qty'].sum()) / df_sales_base_bid_j['j_i_qty_tot'].sum())*100).round(2)

    tkyk_list = df_sales_base_bid['tkyk_name'].to_list()

    bid_qty0_sum = ((df_sales_base_bid.iloc[0, 8:13].sum() / df_sales_base_bid.iloc[0]['j_i_qty_tot'].sum())*100).round(1)
    bid_qty1_sum = ((df_sales_base_bid.iloc[1, 8:13].sum() / df_sales_base_bid.iloc[1]['j_i_qty_tot'].sum())*100).round(1)
    bid_qty2_sum = ((df_sales_base_bid.iloc[2, 8:13].sum() / df_sales_base_bid.iloc[2]['j_i_qty_tot'].sum())*100).round(1)
    bid_qty3_sum = ((df_sales_base_bid.iloc[3, 8:13].sum() / df_sales_base_bid.iloc[3]['j_i_qty_tot'].sum())*100).round(1)
    bid_qty4_sum = ((df_sales_base_bid.iloc[4, 8:13].sum() / df_sales_base_bid.iloc[4]['j_i_qty_tot'].sum())*100).round(1)
    bid_qty5_sum = ((df_sales_base_bid.iloc[5, 8:13].sum() / df_sales_base_bid.iloc[5]['j_i_qty_tot'].sum())*100).round(1)
    bid_qty0_sum_j = ((df_sales_base_bid_j.iloc[0, 8:13].sum() / df_sales_base_bid_j.iloc[0]['j_i_qty_tot'].sum())*100).round(1)
    bid_qty1_sum_j = ((df_sales_base_bid_j.iloc[1, 8:13].sum() / df_sales_base_bid_j.iloc[1]['j_i_qty_tot'].sum())*100).round(1)
    bid_qty2_sum_j = ((df_sales_base_bid_j.iloc[2, 8:13].sum() / df_sales_base_bid_j.iloc[2]['j_i_qty_tot'].sum())*100).round(1)
    bid_qty3_sum_j = ((df_sales_base_bid_j.iloc[3, 8:13].sum() / df_sales_base_bid_j.iloc[3]['j_i_qty_tot'].sum())*100).round(1)
    bid_qty4_sum_j = ((df_sales_base_bid_j.iloc[4, 8:13].sum() / df_sales_base_bid_j.iloc[4]['j_i_qty_tot'].sum())*100).round(1)
    bid_qty5_sum_j = ((df_sales_base_bid_j.iloc[5, 8:13].sum() / df_sales_base_bid_j.iloc[5]['j_i_qty_tot'].sum())*100).round(1)

    this_year_cnt_sum = df_sales_base_bid.iloc[:, 3:8].sum().sum()
    this_year_qty_sum = df_sales_base_bid.iloc[:, 8:13].sum().sum()
    last_year_cnt_sum = df_sales_base_bid.iloc[:, -2].sum()
    last_year_qty_sum = df_sales_base_bid.iloc[:, -1].sum()

    # st.write(this_year_cnt_sum)
    column_1, column_2, column_3, column_4, column_5, column_6, column_7 = st.columns(7)  
    with column_1:
        st.metric(f'{max(season_list)} 총 진행률', str(bid_qty_sum)+'%', delta=f'{(bid_qty_sum - bid_qty_sum_j).round(1)}%'+' (전주대비)', delta_color="normal", help=f'지난주 진행률 : {bid_qty_sum_j.round(1)}%')
    with column_2:
        st.metric(f'{tkyk_list[0]} 진행률', str(bid_qty0_sum)+'%', delta=f'{(bid_qty0_sum - bid_qty0_sum_j).round(1)}%'+' (전주대비)', delta_color="normal", help=f'지난주 진행률 : {bid_qty0_sum_j.round(1)}%')
    with column_3:
        st.metric(f'{tkyk_list[1]} 진행률', str(bid_qty1_sum)+'%', delta=f'{(bid_qty1_sum - bid_qty1_sum_j).round(1)}%'+' (전주대비)', delta_color="normal", help=f'지난주 진행률 : {bid_qty1_sum_j.round(1)}%')
    with column_4:
        st.metric(f'{tkyk_list[2]} 진행률', str(bid_qty2_sum)+'%', delta=f'{(bid_qty2_sum - bid_qty2_sum_j).round(1)}%'+' (전주대비)', delta_color="normal", help=f'지난주 진행률 : {bid_qty2_sum_j.round(1)}%')
    with column_5:
        st.metric(f'{tkyk_list[3]} 진행률', str(bid_qty3_sum)+'%', delta=f'{(bid_qty3_sum - bid_qty3_sum_j).round(1)}%'+' (전주대비)', delta_color="normal", help=f'지난주 진행률 : {bid_qty3_sum_j.round(1)}%')
    with column_6:
        st.metric(f'{tkyk_list[4]} 진행률', str(bid_qty4_sum)+'%', delta=f'{(bid_qty4_sum - bid_qty4_sum_j).round(1)}%'+' (전주대비)', delta_color="normal", help=f'지난주 진행률 : {bid_qty4_sum_j.round(1)}%')
    with column_7:
        st.metric(f'{tkyk_list[-1]} 진행률', str(bid_qty5_sum)+'%', delta=f'{(bid_qty5_sum - bid_qty5_sum_j).round(1)}%'+' (전주대비)', delta_color="normal", help=f'지난주 진행률 : {bid_qty5_sum_j.round(1)}%')
    
    st.markdown('''---''')

    st.markdown(f'##### {max(season_list)}/{min(season_list)} 주관구매 낙찰현황')

    # st.dataframe(df_sales_base_bid)

    left_column, right_column_1, right_column_2 = st.columns([2, 1, 1])
    left_column.dataframe(make_bid_data2(df_sales_bid, df_sales_bid_j, season_list), use_container_width=True) # 연간 차이
    right_column_1.metric(f'{max(season_list)} 낙찰된 학교수 (개교)', f'{this_year_cnt_sum:,}', delta=f'{(this_year_cnt_sum - last_year_cnt_sum):,} (전년최종대비)', delta_color="normal", help=None)
    right_column_2.metric(f'{max(season_list)} 낙찰된 학생수 (명)', f'{this_year_qty_sum:,}', delta=f'{(this_year_qty_sum - last_year_qty_sum):,} (전년최종대비)', delta_color="normal", help=None)
    right_column_1.metric(f'{min(season_list)} 최종 학교수 (개교)', f'{last_year_cnt_sum:,}', delta=None, delta_color="normal", help=None)
    right_column_2.metric(f'{min(season_list)} 최종 학생수 (명)', f'{last_year_qty_sum:,}', delta=None, delta_color="normal", help=None)
    
    
    
    left_column, right_column = st.columns(2)
    left_column.markdown(f'##### {max(season_list)} 주관구매 낙찰현황 (상권)')
    left_column.dataframe(df_bid_tkyk_1, use_container_width=True)
    right_column.markdown(f'##### {min(season_list)} 주관구매 낙찰현황 (상권)')
    right_column.dataframe(df_bid_tkyk_2, use_container_width=True)
    
    
    left_column.markdown(f'##### {max(season_list)} - {min(season_list)} (차이)')
    
    df_minus = df_bid_tkyk_1 - df_bid_tkyk_2 # 차이 DataFrame
    df_minus_school = df_minus.iloc[:, :5].copy()
    df_minus_school.loc['업체별 합계'] = df_minus_school.sum() # 합계행 추가
    df_minus_school['학교수 합계'] = df_minus_school.sum(axis=1) # 합계열 추가
    
    df_minus_student = df_minus.iloc[:, 5:10].copy()
    df_minus_student.loc['업체별 합계'] = df_minus_student.sum() # 합계행 추가
    df_minus_student['학생수 합계'] = df_minus_student.sum(axis=1) # 합계열 추가


    left_column, right_column = st.columns(2)
    left_column.dataframe(df_minus_school, use_container_width=True)
    right_column.dataframe(df_minus_student, use_container_width=True)
    

    left_column, right_column = st.columns(2)
    
    # 히트맵1 (학교수)
    fig_minus1 = px.imshow(
        df_minus.iloc[:, :5],
        text_auto=True,
        # height=400,
        )
    fig_minus1.update_xaxes(side='top')

    # 히트맵2 (학생수)
    fig_minus2 = px.imshow(
        df_minus.iloc[:, 5:10],
        text_auto=True,
        # height=400,
        )
    fig_minus2.update_xaxes(side='top')
    
    left_column.plotly_chart(fig_minus1, theme=None)
    right_column.plotly_chart(fig_minus2, theme=None)


    st.plotly_chart(fig4, use_container_width=True, theme=None)
    # st.dataframe(df_sales_bid_graph.groupby(['시즌', '업체구분', '특약명'])[['학생수']].agg(sum)['학생수'])
    # st.write(df_sales_bid_graph[(df_sales_bid_graph['시즌']==max(season_list)) & (df_sales_bid_graph['업체구분']=='아이비클럽') & (df_sales_bid_graph['특약명']=='서울상권')]['학생수'].agg(sum))
    # st.dataframe(df_sales_bid_graph)
    
    
    # left_column, right_column = st.columns(2)
    # left_column.caption('[시즌 -> 업체 -> 상권]')
    # left_column.plotly_chart(fig2, use_container_width=True, theme=None)
    # right_column.caption('[업체 -> 상권 -> 시즌]')
    # right_column.plotly_chart(fig3, use_container_width=True, theme=None)


if selected == "낙찰추이":
    # st.warning('아직 공사중인 페이지입니다...')

    # st.dataframe(make_bid_data2(df_sales_bid, df_sales_bid_j, season_list))
    # st.dataframe(df_sales_bid)
    # st.dataframe(df_sales_bid_j)

    # st.dataframe(df_sales_base_bid)
    # td = datetime.today().strftime("%Y-%m-%d")
    # st.dataframe(mod.select_data(make_sql3(max(season_list), td)).sort_values('sort').reset_index(drop=True))
    # st.dataframe(mod.select_data(make_sql3(max(season_list), td)))
    # st.dataframe(make_bid_data3(mod.select_data(make_sql3(max(season_list), td)),td))
    # st.dataframe(make_bid_data4(max(season_list)))
    
    
    # st.write(f'##### {max(season_list)} 상권별 4사 낙찰추이')
    st.plotly_chart(fig9, use_container_width=True, theme=None)
    
    # st.write(f'##### {max(season_list)} 상권별 낙찰추이 (상세)')
    st.plotly_chart(fig10, use_container_width=True, theme=None)

    # st.write(f'##### {max(season_list)} 상권별 낙찰 점유율 추이')
    st.plotly_chart(fig11, use_container_width=True, theme=None)

    with st.expander('주단위 실데이터 (클릭해서 열기)'):
        st.dataframe(df_sales_bid_flow, use_container_width=True)

    # st.plotly_chart(fig13, use_container_width=True, theme=None)


if selected == "투찰율":

    st.write(f'##### {max(season_list)} 업체별 투찰율 구성 비율 (전국)')
    left_column, right_column = st.columns(2)
    left_column.dataframe(df_bid_rate, use_container_width=True)
    right_column.write('''###### 투찰율이란?
        낙찰 가능한 최저가격을 결정하는 백분율
    ''')
    right_column.latex('투찰율 = 입찰가 / 예정가 * 100')

    st.plotly_chart(fig17, use_container_width=True, theme=None) # 전체 pie
    # st.plotly_chart(fig15, use_container_width=True, theme=None) # 전체 산점도
    st.plotly_chart(fig16, use_container_width=True, theme=None) # 상권별 10일간 산점도
    with st.expander('실데이터 (클릭해서 열기)'):
        st.dataframe(df_bid_rate_graph, use_container_width=True)


    # 상권별 투찰율
    # st.dataframe(df_bid_rate_graph, use_container_width=True)

    for ar in (df_bid_rate_graph['특약명'].unique()):
        plot_df_tkyk = df_bid_rate_graph[
            (df_bid_rate_graph['특약명']==ar)
            # & (df_bid_rate_graph['개찰일자'].isin(pd.date_range((datetime.today() - timedelta(days=14)).strftime('%Y-%m-%d'), datetime.today().strftime('%Y-%m-%d'))))
            ]

        df_tk = make_bid_data6(df_bid_rate_graph[df_bid_rate_graph['특약명']==ar]) # 특약별 투찰율 표


        # go.pie 그래프 시작
        labels = list(df_bid_rate_graph['특약명'].unique())
        cust_list = list(df_bid_rate_graph['업체명'].unique())
        # pie_xpos = [0.08, 0.28, 0.5, 0.72, 0.92] # pie chart x 간격

        fig_tkyk = make_subplots(
            1, 5,
            specs=[[{'type':'domain'}, {'type':'domain'}, {'type':'domain'}, {'type':'domain'}, {'type':'domain'}],],
            subplot_titles=cust_list,
            horizontal_spacing=0,
            )
        for i, gn in enumerate(cust_list):
            plot_df_tkyk_pie = df_tk.reset_index()
            plot_df_tkyk_pie = plot_df_tkyk_pie[['구간', gn]]
            fig_tkyk.add_trace(
                go.Pie(
                    labels=plot_df_tkyk_pie['구간'],
                    values=plot_df_tkyk_pie[gn],
                    # scalegroup='one',
                    pull=[0, 0.05, 0.1, 0.15, 0.2, 0.25],
                    name=gn,
                    hole=.4,
                    sort=False,
                    ), 1, i+1)
            fig_tkyk.add_annotation(
                xref='paper',
                yref='paper',
                x=pie_xpos[i],
                y=0.5,
                # bgcolor=colors3[i],
                text=str(format(plot_df_tkyk_pie[gn].sum(), ',')),
                font_size=20,
                align='center',
                showarrow=False
                )

        fig_tkyk.update_traces(textposition='inside', textinfo='percent', textfont_size=20,)
        fig_tkyk.update_layout(
            paper_bgcolor='rgba(233,233,233,233)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=450,
            title=f'{max(season_list)} 업체별 투찰율 구성 비율 ({ar})',
            title_font_size=30,
            uniformtext_minsize=25,
            # uniformtext_mode='hide',
            )


        # fig_tkyk1 = px.pie(
        #     plot_df_tkyk,
        #     values='학생수',
        #     names='구간',
        #     # color_discrete_sequence=px.colors.sequential.RdBu,
        #     facet_col='업체명',
        #     hole=.3,
        # )
        # fig_tkyk1.update_traces(textposition='inside', textinfo='percent+label')
        # fig_tkyk1.update_layout(
        #     paper_bgcolor='rgba(233,233,233,233)',
        #     plot_bgcolor='rgba(0,0,0,0)',
        #     height=400,
        #     title=f'{max(season_list)} 업체별 투찰율 구성 비율 ({ar})',
        #     title_font_size=30,
        #     )


        # fig_tkyk2 = px.scatter(
        #     plot_df_tkyk,
        #     x='개찰일자',
        #     y='투찰율',
        #     color='업체명',
        #     # symbol='업체명',
        #     color_discrete_map=colors2,
        #     # size='학생수',
        #     marginal_x='histogram',
        #     marginal_y='rug',
        #     hover_data = [ '특약명', '학교명' ],
        #     # size_max=30,
        #     opacity=0.7,
        #     # facet_col='특약명',
        #     # facet_col_wrap=2,
        #     )
        # fig_tkyk2.update_traces(
        #     marker=dict(
        #         size=12,
        #         line=dict(
        #             width=1,
        #             color='DarkSlateGrey')
        #         ),
        #     selector=dict(mode='markers')
        #     )
        # fig_tkyk2.update_layout(
        #     paper_bgcolor='rgba(233,233,233,233)',
        #     plot_bgcolor='rgba(0,0,0,0)',
        #     height=600,
        #     yaxis_range=[30, 110],
        #     # xaxis_range=[
        #     #     (datetime.today() - timedelta(days=14)).strftime('%Y-%m-%d'), # 7일전
        #     #     datetime.today().strftime('%Y-%m-%d') # 오늘
        #     #     ],
        #     title=f'{max(season_list)} 업체별 낙찰건 투찰율 산점도 ({ar})',
        #     title_font_size = 30,
        #     )
        # fig_tkyk2.update_xaxes(tickformat='%Y-%m-%d')


        st.write(f'###### 업체별 투찰율 구성 비율 ({ar})')
        st.dataframe(df_tk, use_container_width=True)

        st.plotly_chart(fig_tkyk, use_container_width=True, theme=None)
        # st.plotly_chart(fig_tkyk1, use_container_width=True, theme=None)
        # st.plotly_chart(fig_tkyk2, use_container_width=True, theme=None)
        st.write('''---''')




# ---------- 주요업무(텍스트) ----------

tab1, tab2 = st.tabs(['.', '.'])
with tab1:
    try:
        sel_text = mod.select_text(mod.db_file, datetime.strptime(mod.this_fri, '%Y/%m/%d').isocalendar()[1], '영업팀', 'text1')
    except IndexError:
        sel_text = ''

    st.markdown(sel_text)

    # 이번주만 추가
    # raw_data = {
    #     '품목': ['아이비클럽', '스마트', '엘리트', '스쿨룩스'],
    #     '대(64,200)': ['900', '520', '800', '600'],
    #     '중(13,200)': ['850', '490', 'X', '410'],
    #     '소(17,000)': ['800', 'X', 'X', 'X'],
    #     '세로형(24,300)': ['900', 'X', '600', '470'],
    #     '부직포(22,600)': ['1600', '', '', '590'],
    #     '체육복백(1,500)': ['1200', '', '', '640'],
    #     '비닐백(38,500)': ['170', '190', '', '60'],
    #     '비닐백(대)(31,000)': ['300', '310', '', '160'],
    #     }
    # df_bag = pd.DataFrame(raw_data).set_index('품목').T
    # st.dataframe(df_bag, use_container_width=True)

    # st.markdown('''##### □ 23N/S 주관구매 낙찰학교 수주 및 홀드해제 진행''')
    # st.markdown('''##### □ 홈페이지 매장찾기 자료 업데이트 취합 (10/21)''')
    # left_column, right_column = st.columns(2)
    # left_column.image('./data/image/bag1.jpg')
    # right_column.image('./data/image/bag2.jpg')
    # st.image('./data/image/table1.png')
    # st.markdown('''
    # ###### 
    #     - 조례 제정안 시행연도인 2023년부터 2026년까지 4년
    #     - 연도별 단가는 전년도 권고가격에 소비자 물가 상승률 1.7% 적용
    #     - 경남 중학생 7만원, 고등학생 8만원(현금), 부산 중/고 신입생 6만원(현물)
    # ''')


with tab2:
    # 입력파트
    sales_text = st.text_area('이번 주 내용을 입력하세요.', sel_text)
    st.write('입력된 내용 : \n', sales_text)
    
    mod.insert_text(mod.db_file, datetime.strptime(mod.this_fri, '%Y/%m/%d').isocalendar()[1], '영업팀', sales_text, 'text1')


# -------------------- HIDE STREAMLIT STYLE --------------------
hide_st_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """
st.markdown(hide_st_style, unsafe_allow_html=True)