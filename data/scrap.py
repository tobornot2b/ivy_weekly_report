import requests
from bs4 import BeautifulSoup
import pandas as pd
from data import * # 패키지 불러오기


# 검색 키워드
keyword = '교복%20%2B경북%20%2B교육청%20%2B품질' # 교복 +경북 +교육청 +품질

# BeautifulSoup 설정값
url = f'https://m.search.naver.com/search.naver?where=m_news&sm=mtb_nmr&query={keyword}&sort=1' # 모바일 뉴스검색(sort=1:최신순)
UserAgent = 'Mozilla/5.0 (Linux; Android 12; LM-V500N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Mobile Safari/537.36' # 모바일 헤더값


def naver_news_scrap(url: str, UserAgent: str) -> pd.DataFrame: # 네이버 뉴스 스크랩
    try:
        html = requests.get(url=url, headers={'User-Agent': UserAgent})
        soup = BeautifulSoup(html.text, 'html.parser')

        # 뉴스 기사 제목, 언론사, 송고시간, URL 스크랩
        articles = soup.select('#news_result_list > li.bx')

        # 기사단위로 쪼개기
        article_list = []

        for article in articles:
            press = article.select_one('a.info.press').text.strip() # 언론사
            upload_time = article.select_one('span.info').text.strip() # 송고시간
            # title = article.select_one('a[class^="news_tit"]').text.strip() # 기사제목
            title = article.select_one('a.news_tit').text.strip() # 기사제목
            # url = article.select_one('a[class^="news_tit"]')['href'] # 기사 URL
            url = article.select_one('a.news_tit')['href'].strip() # 기사 URL
            main_text = article.select_one('div.news_dsc > div.dsc_wrap > a').text.strip() # 기사 본문
            thumb = article.select_one('a.dsc_thumb > img.thumb')['data-lazysrc'] # 썸네일

            article_list.append([press, upload_time, title, url, main_text, thumb])
            
        df = pd.DataFrame(article_list, columns=['언론사', '송고시간', '기사제목', 'URL', '기사본문', '썸네일'])

        print(df)
        return df
    except Exception as e:
        print(e)
        return None


if __name__ == '__main__':
    naver_news_scrap(url, UserAgent)
