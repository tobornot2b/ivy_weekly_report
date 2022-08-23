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


# 주요업무
main_text = '''
---

### 5. 주요업무
    
    - 주관구매 낙찰학교 수주 및 홀드해제 진행

    - 주관구매 관련 경쟁사 동향 및 특이사항 지속 점검

---
'''


if __name__ == "__main__":
    print('영업팀 데이터 모듈파일입니다.')
    