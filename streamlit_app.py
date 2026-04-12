import pandas as pd
import streamlit as st
import plotly.express as px
import requests
from io import BytesIO
import sys
import os

sys.path.append(os.path.abspath("modules"))

from modules.sql_generator import generate_sql
from modules.sql_executor import run_sql
from smart_ai import smart_ai_analyst

# -----------------------
# GROQ SETUP
# -----------------------
from groq import Groq

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def query_huggingface(prompt):
    try:
        chat_completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a smart business data analyst."},
                {"role": "user", "content": prompt}
            ],
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ {str(e)}"


def explain_results(prompt, data):
    full_prompt = f"""
    You are a business data analyst.

    Question: {prompt}
    Data: {data}

    Give 2-3 short business insights.
    """

    try:
        return query_huggingface(full_prompt)
    except Exception as e:
        return f"⚠️ {str(e)}"

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

# Download
output = BytesIO()
filtered_df.to_excel(output, index=False, engine='openpyxl')

st.download_button(
    "📥 Download Excel",
    data=output.getvalue(),
    file_name="sales.xlsx"
)

# -----------------------
# METRICS
# -----------------------

st.subheader("📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Revenue", f"${filtered_df['Revenue'].sum():,.0f}")
col2.metric("Profit", f"${filtered_df['Profit'].sum():,.0f}")
col3.metric("Orders", len(filtered_df))
col4.metric("Avg Revenue", f"${filtered_df['Revenue'].mean():,.0f}")

# -----------------------
# CHART
# -----------------------

st.subheader("📈 Monthly Trend")

trend = filtered_df.groupby('Month')['Revenue'].sum().reset_index()

# ✅ FIX: correct month order
month_order = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

trend["Month"] = pd.Categorical(trend["Month"], categories=month_order, ordered=True)
trend = trend.sort_values("Month")

fig = px.line(trend, x='Month', y='Revenue', markers=True)
st.plotly_chart(fig, use_container_width=True)

# -----------------------
# AI INSIGHTS (1)
# -----------------------

st.subheader("Insights")

question_options = [
    "What is total revenue?",
    "Which product generates the most revenue?",
    "What is the profit trend?",
    "Which country performs best?",
    "What are the top 5 products?",
    "How does revenue change month by month?",
    "Is there any sales drop recently?",
    "How does Q1 revenue look?",
    "How does Q2 revenue look?",
    "How does Q3 revenue look?",
    "How does Q4 revenue look?",
    "Compare revenue across all quarters"
]

selected_question = st.selectbox(
    "Choose a business question",
    question_options,
    key="insights_1"
)

final_question = selected_question  # 👈 only dropdown now

if st.button("Generate Insights", key="btn_1"):

    grouped_data = filtered_df.groupby(['Country','Product']).sum(numeric_only=True)

    result = explain_results(final_question, grouped_data.to_string())

    if "⚠️" in result:
        st.warning(result)
    else:
        st.success("Insights generated successfully!")
        st.write(result)


# -----------------------
# AI CHAT
# -----------------------

st.subheader("💬 Ask AI Analyst")

user_input = st.text_input("Ask anything:")

if user_input:

    sql_query = generate_sql(user_input)

    if sql_query:
        result = run_sql(sql_query)

        st.session_state.last_question = user_input
        st.session_state.last_result = result

        st.dataframe(result)

        explanation = explain_results(
            user_input,
            result.head(10).to_string()
        )

        st.write("### 🤖 Explanation")
        st.write(explanation)

    else:
        answer = smart_ai_analyst(user_input, filtered_df)
        st.success(answer)

# -----------------------
# TOP PRODUCTS
# -----------------------

st.subheader("🏆 Top 5 Products")

top_products = (
    filtered_df.groupby("Product")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
)

st.bar_chart(top_products)
