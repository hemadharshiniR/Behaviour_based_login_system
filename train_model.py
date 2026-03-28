import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score

MODEL_FILE = "behavior_model.pkl"

# -------------------------------------------------------
# Feature columns MUST EXACTLY match what app.py sends:
#   hold, delay, typing_speed, clicks, distance
#
# Real-world value ranges (from browser JS tracking):
#   typing_speed  = totalKeys / (totalIntervalSeconds)
#                   normal typist on a short password ≈ 3–8 keys/sec
#                   slow / hesitant typist            ≈ 0.3–2 keys/sec
#                   bot / very fast                   ≈ 8–30 keys/sec
#
#   hold          = avg key-hold time in ms
#                   normal ≈ 80–160ms
#                   slow   ≈ 200–500ms
#
#   delay         = avg interval between successive keypresses in ms
#                   normal ≈ 100–250ms
#                   slow   ≈ 400–2000ms
#
#   clicks        = total mouse clicks on the page
#                   normal ≈ 1–4 (click username, click password, click submit)
#                   suspicious ≈ 8–30
#
#   distance      = total mouse distance in pixels
#                   normal ≈ 200–900px
#                   high   ≈ 1500–6000px
# -------------------------------------------------------
FEATURE_COLS = ["hold", "delay", "typing_speed", "clicks", "distance"]


def generate_synthetic_data(n_samples=900, seed=42):
    """
    Generate realistic synthetic data aligned with actual browser JS values.

    LOW    – confident, normal typist (legitimate user)
    MEDIUM – slower, hesitant typing (cautious / uncertain user)
    HIGH   – very slow, erratic behavior (attacker guess-typing or bot)
    """
    rng = np.random.default_rng(seed)
    rows = []

    samples_per_class = n_samples // 3

    # ── LOW risk ── confident, normal-speed typing (> 3.0 keys/sec)
    for _ in range(samples_per_class):
        rows.append({
            "hold":         rng.uniform(60,  120),   
            "delay":        rng.uniform(80,  150),   
            "typing_speed": rng.uniform(3.1,  10.0), 
            "clicks":       int(rng.integers(1, 4)),
            "distance":     rng.uniform(100, 600),
            "risk":         "LOW",
        })

    # ── MEDIUM risk ── hesitant/slow (1.0 - 3.0 keys/sec)
    for _ in range(samples_per_class):
        rows.append({
            "hold":         rng.uniform(120, 250),
            "delay":        rng.uniform(200, 500),
            "typing_speed": rng.uniform(1.0,  3.0),
            "clicks":       int(rng.integers(1, 6)),
            "distance":     rng.uniform(100, 1000),
            "risk":         "MEDIUM",
        })

    # ── HIGH risk ── suspicious/guessing (< 1.0 keys/sec)
    for _ in range(samples_per_class):
        rows.append({
            "hold":         rng.uniform(250, 800),
            "delay":        rng.uniform(500, 4000),
            "typing_speed": rng.uniform(0.01, 1.0),
            "clicks":       int(rng.integers(1, 15)),
            "distance":     rng.uniform(100, 4000),
            "risk":         "HIGH",
        })

    return pd.DataFrame(rows)


def main():
    print("Generating synthetic training data with real-world thresholds …")
    df = generate_synthetic_data()

    X = df[FEATURE_COLS]
    y = df["risk"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)

    print(f"\nAccuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%")
    
    # Calculate Multiclass ROC-AUC using One-Vs-Rest
    try:
        roc_auc = roc_auc_score(y_test, y_prob, multi_class='ovr')
        print(f"ROC-AUC (OvR): {roc_auc * 100:.2f}%")
    except Exception as e:
        print(f"ROC-AUC calculation skipped: {e}")

    print("\nClassification Report:\n")
    print(classification_report(y_test, y_pred, zero_division=0))

    # Show feature importances
    importances = dict(zip(FEATURE_COLS, model.feature_importances_))
    print("\nFeature Importances:")
    for feat, imp in sorted(importances.items(), key=lambda x: -x[1]):
        print(f"  {feat}: {imp:.3f}")

    joblib.dump(model, MODEL_FILE)
    print(f"\nModel saved as: {MODEL_FILE}")
    print("Training feature columns:", FEATURE_COLS)
    print("\nReal-world decision boundaries:")
    print("  LOW    -> typing_speed > 3.0 keys/sec  (normal, confident typing)")
    print("  MEDIUM -> typing_speed 1.0-3.0 keys/sec (slow, noticeable hesitation)")
    print("  HIGH   -> typing_speed < 1.0 keys/sec  (very slow, suspicious)")


if __name__ == "__main__":
    main()