
import streamlit as st
import pandas as pd
import numpy as np
import re
from datetime import datetime

st.set_page_config(page_title="Executive Decision Intelligence Platform", layout="wide", page_icon="📊")
st.title("📊 AI Business Strategy & Executive Decision Intelligence Platform")
st.markdown("**GenAI Powered - Converts Complex Business Data into Executive Insights**")
st.divider()

with st.sidebar:
    st.header("⚙️ Control Panel")
    sales_file = st.file_uploader("1. Sales/Financial Data (CSV)", type=["csv"])
    feedback_file = st.file_uploader("2. Customer Feedback (CSV)", type=["csv","txt"])
    st.divider()
    growth_rate = st.slider("Expected Sales Growth %", -20, 50, 10)
    cost_change = st.slider("Expected Cost Change %", -20, 50, 5)

def feedback_sentiment(text):
    text = str(text).lower()
    pos_words = ['good','great','excellent','love','best','happy','satisfied','awesome']
    neg_words = ['bad','worst','poor','hate','disappoint','slow','angry','complaint']
    pos = sum(1 for w in pos_words if w in text)
    neg = sum(1 for w in neg_words if w in text)
    if pos > neg: return "Positive"
    elif neg > pos: return "Negative"
    else: return "Neutral"

if sales_file:
    df = pd.read_csv(sales_file)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    sales_col = numeric_cols[0] if numeric_cols else df.columns[1]
    cost_col = numeric_cols[1] if len(numeric_cols)>1 else sales_col

    st.subheader("📌 Executive KPIs")
    col1, col2, col3, col4 = st.columns(4)
    total_sales = df[sales_col].sum()
    total_cost = df[cost_col].sum()
    profit = total_sales - total_cost
    col1.metric("Total Revenue", f"${total_sales:,.0f}")
    col2.metric("Total Cost", f"${total_cost:,.0f}")
    col3.metric("Profit", f"${profit:,.0f}")
    col4.metric("Scenario Profit", f"${(total_sales*(1+growth_rate/100) - total_cost*(1+cost_change/100)):,.0f}")

    tab1, tab2, tab3, tab4 = st.tabs(["📈 Performance", "🚨 Trends & Anomalies", "💬 Customer Feedback", "💡 AI Recommendations & Summary"])

    with tab1:
        st.dataframe(df.head(10), use_container_width=True)
        st.line_chart(df[sales_col])

    with tab2:
        Q1 = df[sales_col].quantile(0.25); Q3 = df[sales_col].quantile(0.75); IQR = Q3-Q1
        anomalies = df[(df[sales_col] < Q1-1.5*IQR) | (df[sales_col] > Q3+1.5*IQR)]
        st.write(f"Anomalies: {len(anomalies)}")
        st.dataframe(anomalies)
        half = len(df)//2
        change = ((df.iloc[half:][sales_col].mean() - df.iloc[:half][sales_col].mean())/df.iloc[:half][sales_col].mean()*100) if df.iloc[:half][sales_col].mean()!=0 else 0
        st.metric("Period Change %", f"{change:.2f}%")

    with tab3:
        if feedback_file:
            fb_df = pd.read_csv(feedback_file) if feedback_file.name.endswith('.csv') else pd.DataFrame({"Feedback":[feedback_file.read().decode('utf-8')]})
            fb_df['Sentiment'] = fb_df[fb_df.columns[0]].apply(feedback_sentiment)
            st.dataframe(fb_df.head(20))
            st.bar_chart(fb_df['Sentiment'].value_counts())
        else:
            st.info("Upload feedback file for sentiment & risk analysis")

    with tab4:
        recs = []
        if profit < 0: recs.append("🔴 RISK: Cost > Revenue. Action: Reduce cost 15%")
        else: recs.append("🟢 OPPORTUNITY: Profit healthy. Action: Expand market")
        recs.append(f"Scenario Impact: Growth {growth_rate}%, Cost {cost_change}% -> Projected Profit ${(total_sales*(1+growth_rate/100) - total_cost*(1+cost_change/100)):,.0f}")
        recs.append("Customer: Fix negative feedback themes, use positive for marketing")
        for r in recs: st.write(r)
        st.markdown(f"**Executive Summary:** Revenue ${total_sales:,.0f}, Profit ${profit:,.0f}. Trend shows {'growth' if change>0 else 'decline'}. Recommendation: Focus on data-driven decisions.")

else:
    st.warning("Upload sales_financial_data.csv created in CELL 3 to see magic!")
    try:
        st.dataframe(pd.read_csv("sales_financial_data.csv").head())
    except: st.write("Run CELL 3 first")
