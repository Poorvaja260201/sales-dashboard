def generate_sql(query):

    query = query.lower()

    # -----------------------
    # COUNTRY REVENUE
    # -----------------------
    if ("country" in query or "countries" in query) and "revenue" in query:
        return """
        SELECT Country, SUM(Revenue) as total_revenue
        FROM sales
        GROUP BY Country
        ORDER BY total_revenue DESC
        """

    # -----------------------
    # TOP PRODUCTS
    # -----------------------
    elif "top product" in query or "products" in query:
        return """
        SELECT Product, SUM(Revenue) as total_revenue
        FROM sales
        GROUP BY Product
        ORDER BY total_revenue DESC
        LIMIT 5
        """

    # -----------------------
    # TOTAL REVENUE
    # -----------------------
    elif "total revenue" in query:
        return """
        SELECT SUM(Revenue) as total_revenue
        FROM sales
        """

    # -----------------------
    # PROFIT
    # -----------------------
    elif "profit" in query:
        return """
        SELECT SUM(Profit) as total_profit
        FROM sales
        """

    # -----------------------
    # MONTHLY TREND
    # -----------------------
    elif "monthly" in query or "trend" in query:
        return """
        SELECT strftime('%Y-%m', Date) as month, SUM(Revenue) as revenue
        FROM sales
        GROUP BY month
        ORDER BY month
        """

    else:
        return None
