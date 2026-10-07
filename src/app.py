import streamlit as st
import pandas as pd
import plotly.express as px
from risk_engine import RiskEngine
from module_a_rebalancer import calculate_rebalanced_weights, format_rebalance_df
from module_b_stress_test import run_stress_test, format_stress_results

st.set_page_config(page_title="AI/NLP Risk Engine", layout="wide")
st.title("AI/NLP Financial Risk Engine & Downstream Analytics")

# Cache engine initialization so model weights load into memory ONCE
@st.cache_resource
def load_risk_engine():
    return RiskEngine()

engine = load_risk_engine()

# Sidebar Data Inputs
st.sidebar.header("Data Ingestion Stream")
data_source = st.sidebar.selectbox("Select Source", ["Financial News Feed", "Social Media (Twitter/X)"])

# Sample Preset Scenarios
presets = {
    "Macro Crisis (Oil & Interest Rates)": "Breaking: Global tensions spark oil supply fears amidst rising central bank interest rate hikes.",
    "Tech Boom (AI Earnings Beat)": "Breaking: Breakthrough AI productivity gains fuel massive enterprise earnings beat across tech sector.",
    "Banking Sector Stress (Credit Defaults)": "Alert: Rising corporate credit default rates spark severe liquidity tightening in wholesale banking."
}

selected_preset = st.sidebar.selectbox(
    "Sample Preset Scenarios", 
    ["Macro Crisis (Oil & Interest Rates)", "Tech Boom (AI Earnings Beat)", "Banking Sector Stress (Credit Defaults)"]
)

default_text = presets.get(selected_preset, presets["Macro Crisis (Oil & Interest Rates)"])

input_text = st.sidebar.text_area(
    "Unstructured Text Payload", 
    value=default_text,
    height=120
)

if st.sidebar.button("Process Payload"):
    # Smooth loading feedback
    with st.spinner("Analyzing NLP payload & evaluating downstream risk..."):
        risk_signal = engine.analyze_text(input_text)
    
    st.subheader("1. Core Risk Engine Output Signals")
    col1, col2, col3 = st.columns(3)
    col1.metric("Sentiment Score", risk_signal['sentiment_score'])
    col2.metric("Event Classification", risk_signal['event_classification'])
    col3.metric("Impact Score (1-10)", risk_signal['impact_score'])

    tab1, tab2 = st.tabs(["Tactical Index Rebalancer", "Wholesale Stress Testing"])

    with tab1:
        st.header("S&P Index Tactical Weight Adjustments")
        base_weights = {"AAPL": 0.25, "MSFT": 0.25, "NVDA": 0.20, "JPM": 0.15, "XOM": 0.15}
        sentiments = {"AAPL": risk_signal['sentiment_score'], "MSFT": 0.2, "NVDA": -0.4, "JPM": 0.1, "XOM": -0.3}
        
        rebalanced_df = calculate_rebalanced_weights(base_weights, sentiments)
        
        fig = px.bar(
            rebalanced_df, 
            x='Ticker', 
            y=['Base_Weight', 'New_Weight'], 
            barmode='group', 
            title="Portfolio Weight Adjustments (Pre vs. Post Sentiment Tilt)"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        formatted_reb_df = format_rebalance_df(rebalanced_df)
        st.dataframe(formatted_reb_df, use_container_width=True)
        
        csv_rebalance = formatted_reb_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Risk Assessment Report (CSV)",
            data=csv_rebalance,
            file_name="tactical_index_rebalance_report.csv",
            mime="text/csv"
        )

    with tab2:
        st.header("Wholesale Banking Portfolio Stress Test")
        stress_res = run_stress_test("data/wholesale_portfolio.json", risk_signal['event_classification'], risk_signal['impact_score'])
        
        if stress_res['status'] == "STRESS_EXECUTED":
            st.error(f"High Risk Event Triggered (Impact > 7.0)! Total PnL Impact: ${stress_res['total_pnl']:,.2f} ({stress_res['pnl_pct']}%)")
            
            df_stress_raw = pd.DataFrame(stress_res['asset_details'])
            fig_stress = px.bar(
                df_stress_raw,
                x='Asset_ID',
                y='PnL',
                color='Type',
                title='PnL Loss Breakdown by Portfolio Asset',
                labels={'PnL': 'PnL Impact ($)', 'Asset_ID': 'Asset Identifier'}
            )
            st.plotly_chart(fig_stress, use_container_width=True)

            formatted_stress_df = format_stress_results(stress_res['asset_details'])
            st.dataframe(formatted_stress_df, use_container_width=True)
            
            csv_stress = formatted_stress_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Stress Test Audit Log (CSV)",
                data=csv_stress,
                file_name="wholesale_stress_test_audit_log.csv",
                mime="text/csv"
            )
        else:
            st.success("Impact score below threshold (<= 7.0). No portfolio stress test required.")