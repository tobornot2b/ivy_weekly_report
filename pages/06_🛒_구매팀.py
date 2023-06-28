import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from data import * # 패키지 불러오기
from data.mod import cp949_to_utf8_in_us7ascii


# emojis: https://www.webfx.com//tools/emoji-cheat-sheet/
st.set_page_config(
    page_title='주간업무보고',
    page_icon=":chart_with_upwards_trend:",
    layout="wide"
)


# -------------------- 함수 (구매팀) --------------------

# SQL문 작성 함수
@st.cache_data
def make_sql(F_season: str, S_season: str, jaepum: str) -> str:
    sql_1 = f'''
    SELECT Max(s.sub_sojae_saib_gb),
        Max(To_char(s.sub_buking_cnt)),
        utl_raw.Cast_to_raw(Max(s.sub_cf_ref)),
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
        utl_raw.Cast_to_raw(Max(tkyk_name)),
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
        utl_raw.Cast_to_raw(Max(s.sub_cf_ref)),
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
        utl_raw.Cast_to_raw(Max(tkyk_name)),
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
@st.cache_data
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

    # 한글 변환
    df1["참조"] = df1["참조"].apply(cp949_to_utf8_in_us7ascii)
    df1["사입처"] = df1["사입처"].apply(cp949_to_utf8_in_us7ascii)
    df2["참조"] = df2["참조"].apply(cp949_to_utf8_in_us7ascii)
    df2["사입처"] = df2["사입처"].apply(cp949_to_utf8_in_us7ascii)

    # 타입변환 (이 부분은 이 전단계에서 해도 되나 공통함수 건드리기 싫음)
    df2['당초발주'] = df2['당초발주'].astype('float')
    df2['입고량'] = df2['입고량'].astype('float')

    df = pd.concat([df1, df2])

    return df


# CPC 분류에 쓰이는 SQL문
# soje_cpc_sql = f'''
# SELECT cod_code,
#        utl_raw.Cast_to_raw(cod_name) cod_name,
#        utl_raw.Cast_to_raw(cod_etc) cod_etc
# FROM   i_cod_t
# WHERE  cod_gbn_code = '36'
#        AND del_yn = 'Y'
# ORDER  BY sort, cod_name 
# '''


# 품종 분류에 쓰이는 데이터프레임 (merge용)
soje_kind = {
    '품종코드' : ['E', 'F', 'T', 'V', 'W', 'X', 'Y', 'Z'],
    '품종' : ['생활복', '체육복', '타소재', '방모', '소모', 'COAT', '편사', '기타']
}
df_soje_kind = pd.DataFrame(soje_kind) # 원단 구분


