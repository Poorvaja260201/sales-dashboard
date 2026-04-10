from modules.data_loader import load_data
from modules.ai_insights import generate_insights
from modules.anomaly_detection import detect_anomalies

import pandas as pd

# -------------------------------
# SAVE OUTPUTS FOR TABLEAU
# -------------------------------

def save_outputs(df, insights):
    df.to_csv("data/processed_data.csv", index=False)

    insights_df = pd.DataFrame({
        "Insight": insights
    })

    insights_df.to_csv("data/ai_insights.csv", index=False)

# -------------------------------
# MAIN PIPELINE (FOR TABLEAU)
# -------------------------------

def run_pipeline():
    df = load_data()

    insights = generate_insights(df)
    df = detect_anomalies(df)

    save_outputs(df, insights)

    print("✅ Data + Insights saved for Tableau")

# -------------------------------
# RUN PIPELINE
# -------------------------------

if __name__ == "__main__":
    run_pipeline()
