import pandas as pd
import streamlit as st
import plotly.express as px
import requests
from modules.ai_explainer import explain_results
from modules.ai_insights import generate_insights
from modules.sql_generator import generate_sql
from modules.sql_executor import run_sql
from modules.llama_explainer import ask_llama

# -----------------------
# CHAT MEMORY
# -----------------------

if "last_question" not in st.session_state:
    st.session_state.last_question = None

if "last_result" not in st.session_state:
    st.session_state.last_result = None
# -----------------------
# PAGE CONFIG
# -----------------------
st.set_page_config(page_title="Sales AI Assistant", layout="wide")

st.title("📊 Sales Analytics Assistant")

# -----------------------
# LOAD DATA
# -----------------------
df = pd.read_csv("data/sales_data.csv")

df['Date'] = pd.to_datetime(df['Date'])
df['Month'] = df['Date'].dt.month_name()
df['Year'] = df['Date'].dt.year

# -----------------------
# SIDEBAR
# -----------------------
st.sidebar.header("Filters")

selected_country = st.sidebar.selectbox(
    "Select Country",
    df['Country'].unique()
)

filtered_df = df[df['Country'] == selected_country]

from io import BytesIO
output = BytesIO()
filtered_df.to_excel(output, index=False, engine='openpyxl')
excel_data = output.getvalue()

st.download_button(
    label="📥 Download Excel File",
    data=excel_data,
    file_name="sales_data.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# -----------------------
# METRIC FUNCTIONS
# -----------------------
def total_revenue(data):
    return f"${data['Revenue'].sum():,}"

def total_profit(data):
    return f"${data['Profit'].sum():,}"

def top_product(data):
    return data.groupby('Product')['Revenue'].sum().idxmax()

def detect_sales_drop(data):
    trend = data.groupby(['Year', 'Month'])['Revenue'].sum().pct_change().dropna()
    if len(trend) == 0:
        return "Not enough data"

    latest = trend.iloc[-1]
    return f"{'📉 Drop' if latest < 0 else '📈 Growth'}: {round(latest*100,2)}%"

def top_5_products(data):
    return data.groupby('Product')['Revenue'].sum().sort_values(ascending=False).head(5)

def simple_forecast(data):
    trend = data.groupby(['Year', 'Month'])['Revenue'].sum()
    return trend.tail(3).mean() if len(trend) > 0 else 0


# -----------------------
# DASHBOARD SECTION
# -----------------------
st.subheader("📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Revenue", total_revenue(filtered_df))
col2.metric("Profit", total_profit(filtered_df))
col3.metric("Orders", f"{len(filtered_df):,}")
col4.metric("Forecast", f"${simple_forecast(filtered_df):,.0f}")


# -----------------------
# CHART
# -----------------------
st.subheader("📈 Monthly Sales Trend")

month_order = [
    'January','February','March','April','May','June',
    'July','August','September','October','November','December'
]

trend = filtered_df.groupby('Month')['Revenue'].sum().reset_index()
trend['Month'] = pd.Categorical(trend['Month'], categories=month_order, ordered=True)
trend = trend.sort_values('Month')

fig = px.line(trend, x='Month', y='Revenue', markers=True)
st.plotly_chart(fig, use_container_width=True)


# -----------------------
# INSIGHTS
# -----------------------
st.subheader("📊 Quick Insights")

st.write(f"🏆 Top Product: {top_product(filtered_df)}")
st.write(detect_sales_drop(filtered_df))


# -----------------------
# AI INSIGHTS BUTTON
# -----------------------
st.subheader("🤖 AI Insights")

if st.button("Generate AI Insights", key="ai_insights_btn"):
    insights = generate_insights(df, selected_country)

    for i in insights:
        st.write(f"• {i}")


# -----------------------
# LLaMA QUICK ASK
# -----------------------
st.subheader("🧠 Ask LLaMA")

if st.button("Why is revenue down in Q4?", key="llama_btn"):
    answer = ask_llama("Why is revenue down in Q4?")
    st.write(answer)


# -----------------------
# MAIN AI CHAT (BEST PART 🔥)
# -----------------------
# -----------------------
# AI CHAT (WITH MEMORY)
# -----------------------

st.subheader("💬 Ask AI Analyst (NL → SQL + AI)")

user_input = st.text_input("Ask a business question:")

if user_input:

    # 🔥 HANDLE FOLLOW-UP QUESTION
    if user_input.lower() in ["why", "explain", "why is that"]:
        
        if st.session_state.last_result is not None:

            with st.spinner("Analyzing previous result..."):
                explanation = explain_results(
                    st.session_state.last_question,
                    st.session_state.last_result
                )

            st.write("### 🤖 AI Explanation")
            st.write(explanation)

        else:
            st.write("⚠️ Ask a question first.")

    else:
        # Normal flow
        sql_query = generate_sql(user_input)

        if sql_query:
            result = run_sql(sql_query)

            # Save memory
            st.session_state.last_question = user_input
            st.session_state.last_result = result

            st.write("### 📊 Query Result")
            st.dataframe(result)

            # Auto explanation
            with st.spinner("Analyzing results..."):
                explanation = explain_results(user_input, result)

            st.write("### 🤖 AI Explanation")
            st.write(explanation)

        else:
            st.write("❌ Sorry, I don’t understand that question yet.")

# -----------------------
# TOP PRODUCTS TABLE
# -----------------------
st.subheader("🏆 Top 5 Products")

st.dataframe(top_5_products(filtered_df))
