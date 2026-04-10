def generate_insights(df, selected_country=None):
    insights = []

    # Revenue by country
    country_rev = df.groupby('Country')['Revenue'].sum()
    total_rev = country_rev.sum()

    if selected_country:
        selected_rev = country_rev[selected_country]
        share = round((selected_rev / total_rev) * 100, 2)

        insights.append(
            f"{selected_country} contributes {share}% of total revenue across all regions."
        )

    # Top country overall
    top_country = country_rev.idxmax()
    top_share = round((country_rev.max() / total_rev) * 100, 2)

    insights.append(
        f"{top_country} is the highest contributor with {top_share}% of total revenue."
    )

    # Product concentration
    product_rev = df.groupby('Product')['Revenue'].sum()
    top_product = product_rev.idxmax()
    product_share = round((product_rev.max() / product_rev.sum()) * 100, 2)

    insights.append(
        f"{top_product} drives {product_share}% of total revenue, indicating product concentration."
    )

    # Growth trend
    monthly = df.groupby(df['Date'].dt.to_period('M'))['Revenue'].sum()

    if len(monthly) > 2:
        growth = monthly.pct_change().dropna()
        latest = round(growth.iloc[-1] * 100, 2)

        insights.append(
            f"Latest monthly growth rate is {latest}%, showing {'decline' if latest < 0 else 'growth'}."
        )

    # Profitability
    margin = (df['Profit'].sum() / df['Revenue'].sum()) * 100

    insights.append(
        f"Overall profit margin is {round(margin,2)}%, indicating {'strong' if margin > 20 else 'moderate'} profitability."
    )

    return insights
