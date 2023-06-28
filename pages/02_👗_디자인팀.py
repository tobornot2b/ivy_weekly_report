import streamlit as st
from datetime import datetime
from data import * # 패키지 불러오기

# emojis: https://www.webfx.com//tools/emoji-cheat-sheet/
st.set_page_config(
    page_title='주간업무보고',
    page_icon=":chart_with_upwards_trend:",
    layout="wide"
)


# -------------------- 메인페이지 (디자인팀) --------------------
st.markdown('#### 디자인팀 주간업무 보고')
st.markdown(f"주요업무 ({mod.this_mon} ~ {mod.this_fri})")
# mod.draw_plan(mod.plan_data, '디자인팀')

tab1, tab2 = st.tabs(['.', '.'])
with tab1:
    try:
        sel_text = mod.select_text(mod.db_file, datetime.strptime(mod.this_fri, '%Y/%m/%d').isocalendar()[1], '디자인팀', 'text1')
    except IndexError:
        sel_text = ''

    st.markdown(sel_text)
    # st.image('./data/image/design1.jpg', width=480)

with tab2:
    # 입력파트
    design_text = st.text_area('이번 주 내용을 입력하세요.', sel_text)
    st.write('입력된 내용 : \n', design_text)
    
    mod.insert_text(mod.db_file, datetime.strptime(mod.this_fri, '%Y/%m/%d').isocalendar()[1], '디자인팀', design_text, 'text1')



# -------------------- HIDE STREAMLIT STYLE --------------------
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)