# 전처리 함수2 : 분류기준 머지, 분류용 컬럼 생성
@st.cache_data
def data_preprocess2(df1:pd.DataFrame, df2:pd.DataFrame, season: str, jaepum: str) -> pd.DataFrame:
    df_temp = df1.merge(df2, how='left', left_on='CPC', right_on='cod_code')
    df = df_temp.merge(df_soje_kind, how='left')

    df['제품'] = df['cod_etc'].str[:3]
    df['미입고량'] = df['변경발주'] - df['입고량']

    df['납기월'] = df['납기일'].str[:7]
    # df['납기월'] = df['납기일'].dt.to_period(freq = 'M')   # 연월까지

    df['업체출고예정일'] = pd.to_datetime(df['업체출고예정일'], errors='coerce') # 날짜형식으로 변환, 에러는 NaT으로
    df['최초발주'] = pd.to_datetime(df['최초발주'], errors='coerce')
    df['최종발주'] = pd.to_datetime(df['최종발주'], errors='coerce')
    df['납기일'] = pd.to_datetime(df['납기일'], errors='coerce')
    df['최초입고'] = pd.to_datetime(df['최초입고'], errors='coerce')
    df['최종입고'] = pd.to_datetime(df['최종입고'], errors='coerce')
    


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
@st.cache_data
def data_preprocess3(df:pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={'변경발주': '발주량'})

    # int 와 float 연산에러 때문에 넣음
    df['발주량'] = df['발주량'].astype(float)
    df['입고량'] = df['입고량'].astype(float)
    df['미입고량'] = df['미입고량'].astype(float)

    df_total = df.groupby(['발주시즌', '구분'])[['발주량', '입고량', '미입고량']].agg(sum)

    df_total['입고율'] = df_total['입고량'] / df_total['발주량'] * 100 # float 강제형변환이 없으면 발주량 컬럼이 int일 경우가 있는데 여기서 연산에러 발생
    # df_total['입고율'] = df_total['입고량'].div(df_total['발주량']) * 100
    df_total = df_total.fillna(0) # NaN 값이 있으면 0으로 채움
    df_total = df_total.round(0).astype(int)
    df_total['입고율'] = df_total['입고율'].astype(str) + '%'
    df_total = df_total.reset_index(drop=False)

    df_total_sum = df.groupby(['발주시즌'])[['발주량', '입고량', '미입고량']].agg(sum).round(0).astype(int).reset_index(drop=False) # 합계

    # 월별
    # df_month = df.pivot_table(['발주량', '입고량', '미입고량'], index=['납기월'], columns=['구분'], aggfunc='sum') # 멀티인덱스 (컬럼도 멀티가 가능하다)
    # # df_month = df_month.stack(level=[0, 1]).reset_index().set_index('납기월')
    # df_month = df_month.stack(level=[0, 1]).reset_index()
    # df_month.columns = ['납기월', '구분', '원단종류', '원단량']
    # df_month['원단량'] = df_month['원단량'].round(0).astype(int).copy()

    return df_total, df_total_sum


# 전처리 함수4 : 시각화용 melt, 미입고량 음수처리 (Icicle 차트는 음수 넣으면 에러남)
@st.cache_data
def data_preprocess4(df1: pd.DataFrame) -> pd.DataFrame:
    df1 = df1.drop('발주량', axis=1)
    df = df1.melt(id_vars=['발주시즌', '구분', '입고율'], var_name='종류', value_name='원단량').drop('입고율', axis=1)
    # df = df.sort_values('발주시즌', ascending=False)

    # 미입고량 음수 처리 (사실 음수면 모두 0 처리됨)
    df.loc[df['원단량'] < 0, '원단량'] = 0
    
    return df



# -------------------- 사이드바 (구매팀) --------------------
st.sidebar.header('시즌')

# 사이드바 시즌 선택
choosen_season = st.sidebar.selectbox(
    '시즌을 선택하세요 : ',
    options=['24F', '23S'],
)

# 사이드바 2
st.sidebar.header('제품')

# 사이드바 제품 선택
choosen_jaepum = st.sidebar.selectbox(
    '제품을 선택하세요 : ',
    options=['학생복원단', '체육복원단'],
)

# 제품 코드 지정
if choosen_jaepum == '학생복원단':
    jaepum = 'H'
elif choosen_jaepum == '체육복원단':
    jaepum = 'F'



# SQL문 만들기
sql_1, sql_2 = make_sql(choosen_season[:3], choosen_season[-3:], jaepum)

# 기본 데이터프레임 만들기
df_base_a = mod.select_data(sql_1)
df_base_b = mod.select_data(sql_2)
# 위의 데이터프레임은 streamlit으로 출력 안됨. 컬럼명 길이 제한이 있는 듯.

# 전처리 (astype 후 concat)
df_base = data_preprocess(df_base_a, df_base_b)

# merge 할 CPC 표 (기초코드 36)
df_cpc_list = mod.cod_code('36')

# merge 작업 (체육복 원단쪽엔 E 없음)
df_base_2, df_base_2_E = data_preprocess2(df_base, df_cpc_list, choosen_season[-1], jaepum) # 원본, 머지테이블, 시즌(동하복), 제품(학,체)

