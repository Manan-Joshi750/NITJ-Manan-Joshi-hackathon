import streamlit as st
import pandas as pd
import plotly.express as px
from risk_engine import RiskEngine
from module_a_rebalancer import calculate_rebalanced_weights
from module_b_stress_test import run_stress_test

st.set_page_config(page_title="AI/NLP Risk Engine", layout="wide")
st.title("AI/NLP Financial Risk Engine & Downstream Analytics")

engine = RiskEngine()

# Sidebar Data Inputs
st.sidebar.header("Data Ingestion Stream")
data_source = st.sidebar.selectbox("Select Source", ["Financial News Feed", "Social Media (Twitter/X)"])
input_text = st.sidebar.text_area(
    "Unstructured Text Payload", 
    "Breaking: Global tensions spark oil supply fears amidst rising central bank interest rate hikes."
)

if st.sidebar.button("Process Payload"):
    risk_signal = engine.analyze_text(input_text)
    
    st.subheader("1. Core Risk Engine Output Signals")
    col1, col2, col3 = st.columns(3)
    col1.metric("Sentiment Score", risk_signal['sentiment_score'])
    col2.metric("Event Classification", risk_signal['event_classification'])
    col3.metric("Impact Score (1-10)", risk_signal['impact_score'])

    tab1, tab2 = st.tabs(["Module A: Tactical Index Rebalancer", "Module B: Portfolio Stress Testing"])

    with tab1:
        st.header("S&P Index Tactical Weight Adjustments")
        base_weights = {"AAPL": 0.25, "MSFT": 0.25, "NVDA": 0.20, "JPM": 0.15, "XOM": 0.15}
        sentiments = {"AAPL": risk_signal['sentiment_score'], "MSFT": 0.2, "NVDA": -0.4, "JPM": 0.1, "XOM": -0.3}
        
        rebalanced_df = calculate_rebalanced_weights(base_weights, sentiments)
        fig = px.bar(rebalanced_df, x='Ticker', y=['Base_Weight', 'New_Weight'], barmode='group', title="Portfolio Weight Adjustments")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(rebalanced_df)

    with tab2:
        st.header("Wholesale Banking Portfolio Stress Test")
        stress_res = run_stress_test("data/wholesale_portfolio.json", risk_signal['event_classification'], risk_signal['impact_score'])
        
        if stress_res['status'] == "STRESS_EXECUTED":
            st.error(f"High Risk Event Triggered (Impact > 7.0)! Total PnL Impact: ${stress_res['total_pnl']:,.2f} ({stress_res['pnl_pct']}%)")
            st.dataframe(pd.DataFrame(stress_res['asset_details']))
        else:
            st.success("Impact score below threshold (<= 7.0). No stress test required.")