import streamlit as st
import pandas as pd
import yfinance as yf

from finvizfinance.quote import finvizfinance
from finvizfinance.screener.overview import Overview
from datetime import datetime, timedelta

from lightweight_charts.widgets import StreamlitChart

df = pd.DataFrame(
    [
       {"command": "st.selectbox", "rating": 4, "is_widget": False},
       {"command": "st.balloons", "rating": 5, "is_widget": False},
       {"command": "st.time_input", "rating": 3, "is_widget": False},
   ]
)

if "my_df" not in st.session_state:
    st.session_state['counter'] = 0
    if st.button("scan", type="primary"):
        edited_df = st.data_editor(df, key="remember") 
        st.session_state.my_df = edited_df
        st.session_state['counter'] += 1
else:
    #df = st.session_state.my_df
    df = st.session_state.my_df
    mykey = st.session_state.remember['edited_rows']

    for key in mykey:
        row_edited = int(key)
        row_value = mykey[key]['is_widget']

    if row_value == True:
        df.loc[row_edited, 'is_widget'] = True
    else:
        df.loc[row_edited, 'is_widget'] == False

    edited_df = st.data_editor( df, key="remember")

    st.session_state.my_df = edited_df
    st.session_state['counter'] += 10

def run1():
    try:
        st.write('counter: ', st.session_state.counter)
    except:
        st.write("missing counter")
run1()
