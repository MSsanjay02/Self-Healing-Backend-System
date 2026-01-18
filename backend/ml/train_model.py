import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
import os


CSV_URL = "http://127.0.0.1:8000/export/csv?limit=1000"


def main():
    print("✅ Loading dataset from backend CSV export...")

    df = pd.read_csv(CSV_URL)

    # Keep only features we need for ML
    features = df[["cpu_usage", "memory_usage"]]

    print("✅ Dataset shape:", features.shape)
    print("✅ Sample data:")
    print(features.head())

    # Train Isolation Forest (Anomaly detection)
    model = IsolationForest(
        n_estimators=200,
        contamination=0.2,  # assume 5% points are anomalies
        random_state=42
    )

    print("🧠 Training Isolation Forest model...")
    model.fit(features)

    # Create folder if not exists
    os.makedirs("ml", exist_ok=True)

    # Save model
    model_path = "ml/isolation_forest_model.pkl"
    joblib.dump(model, model_path)

    print(f"✅ Model saved at: {model_path}")


if __name__ == "__main__":
    main()