# 세부 전처리 (시즌토탈, 월별계)
df_base_3, df_base_3_sum = data_preprocess3(df_base_2)

# 그래프용 melt (음수처리)
df_base_4 = data_preprocess4(df_base_3)


# @st.cache_data
# def past_seasons() -> pd.DataFrame:
#     df_past_seasons = pd.DataFrame()
#     # 년도별 누적 발주
#     for i in range(5): # 5년

#         past_season = str(int(choosen_season[:2]) - i) + choosen_season[-1]
        
#         # SQL문 만들기
#         sql_1_s, sql_2_s = make_sql(past_season[:3], past_season[-3:], jaepum)

#         # 기본 데이터프레임 만들기
#         df_base_1_s = mod.select_data(sql_1_s)
#         df_base_2_s = mod.select_data(sql_2_s)
#         # 위의 데이터프레임은 streamlit으로 출력 안됨. 컬럼명 길이 제한이 있는 듯.

#         # 전처리 (astype 후 concat)
#         df_base_s = data_preprocess(df_base_1_s, df_base_2_s)

#         # merge 할 CPC 표 (기초코드 36)
#         df_cpc_list_s = mod.cod_code('36')

#         # merge 작업 (체육복 원단쪽엔 E 없음)
#         df_base_2_s, df_base_2_E_s = data_preprocess2(df_base_s, df_cpc_list_s, choosen_season[-1], jaepum) # 원본, 머지테이블, 시즌(동하복), 제품(학,체)

#         # 세부 전처리 (시즌토탈, 월별계)
#         df_base_3_s, df_base_3_sum_s = data_preprocess3(df_base_2_s)
        
#         df_result = pd.concat([df_past_seasons, (df_base_3_sum_s[df_base_3_sum_s['발주시즌'] == past_season]).set_index('발주시즌')])

#     return df_result

# df_past_seasons = past_seasons()


# -------------------- 그래프 (구매팀) --------------------

# Icicle 차트
cm: dict = {'(?)': 'lightgrey', '미입고량': 'rgb(239,120,64)', '발주량': 'lightgray', '입고량': 'rgb(94,144,205)'}
# fig1 = px.icicle(df_base_4,
#             path=[px.Constant('전체 (전년 + 올해)'), '발주시즌', '구분', '원단량'],
#             values='원단량',
#             # title=f'전년도 대비 비교 (면적 차트)',
#             color='종류',
#             color_discrete_map=cm,
#             maxdepth=4,
#             height=600,
#             )
# # fig1.update_layout(paper_bgcolor='rgba(233,233,233,233)', plot_bgcolor='rgba(0,0,0,0)')
# fig1.update_layout(
#     margin = dict(t=0, l=0, r=0, b=0),
#     font_size=20,
#     )
# # fig1.update_traces(sort=False)


# fig2 = px.sunburst(
#     df_base_4[df_base_4['발주시즌']==choosen_season],
#     path=['구분', '원단량'],
#     values='원단량',
#     color='종류',
#     height=600,
#     color_discrete_map=cm,
#     )
# fig2.update_traces(textfont_size=20,)
# fig2.update_layout(
#     plot_bgcolor="rgba(0,0,0,0)",
#     margin = dict(t=0, l=0, r=0, b=0),
#     # font_size=20,
# )


# fig3 = px.sunburst(
#     df_base_4[df_base_4['발주시즌']==(str(int(choosen_season[:2])-1)+choosen_season[-1])],
#     path=['구분', '원단량'],
#     values='원단량',
#     color='종류',
#     height=600,
#     color_discrete_map=cm,
#     )
# fig3.update_traces(textfont_size=20,)
# fig3.update_layout(
#     plot_bgcolor="rgba(0,0,0,0)",
#     margin = dict(t=0, l=0, r=0, b=0),
#     # font_size=20,
# )

