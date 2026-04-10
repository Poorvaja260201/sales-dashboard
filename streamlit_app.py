import pandas as pd
import streamlit as st
import plotly.express as px
import requests
from io import BytesIO
from modules.ai_insights import generate_insights
from modules.sql_generator import generate_sql
from modules.sql_executor import run_sql
from modules.llama_explainer import ask_llama
import sys
import os

sys.path.append(os.path.abspath("modules"))

from smart_ai import smart_ai_analyst

# -----------------------
# HUGGING FACE SETUP
# -----------------------

API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"

headers = {
    "Authorization": f"Bearer {st.secrets['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']}"
}

def explain_results(prompt, data):
    try:
        full_prompt = f"""
        You are a business data analyst.

        Question: {prompt}
        Data: {data}

        Give 2-3 short business insights.
        """

        response = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": full_prompt}
        )

        output = response.json()

        if isinstance(output, list):
            return output[0].get("generated_text", "No response")
        elif isinstance(output, dict) and "error" in output:
            return f"⚠️ {output['error']}"
        else:
            return str(output)

    except Exception:
        return "⚠️ AI insights temporarily unavailable."

# -----------------------
# SESSION MEMORY
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

# Download button
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
# METRICS
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

def simple_forecast(data):
    trend = data.groupby(['Year', 'Month'])['Revenue'].sum()
    return trend.tail(3).mean() if len(trend) > 0 else 0

# -----------------------
# DASHBOARD
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
# QUICK INSIGHTS
# -----------------------

st.subheader("📊 Quick Insights")

st.write(f"🏆 Top Product: {top_product(filtered_df)}")
st.write(detect_sales_drop(filtered_df))

# -----------------------
# AI INSIGHTS
# -----------------------

st.subheader("🤖 AI Insights")

question_options = [
    "What is total revenue?",
    "Which product generates the most revenue?",
    "What is the profit trend?",
    "Which country performs best?",
    "What are the top 5 products?",
    "How does revenue change month by month?",
    "Is there any sales drop recently?",

    # 👇 QUARTER QUESTIONS
    "How does Q1 revenue look?",
    "How does Q2 revenue look?",
    "How does Q3 revenue look?",
    "How does Q4 revenue look?",
    "Compare revenue across all quarters"
]

selected_question = st.selectbox(
    "Choose a business question",
    question_options
)

custom_question = st.text_input("Or type your own question")

final_question = custom_question if custom_question else selected_question

if st.button("Generate Insights"):
    result = explain_results(
        final_question,
        filtered_df.groupby(['Country','Product']).sum().to_string()
    )

    st.success("Insights generated successfully!")
    st.write(result)


# -----------------------
# AI CHAT (WITH MEMORY)
# -----------------------

st.subheader("💬 Ask AI Analyst")

user_input = st.text_input("Ask a business question:")

if user_input:

    if user_input.lower() in ["why", "explain", "why is that"]:

        if st.session_state.last_result is not None:

            with st.spinner("Analyzing previous result..."):
                explanation = explain_results(
                    st.session_state.last_question,
                    st.session_state.last_result.head(10).to_string()
                )

            st.write("### 🤖 AI Explanation")
            st.write(explanation)

        else:
            st.write("⚠️ Ask a question first.")

    else:
        sql_query = generate_sql(user_input)

        if sql_query:
            result = run_sql(sql_query)

            st.session_state.last_question = user_input
            st.session_state.last_result = result

            st.write("### 📊 Query Result")
            st.dataframe(result)

            with st.spinner("Analyzing results..."):
                explanation = explain_results(
                    user_input,
                    result.head(10).to_string()
                )

            st.write("### 🤖 AI Explanation")
            st.write(explanation)

       

sql_query = generate_sql(user_input)

if sql_query:
    result = run_sql(sql_query)

    st.session_state.last_question = user_input
    st.session_state.last_result = result

    st.write("### 📊 Query Result")
    st.dataframe(result)

    with st.spinner("Analyzing results..."):
        explanation = explain_results(
            user_input,
            result.head(10).to_string()
        )

    st.write("### 🤖 AI Explanation")
    st.write(explanation)

else:
    # 🔥 fallback to smart AI
    answer = smart_ai_analyst(user_input, df)

    st.write("### 🤖 Smart AI Answer")
    st.success(answer)
# -----------------------
# TOP PRODUCTS
# -----------------------

st.subheader("🏆 Top 5 Products")

def top_5_products(df):
    df = df.copy()
    df["Product_clean"] = df["Product"].str.split(",").str[0]

    return (
        df.groupby("Product_clean")["Revenue"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
        .head(5)
    )

top_products = top_5_products(filtered_df)

st.bar_chart(
    top_products.set_index("Product_clean")["Revenue"]
)
