def generate_sql(query):

    query = query.lower()

    # -----------------------
    # QUARTERS
    # -----------------------
    if "q1" in query:
        return """
        SELECT SUM(Revenue) as total_revenue
        FROM sales
        WHERE strftime('%m', Date) IN ('01','02','03')
        """

    elif "q2" in query:
        return """
        SELECT SUM(Revenue) as total_revenue
        FROM sales
        WHERE strftime('%m', Date) IN ('04','05','06')
        """

    elif "q3" in query:
        return """
        SELECT SUM(Revenue) as total_revenue
        FROM sales
        WHERE strftime('%m', Date) IN ('07','08','09')
        """

    elif "q4" in query:
        return """
        SELECT SUM(Revenue) as total_revenue
        FROM sales
        WHERE strftime('%m', Date) IN ('10','11','12')
        """

    elif "quarter" in query:
        return """
        SELECT 
            CASE 
                WHEN strftime('%m', Date) IN ('01','02','03') THEN 'Q1'
                WHEN strftime('%m', Date) IN ('04','05','06') THEN 'Q2'
                WHEN strftime('%m', Date) IN ('07','08','09') THEN 'Q3'
                WHEN strftime('%m', Date) IN ('10','11','12') THEN 'Q4'
            END as Quarter,
            SUM(Revenue) as total_revenue
        FROM sales
        GROUP BY Quarter
        ORDER BY Quarter
        """

    # -----------------------
    # COUNTRY REVENUE
    # -----------------------
    elif ("country" in query or "countries" in query) and "revenue" in query:
        return """
        SELECT Country, SUM(Revenue) as total_revenue
        FROM sales
        GROUP BY Country
        ORDER BY total_revenue DESC
        """

    # -----------------------
    # TOP PRODUCTS
    # -----------------------
    elif "top product" in query or "top 5" in query or "best product" in query:
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
    elif "total revenue" in query or "overall revenue" in query:
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
    elif "monthly" in query or "trend" in query or "over time" in query:
        return """
        SELECT strftime('%Y-%m', Date) as month, SUM(Revenue) as revenue
        FROM sales
        GROUP BY month
        ORDER BY month
        """

    # -----------------------
    # AVERAGE ORDER VALUE
    # -----------------------
    elif "average order" in query:
        return """
        SELECT AVG(Revenue) as avg_order_value
        FROM sales
        """

    # -----------------------
    # FALLBACK (IMPORTANT 🔥)
    # -----------------------
    else:
        return None