plot_df_4 = df_base_4[df_base_4['발주시즌']==choosen_season]
fig4 = px.bar(
    plot_df_4,
    x='구분',
    y='원단량',
    color='종류',
    title=f'{choosen_season[:2]}년 원단 발주/입고 현황',
    text='원단량',
    barmode='stack',
    height=500,
    )
for i, fab in enumerate(plot_df_4['구분'].unique()):
    fig4.add_annotation(
        xref='x',
        yref='y',
        x=i,
        y=plot_df_4[plot_df_4['구분']==fab]['원단량'].sum() + \
            max(df_base_4[df_base_4['발주시즌']==(str(int(choosen_season[:2])-1)+choosen_season[-1])]['원단량'])*0.1, # Y축 최대값 + (공통 Y축 * 0.1)
        text=str(format(plot_df_4[plot_df_4['구분']==fab]['원단량'].sum(), ',')),
        font_size=18,
        showarrow=False,
        bgcolor='skyblue',
        )
fig4.update_yaxes(tickformat=',d')
fig4.update_layout(
    font_size=16,
    paper_bgcolor='rgba(233,233,233,233)', plot_bgcolor='rgba(0,0,0,0)',
    yaxis_range=[0, max(df_base_4[df_base_4['발주시즌']==(str(int(choosen_season[:2])-1)+choosen_season[-1])]['원단량'])*1.2],
    title_font_size=30,
)
fig4.update_traces(texttemplate='%{text:,}', width=0.6, textposition='inside')


plot_df_5 = df_base_4[df_base_4['발주시즌']==(str(int(choosen_season[:2])-1)+choosen_season[-1])]
fig5 = px.bar(
    plot_df_5,
    x='구분',
    y='원단량',
    color='종류',
    title=f'{str(int(choosen_season[:2])-1)}년 원단 발주/입고 현황',
    text='원단량',
    barmode='stack',
    height=500,
    )
for i, fab in enumerate(plot_df_5['구분'].unique()):
    fig5.add_annotation(
        xref='x',
        yref='y',
        x=i,
        y=plot_df_5[plot_df_5['구분']==fab]['원단량'].sum() + \
            max(plot_df_5['원단량'])*0.1, # Y축 최대값 + (공통 Y축 * 0.1)
        text=str(format(plot_df_5[plot_df_5['구분']==fab]['원단량'].sum(), ',')),
        font_size=18,
        showarrow=False,
        bgcolor='skyblue',
        )
fig5.update_yaxes(tickformat=',d')
fig5.update_layout(
    font_size=16,
    paper_bgcolor='rgba(233,233,233,233)', plot_bgcolor='rgba(0,0,0,0)',
    yaxis_range=[0, max(plot_df_5['원단량'])*1.2],
    title_font_size=30,
)
fig5.update_traces(texttemplate='%{text:,}', width=0.6, textposition='inside')


# plot_df_6 = df_past_seasons
# fig6 = px.bar(
#     plot_df_6,
#     x='구분',
#     y='원단량',
#     color='종류',
#     title=f'{str(int(choosen_season[:2])-1)}년',
#     text='원단량',
#     barmode='stack',
#     height=500,
#     )
# for i, fab in enumerate(plot_df_6['구분'].unique()):
#     fig6.add_annotation(
#         xref='x',
#         yref='y',
#         x=i,
#         y=plot_df_6[plot_df_6['구분']==fab]['원단량'].sum() + \
#             max(plot_df_6['원단량'])*0.1, # Y축 최대값 + (공통 Y축 * 0.1)
#         text=str(format(plot_df_6[plot_df_6['구분']==fab]['원단량'].sum(), ',')),
#         font_size=18,
#         showarrow=False,
#         bgcolor='skyblue',
#         )
# fig6.update_yaxes(tickformat=',d')
# fig6.update_layout(
#     font_size=16,
#     paper_bgcolor='rgba(233,233,233,233)', plot_bgcolor='rgba(0,0,0,0)',
#     yaxis_range=[0, max(plot_df_6['원단량'])*1.2],
#     title_font_size=30,
# )
# fig6.update_traces(texttemplate='%{text:,}', width=0.6, textposition='inside')



