import pandas as pd

def smart_ai_analyst(question, df):
    q = question.lower()

    # ---------------- BASIC KPIs ----------------
    if "total revenue" in q:
        return f"Total revenue is {df['Revenue'].sum():,.2f}"

    if "top product" in q or "most revenue product" in q:
        top = df.groupby('Product')['Revenue'].sum().idxmax()
        return f"Top product is {top}"

    if "top country" in q or "best country" in q:
        top = df.groupby('Country')['Revenue'].sum().idxmax()
        return f"Top country is {top}"

    if "profit margin" in q:
        margin = (df['Profit'].sum() / df['Revenue'].sum()) * 100
        return f"Profit margin is {margin:.2f}%"

    # ---------------- TIME ANALYSIS ----------------
    if "monthly" in q or "month" in q:
        monthly = df.groupby(df['Date'].dt.to_period('M'))['Revenue'].sum()
        return monthly.to_string()

    if "trend" in q:
        monthly = df.groupby(df['Date'].dt.to_period('M'))['Revenue'].sum()
        growth = monthly.pct_change().dropna()
        return f"Latest growth: {growth.iloc[-1]*100:.2f}%"

    # ---------------- QUARTERS ----------------
    if "q1" in q:
        return get_quarter(df, 1)
    if "q2" in q:
        return get_quarter(df, 2)
    if "q3" in q:
        return get_quarter(df, 3)
    if "q4" in q:
        return get_quarter(df, 4)

    if "quarter" in q:
        df['Quarter'] = df['Date'].dt.to_period('Q')
        return df.groupby('Quarter')['Revenue'].sum().to_string()

    return "I understood the question but need more logic added for this one."
