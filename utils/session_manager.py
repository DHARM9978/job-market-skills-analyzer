import streamlit as st
from utils.constants import SESSION_DATA_KEY, SESSION_FILTERS_KEY, SESSION_DATA_SOURCE_KEY, SESSION_API_ERROR_KEY

def init_session_state():
    defaults = {
        SESSION_DATA_KEY: None,
        SESSION_FILTERS_KEY: {},
        SESSION_DATA_SOURCE_KEY: None,
        SESSION_API_ERROR_KEY: None,
        "uploaded_filename": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
