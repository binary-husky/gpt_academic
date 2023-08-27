#! .\venv\
# encoding: utf-8
# @Time   : 2023/8/26
# @Author : Spike
# @Descr   :
import streamlit as st
from streamlit_chat import message
from streamlit_option_menu import option_menu

with st.sidebar:
    st.set_page_config(
        "Tester ",
        initial_sidebar_state="expanded",
    )
    selected_page = option_menu(
        "",
        options=['基础对话', '提示词', '功能插件', '知识库', 'Settings'],
        # 在这里可以找到对应的图标 https://icons.getbootstrap.com/
        icons=['chat', 'braces-asterisk', 'plugin', 'journals', 'sliders2'],
        # menu_icon="chat-quote",
        # orientation='horizontal',
        styles={
            "container": {"padding": "1 !important", },
            # "icon": {"font-size": "25px"},
            # "nav-link": {"font-size": "20px", "text-align": "left", "margin": "0px"},
        }
    )
