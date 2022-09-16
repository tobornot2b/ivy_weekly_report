import streamlit as st
import streamlit_authenticator as stauth
import yaml


# emojis: https://www.webfx.com//tools/emoji-cheat-sheet/
st.set_page_config(
    page_title='주간업무보고',
    page_icon=":chart_with_upwards_trend:",
    layout="wide"
)

st.title('메인 페이지')
st.sidebar.success('각 팀별 페이지를 선택하세요.')



# -------------------- 사용자 인증 파트 --------------------

with open('./config.yaml') as file:
    config = yaml.load(file, Loader=yaml.SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status == False:
    st.error('아이디/비번이 올바르지 않습니다.')

if authentication_status == None:
    st.warning('아이디와 비번을 입력하세요.')

if authentication_status:
    st.success('인증완료')

    authenticator.logout("Logout", "sidebar")
    st.sidebar.title(f"환영합니다! {name}님")

    # with st.sidebar:
    #     st.radio('Select one:', [1, 2])





    # -------------------- HIDE STREAMLIT STYLE --------------------
    hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
    st.markdown(hide_st_style, unsafe_allow_html=True)