# -------------------- 메인페이지 (구매팀) --------------------

st.markdown('#### 구매팀 주간업무 보고')
st.markdown(f'주요업무 ({mod.this_mon} ~ {mod.this_fri})')

# mod.draw_plan(mod.plan_data, '구매팀') # MASTER PLAN

st.markdown('##### [원자재]')
if choosen_season[-1] == 'F':
    st.markdown(f'[{choosen_season[:2]}년 동복 {choosen_jaepum} 진행현황]')
elif choosen_season[-1] == 'S':
    st.markdown(f'[{choosen_season[:2]}년 하복 {choosen_jaepum} 진행현황]')


left_column, right_column = st.columns(2)
left_column.dataframe((df_base_3[df_base_3['발주시즌'] == choosen_season]).set_index('발주시즌'), use_container_width=True)
right_column.dataframe((df_base_3[df_base_3['발주시즌'] == (str(int(choosen_season[:2])-1)+choosen_season[-1])]).set_index('발주시즌'), use_container_width=True)


# st.markdown('''---''')

# 합계
left_column, right_column = st.columns(2)
left_column.dataframe((df_base_3_sum[df_base_3_sum['발주시즌'] == choosen_season]).set_index('발주시즌'), use_container_width=True)
right_column.dataframe((df_base_3_sum[df_base_3_sum['발주시즌'] == (str(int(choosen_season[:2])-1)+choosen_season[-1])]).set_index('발주시즌'), use_container_width=True)


