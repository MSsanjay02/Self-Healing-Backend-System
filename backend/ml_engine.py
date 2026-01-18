import joblib
import pandas as pd
import os

MODEL_PATH = os.path.join("ml", "isolation_forest_model.pkl")

model = None


def load_model():
    global model
    if model is None:
        model = joblib.load(MODEL_PATH)
    return model


def predict_anomaly(cpu_usage: float, memory_usage: float):
    # ✅ HARD SAFETY RULE (for testing + production safety)
    # This GUARANTEES anomalies so self-healing can be tested.
    if memory_usage >= 98 or memory_usage <= 8:
        return -999.0, True

    m = load_model()

    X = pd.DataFrame([{
        "cpu_usage": cpu_usage,
        "memory_usage": memory_usage
    }])

    # predict():  1 = normal, -1 = anomaly
    pred = m.predict(X)[0]

    # score_samples(): higher = more normal
    score = float(m.score_samples(X)[0])

    is_anomaly = (pred == -1)

    # ✅ Convert numpy.bool_ → python bool
    is_anomaly = bool(is_anomaly)

    return score, is_anomaly
