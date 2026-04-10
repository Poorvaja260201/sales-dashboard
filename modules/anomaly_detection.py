from sklearn.ensemble import IsolationForest

def detect_anomalies(df):
    model = IsolationForest(contamination=0.1, random_state=42)

    df['anomaly'] = model.fit_predict(
        df[['Revenue', 'Profit']]  # removed Quantity
    )

    return df
