def generate_insights(df, question, selected_country=None):
    # Revenue by country
    country_rev = df.groupby('Country')['Revenue'].sum()
    total_rev = country_rev.sum()

    # Product revenue
    product_rev = df.groupby('Product')['Revenue'].sum()

    # Monthly trend
    monthly = df.groupby(df['Date'].dt.to_period('M'))['Revenue'].sum()

    # Profit margin
    margin = (df['Profit'].sum() / df['Revenue'].sum()) * 100

    # ------------------ QUESTION LOGIC ------------------

    if question == "Revenue share of selected country":
        if selected_country:
            selected_rev = country_rev[selected_country]
            share = round((selected_rev / total_rev) * 100, 2)
            return f"{selected_country} contributes {share}% of total revenue."
        else:
            return "Please select a country."

    elif question == "Top performing country":
        top_country = country_rev.idxmax()
        top_share = round((country_rev.max() / total_rev) * 100, 2)
        return f"{top_country} is the top contributor with {top_share}% of total revenue."

    elif question == "Top product":
        top_product = product_rev.idxmax()
        product_share = round((product_rev.max() / product_rev.sum()) * 100, 2)
        return f"{top_product} contributes {product_share}% of total revenue."

    elif question == "Monthly growth trend":
        if len(monthly) > 2:
            growth = monthly.pct_change().dropna()
            latest = round(growth.iloc[-1] * 100, 2)
            return f"Latest monthly growth rate is {latest}%."
        else:
            return "Not enough data for growth analysis."

    elif question == "Profit margin":
        return f"Overall profit margin is {round(margin, 2)}%."

    elif question == "Total revenue":
        return f"Total revenue is {round(total_rev, 2)}."

    else:
        return "I don't understand the question."
