import streamlit as st
import pandas as pd
import yfinance as yf

from phi.agent import Agent, RunResponse
#from dotenv import load_dotenv
from phi.model.groq import Groq
from phi.model.anthropic import Claude

from phi.tools.yfinance import YFinanceTools

from finvizfinance.quote import finvizfinance
from finvizfinance.screener.overview import Overview
from datetime import datetime, timedelta

from lightweight_charts.widgets import StreamlitChart

#load_dotenv()
#model=Claude(id="claude-3-5-sonnet-20240620"),
#model=Groq(id="llama-3.3-70b-versatile"),
#model=Groq(id="claude-3-5-haiku-20241022"),
agent = Agent(
    model=Claude(id="claude-3-5-sonnet-20240620"),
    tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, stock_fundamentals=True, company_news=True)],
    show_tool_calls=True,
    markdown=True,
    instruction=["Use tables to display data when possible."],
)

st.set_page_config(layout="wide")

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
    return df

def analyze_stock(symbol):
    """Perform deep dive analysis on a single stock"""
    stock = yf.Ticker(symbol)

    #news = stock.get_news()
    
    response: RunResponse = agent.run(f"Please summarize the corporate financial of {symbol} and summarize any news that may impact the stock price", stream=False, markdown=False)

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
    return analysis, hist, response

def intialize():
    st.session_state.myselect = 0

#initialize_session_state()
st.title("Stock Gapper Analysis Dashboard")

if "my_df" not in st.session_state:
    intialize()
    if st.button("Gap Scan", type="primary"):
        df = get_screener_symbols()
        edited_df = st.data_editor(df, disabled=["Ticker", "Company"], key="remember",  hide_index=True,)
        st.session_state.my_df = edited_df
else:
    st.button("Gap Scan", type="secondary")
    df = st.session_state.my_df
    mykey = st.session_state.remember['edited_rows']
    st.session_state.myselect = 1
    for key in mykey:
        row_edited = int(key)
        row_value = mykey[key]['Deep_Dive']
    try:
        if row_value == True:
            df.loc[row_edited, 'Deep_Dive'] = True
        else:
            df.loc[row_edited, 'Deep_Dive'] = False
            #st.write('test me')
    except:
        pass

    edited_df = st.data_editor(df, disabled=["Ticker", "Company"], key="remember", hide_index=True)
    st.session_state.my_df = edited_df

if st.session_state.myselect == 0:
    st.button("Deep Dive", type="secondary")
elif st.session_state.myselect == 1:

    if st.button("Deep Dive", type="primary"):
        edited_df = st.session_state.my_df
        selected_stocks = edited_df[edited_df["Deep_Dive"] == True]['Ticker'].values.tolist()

        for symbol in selected_stocks:
            company = edited_df[edited_df['Ticker'] == symbol]['Company'].values[0]
            with st.spinner(f"Analyzing {symbol}..."):
                analysis, hist_data, news = analyze_stock(symbol)
                st.write(f"Summary of {company}...")
                #for title in news:
                #    st.write(title['content']['title'])
                st.write(news.content)
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
