import joblib
import pandas as pd

MODEL_FILE = "behavior_model.pkl"
DATA_FILE = "behavior_dataset.csv"


def main():
    model = joblib.load(MODEL_FILE)
    df = pd.read_csv(DATA_FILE)

    X = df.drop(columns=["risk", "user"], errors="ignore")
    X = X.select_dtypes(include=["number"]).fillna(0)

    if hasattr(model, "feature_names_in_"):
        X = X.reindex(columns=model.feature_names_in_, fill_value=0)

    predictions = model.predict(X)

    print("\n------ TEST RESULTS ------")
    for i in range(len(X)):
        actual = df.iloc[i]["risk"] if "risk" in df.columns else "Unknown"
        print(f"Row {i+1}: Actual = {actual}, Predicted = {predictions[i]}")
    print("--------------------------")


if __name__ == "__main__":
    main()