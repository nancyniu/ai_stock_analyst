import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

def initialize_session_state():
    """Initialize session state variables"""
    if 'selected_stocks' not in st.session_state:
        st.session_state.selected_stocks = []
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if "messages" not in st.session_state:
        st.session_state.messages = []

def get_sp500_symbols():
    """Get list of S&P 500 stocks for scanning"""
    # In a real application, you would implement your preferred method
    # of getting stock symbols (e.g., from an API or database)
    # This is a placeholder with some example stocks
    return ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA"]

def get_stock_data(symbol, period='1d'):
    """Fetch stock data using yfinance"""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        return hist
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {str(e)}")
        return None

def identify_gaps(df):
    """Identify price gaps in stock data"""
    df['gap'] = df['Open'] - df['Close'].shift(1)
    df['gap_percent'] = (df['gap'] / df['Close'].shift(1)) * 100
    return df

def analyze_stock(symbol):
    """Perform deep dive analysis on a single stock"""
    stock = yf.Ticker(symbol)
    
    # Get historical data
    hist = stock.history(period='1y')
    
    # Basic statistics
    analysis = {
        'current_price': hist['Close'][-1],
        'daily_change': ((hist['Close'][-1] - hist['Close'][-2]) / hist['Close'][-2] * 100),
        '52w_high': hist['High'].max(),
        '52w_low': hist['Low'].min(),
        'volume_avg': hist['Volume'].mean(),
        'volatility': hist['Close'].pct_change().std() * 100
    }
    
    return analysis, hist

def main():
    st.set_page_config(page_title="Stock Analysis Tool", layout="wide")
    initialize_session_state()
    
    st.title("Stock Analysis Dashboard")
    
    # Create two main columns
    left_column, right_column = st.columns([2, 1])
    
    with left_column:
        # Gap Scanner Section
        with st.expander("Gap Scanner", expanded=True):
            st.subheader("Gap Scanner")
            
            gap_threshold = st.slider("Gap Threshold (%)", 1.0, 10.0, 3.0)
            
            if st.button("Gap Strategy"):
                symbols_list = get_sp500_symbols()  # Automatically get stocks to scan
                results = []
                
                with st.spinner("Scanning for gaps..."):
                    for symbol in symbols_list:
                        data = get_stock_data(symbol)
                        if data is not None:
                            data = identify_gaps(data)
                            significant_gaps = data[abs(data['gap_percent']) > gap_threshold]
                            
                            if not significant_gaps.empty:
                                results.append({
                                    'symbol': symbol,
                                    'gaps': significant_gaps
                                })
                
                st.session_state.analysis_results = results
                
                if results:
                    for result in results:
                        st.subheader(f"Gaps for {result['symbol']}")
                        st.dataframe(result['gaps'][['Open', 'Close', 'gap', 'gap_percent']])
                else:
                    st.info("No significant gaps found for the given threshold.")
        
        # Deep Dive Analysis Section
        with st.expander("Deep Dive Analysis", expanded=True):
            st.subheader("Deep Dive Analysis")
            
            symbol = st.text_input("Enter stock symbol for deep dive", "AAPL")
            
            if st.button("Analyze Stock"):
                with st.spinner(f"Analyzing {symbol}..."):
                    analysis, hist_data = analyze_stock(symbol)
                    
                    # Display analysis results in columns
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
                    
                    # Display price chart
                    st.line_chart(hist_data['Close'])
                    
                    # Display volume chart
                    st.bar_chart(hist_data['Volume'])
    
    with right_column:
        # AI Chat Analysis Section
        st.subheader("AI Chat Analysis")
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask about stock analysis..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Here you would integrate with your AI service
            response = f"AI analysis for: {prompt}"
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)

if __name__ == "__main__":
    main()