left_column, right_column = st.columns(2)
# left_column.write('##### 올해 진행현황')
left_column.plotly_chart(fig4, use_container_width=True, theme=None)
# right_column.write('##### 전년 진행현황')
right_column.plotly_chart(fig5, use_container_width=True, theme=None)
with st.expander('-'):
    sql_every_1 = f'''
    SELECT Max(s.sub_sojae_saib_gb),
        Max(To_char(s.sub_buking_cnt)),
        utl_raw.Cast_to_raw(Max(s.sub_cf_ref)),
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
        utl_raw.Cast_to_raw(Max(tkyk_name)),
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
        AND s.sub_quota IN ( '19F', '20F', '21F', '22F',
                             '19S', '20S', '21S', '22S' )
        AND s.sub_jaepum = 'H'
    GROUP  BY cod_etc2,
            s.sub_order,
            s.sub_quota
    ORDER  BY Max(s.sub_sojae),
            s.sub_order
    '''

    sql_every_2 = f'''
    SELECT Max(s.sub_sojae_saib_gb),
        Max(To_char(s.sub_buking_cnt)),
        utl_raw.Cast_to_raw(Max(s.sub_cf_ref)),
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
        utl_raw.Cast_to_raw(Max(tkyk_name)),
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
        AND i.ipgo_bal_quota IN ( '19F', '20F', '21F', '22F',
                                  '19S', '20S', '21S', '22S' )
        AND subd_quota IN ( '19F', '20F', '21F', '22F',
                            '19S', '20S', '21S', '22S' )
        AND subd_quota = i.ipgo_bal_quota
        AND i.ipgo_quota <> i.ipgo_bal_quota
        AND s.sub_jaepum = 'H'
    GROUP  BY cod_etc2,
            s.sub_order,
            subd_quota,
            i.ipgo_bal_quota
    ORDER  BY Max(s.sub_sojae),
            s.sub_order
    '''
        
    df_every_1 = mod.select_data(sql_every_1) # 기본 데이터프레임 만들기
    df_every_2 = mod.select_data(sql_every_2) # 위의 데이터프레임은 streamlit으로 출력 안됨. 컬럼명 길이 제한이 있는 듯.
    df_every_base = data_preprocess(df_every_1, df_every_2) # 전처리 (astype 후 concat)
    # st.write(df_every_base)
    # df_every_base.to_clipboard(index=False) # 클립보드에 복사

    df_every_base_2, _ = data_preprocess2(df_every_base, df_cpc_list, choosen_season[-1], jaepum) # 원본, 머지테이블, 시즌(동하복), 제품(학,체) # merge 작업 (체육복 원단쪽엔 E 없음)
    df_every_base_3, _ = data_preprocess3(df_every_base_2) # 세부 전처리 (시즌토탈, 월별계)
    df_every_base_4 = data_preprocess4(df_every_base_3) # 그래프용 melt (음수처리)
    

    # df_every_base_4.to_clipboard()
    # st.dataframe(df_every_base, use_container_width=True)
    # st.dataframe(df_every_base_2, use_container_width=True)
    # st.dataframe(df_every_base_3, use_container_width=True)

    # ('최종입고' - '최초발주') > 1년 이상인 데이터
    ####df_error = df_every_base_2[(df_every_base_2['최종입고'] - df_every_base_2['최초발주']) > pd.Timedelta('365 days')].sort_values('최종입고', ascending=False)
    # st.dataframe(df_every_base_2['밀넘버시즌'].str[:2])
    # st.write(df_every_base_2['최종입고'].dropna().dt.year.astype(str).str[-2:])

    df_every_base_2['최종입고년도'] = df_every_base_2['최종입고'].dt.year
    df_every_base_2['밀넘버시즌년도'] = df_every_base_2['밀넘버시즌'].str[:2].astype(int) + 2000

    df_error1 = df_every_base_2[(df_every_base_2['최종입고'] - df_every_base_2['최초발주']) > pd.Timedelta('365 days')].sort_values('최종입고', ascending=False) # 최종입고 - 최초발주 > 1년
    df_error2 = df_every_base_2[df_every_base_2['최종입고년도'] > df_every_base_2['밀넘버시즌년도']].sort_values('최종입고', ascending=False) # 최종입고년도 > 밀넘버시즌년도

    df_error = pd.concat([df_error1, df_error2]).drop_duplicates().sort_values('최종입고', ascending=False) # 1,2 합치기 & 중복제거 & 정렬

    # st.dataframe(df_error.drop('단가', axis=1), use_container_width=True) # 단가삭제
    st.dataframe(df_error, use_container_width=True) # 단가표시
    st.write(df_error.shape) # 사이즈 확인
    # st.dataframe(df_error[df_error['입고밀넘버'] == '21FGS030361'], use_container_width=True)

    # # '최종입고'가 2022년인 데이터
    # df_every_base_2[df_every_base_2['최종입고'] > 2022]

    # st.write(len(df_every_base_4))

    plot_df_every_F = df_every_base_4[df_every_base_4['발주시즌'].str[-1] == 'F']
    plot_df_every_S = df_every_base_4[df_every_base_4['발주시즌'].str[-1] == 'S']
    fig_every_F = px.bar(
        plot_df_every_F,
        x='구분',
        y='원단량',
        color='종류',
        # title=f'{min(plot_df_every_F["발주시즌"])} ~ {max(plot_df_every_F["발주시즌"])}년간 원단 발주/입고 현황',
        text='원단량',
        facet_col='발주시즌',
        facet_col_wrap=1,
        barmode='stack',
        height=1500,
        )
    # for i, fab in enumerate(plot_df_every_F['구분'].unique()):
    #     fig_every_F.add_annotation(
    #         xref='x',
    #         yref='y',
    #         x=i,
    #         # y=plot_df_every_F[plot_df_every_F['구분']==fab]['원단량'].sum() + \
    #         #     max(plot_df_every_F[plot_df_every_F['발주시즌']==(str(int(choosen_season[:2])-1)+choosen_season[-1])]['원단량'])*0.1, # Y축 최대값 + (공통 Y축 * 0.1)
    #         text=str(format(plot_df_every_F[plot_df_every_F['구분']==fab]['원단량'].sum(), ',')),
    #         font_size=18,
    #         showarrow=False,
    #         bgcolor='skyblue',
    #         )
    fig_every_F.update_yaxes(tickformat=',d')
    fig_every_F.update_layout(
        font_size=16,
        paper_bgcolor='rgba(233,233,233,233)', plot_bgcolor='rgba(0,0,0,0)',
        # yaxis_range=[0, max(plot_df_every_F[plot_df_every_F['발주시즌']==(str(int(choosen_season[:2])-1)+choosen_season[-1])]['원단량'])*1.2],
        title_font_size=30,
    )

    fig_every_S = px.bar(
        plot_df_every_S,
        x='구분',
        y='원단량',
        color='종류',
        # title=f'{min(plot_df_every_S["발주시즌"])} ~ {max(plot_df_every_S["발주시즌"])}년간 원단 발주/입고 현황',
        text='원단량',
        facet_col='발주시즌',
        facet_col_wrap=1,
        barmode='stack',
        height=1500,
        )
    # for i, fab in enumerate(plot_df_every_S['구분'].unique()):
    #     fig_every_S.add_annotation(
    #         xref='x',
    #         yref='y',
    #         x=i,
    #         # y=plot_df_every_S[plot_df_every_S['구분']==fab]['원단량'].sum() + \
    #         #     max(plot_df_every_S[plot_df_every_S['발주시즌']==(str(int(choosen_season[:2])-1)+choosen_season[-1])]['원단량'])*0.1, # Y축 최대값 + (공통 Y축 * 0.1)
    #         text=str(format(plot_df_every_S[plot_df_every_S['구분']==fab]['원단량'].sum(), ',')),
    #         font_size=18,
    #         showarrow=False,
    #         bgcolor='skyblue',
    #         )
    fig_every_S.update_yaxes(tickformat=',d')
    fig_every_S.update_layout(
        font_size=16,
        paper_bgcolor='rgba(233,233,233,233)', plot_bgcolor='rgba(0,0,0,0)',
        # yaxis_range=[0, max(plot_df_every_S[plot_df_every_S['발주시즌']==(str(int(choosen_season[:2])-1)+choosen_season[-1])]['원단량'])*1.2],
        title_font_size=30,
    )

    # left_column, right_column = st.columns(2)
    # left_column.dataframe(plot_df_every_F, use_container_width=True)
    # right_column.dataframe(plot_df_every_S, use_container_width=True)
    left_column, right_column = st.columns(2)
    left_column.plotly_chart(fig_every_F, use_container_width=True, theme=None)
    right_column.plotly_chart(fig_every_S, use_container_width=True, theme=None)


# st.dataframe(df_past_seasons, use_container_width=True)

# st.dataframe(df_base_4, use_container_width=True)
# st.dataframe(df_base_2, use_container_width=True)
# df_base_2_E.to_clipboard()


# 텍스트 특이사항
tab1, tab2 = st.tabs(['.', '.'])
with tab1:
    try:
        sel_text = mod.select_text(mod.db_file, datetime.strptime(mod.this_fri, '%Y/%m/%d').isocalendar()[1], '구매팀', 'text1')
    except IndexError:
        sel_text = ''

    st.markdown(sel_text)


with tab2:
    # 입력파트
    pur_text = st.text_area('이번 주 내용을 입력하세요.', sel_text)
    st.write('입력된 내용 : \n', pur_text)
    
    mod.insert_text(mod.db_file, datetime.strptime(mod.this_fri, '%Y/%m/%d').isocalendar()[1], '구매팀', pur_text, 'text1')


# -------------------- HIDE STREAMLIT STYLE --------------------
hide_st_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """
st.markdown(hide_st_style, unsafe_allow_html=True)
