import streamlit as st
from pages import *

st.set_page_config(layout='wide')

def next_page():
    st.session_state.page += 1

def home_page_content():
    st.session_state.page = 0
    st.rerun()

def new_data_page():
    keys = list(st.session_state.keys())
    for key in keys:
        del st.session_state[key]
    st.rerun()

if "page" not in st.session_state:
    st.session_state.page = 0

def get_page():

    if st.session_state.page == 0:
        
        

        load_home()

    elif st.session_state.page == 1:
        second_page_content()

def header():

    home_button, reset_button, right = st.columns([2,2,13])
    with home_button:
        st.write("")
        if st.button(":classical_building: Home",key = "home_button"):
            home_page_content()
    with reset_button:
        st.write("")
        if st.button(":repeat: New Data",key = "new_data_button"):
            new_data_page()
    # with right:
    st.markdown("<h1 style='text-align: center; color: MediumSeaGreen;'> Dataset Features</h1>", unsafe_allow_html=True)


if __name__ == "__main__":
    header()
    get_page()