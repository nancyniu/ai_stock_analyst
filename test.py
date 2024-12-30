import streamlit as st
import pandas as pd
import yfinance as yf

from finvizfinance.quote import finvizfinance
from finvizfinance.screener.overview import Overview
from datetime import datetime, timedelta

from lightweight_charts.widgets import StreamlitChart



st.set_page_config(layout="wide")

def initialize_session_state():
    """Initialize session state variables"""
    if 'selected_stocks' not in st.session_state:
        st.session_state.selected_stocks = 0

def get_screener_symbols():
    """Get list of stocks for finviz scanner API"""
    # In a real application, you would implement your preferred method
    # of getting stock symbols (e.g., from an API or database)
    # This is a placeholder with some example stocks
    foverview = Overview()
    filters_dict = {'Gap': 'Up 4%',
                    'Relative Volume': 'Over 2',
                    'Price': 'Over $5',
                    'Average Volume': 'Over 100K'}
    
    foverview.set_filter(filters_dict=filters_dict)
    df = foverview.screener_view()
    df['Deep_Dive'] = False

    #list_stock = df['Ticker'].values.tolist()
    return df

def analyze_stock(symbol):
    """Perform deep dive analysis on a single stock"""
    stock = yf.Ticker(symbol)
    news = stock.get_news()
    # Get historical data
    hist = stock.history(period='1y')

    # Basic statistics
    analysis = {
        'current_price': hist['Close'].iloc[-1],
        'daily_change': ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2] * 100),
        '52w_high': hist['High'].max(),
        '52w_low': hist['Low'].min(),
        'volume_avg': hist['Volume'].mean(),
        'volatility': hist['Close'].pct_change().std() * 100
    }
    
    return analysis, hist, news

#initialize_session_state()
st.title("Stock Gapper Analysis Dashboard")
#if st.button("Gap Up"):
df = get_screener_symbols()
        
#st.session_state.selected_stocks = 1
#st.write(st.session_state.selected_stocks)

edited_df = st.data_editor(df, disabled=["Ticker", "Company"], hide_index=True,)

if st.button("Go", type="primary"):
    selected_stocks = edited_df[edited_df["Deep_Dive"] == True]['Ticker'].values.tolist()
    
    #st.write('You selected ', *selected_stocks, ' for additional analysis')

    for symbol in selected_stocks:
        company = edited_df[edited_df['Ticker'] == symbol]['Company'].values[0]
        with st.spinner(f"Analyzing {symbol}..."):
            analysis, hist_data, news = analyze_stock(symbol)
            st.write(f"Summary of {company}...")
            for title in news:
                st.write(title['content']['title'])
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Current Price", f"${analysis['current_price']:.2f}")
                st.metric("Daily Change", f"{analysis['daily_change']:.2f}%")
            with col2:
                st.metric("52-Week High", f"${analysis['52w_high']:.2f}")
                st.metric("52-Week Low", f"${analysis['52w_low']:.2f}")
            with col3:
                st.metric("Avg Volume", f"{analysis['volume_avg']:,.0f}")
                st.metric("Volatility", f"{analysis['volatility']:.2f}%")
                        
            chart = StreamlitChart(width=900, height=600)

            chart.set(hist_data)

            chart.load()

            # Display price chart
            #st.line_chart(hist_data['Close'])
                        
            # Display volume chart
            #st.bar_chart(hist_data['Volume'])