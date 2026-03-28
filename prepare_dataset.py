import os
import pandas as pd
import numpy as np

DATASET_FOLDER = "Data"
OUTPUT_FILE = "behavior_dataset.csv"


def safe_read_tsv(path):
    try:
        return pd.read_csv(path, sep="\t")
    except Exception:
        try:
            return pd.read_csv(path)
        except Exception:
            return pd.DataFrame()


def clean_dataframe(df):
    if df.empty:
        return df

    df = df.loc[:, ~df.columns.astype(str).str.contains("^Unnamed", case=False)]
    df.columns = [str(col).strip() for col in df.columns]
    
    # Try to convert "Time" to datetime if it exists
    if "Time" in df.columns:
        df["Time"] = pd.to_datetime(df["Time"], errors="coerce")
    elif "Press_Time" in df.columns:
        df["Press_Time"] = pd.to_datetime(df["Press_Time"], errors="coerce")
    
    return df


def find_file_by_keyword(folder, keyword, extension=".tsv"):
    if not os.path.exists(folder):
        return None

    for file in os.listdir(folder):
        file_lower = file.lower()
        if keyword.lower() in file_lower and file_lower.endswith(extension):
            return os.path.join(folder, file)

    return None


def get_numeric_features(df, prefix):
    features = {}

    if df.empty:
        return features

    numeric_df = df.select_dtypes(include=[np.number]).copy()

    if numeric_df.empty:
        return features

    for col in numeric_df.columns:
        features[f"{prefix}_{col}_mean"] = numeric_df[col].mean()
        features[f"{prefix}_{col}_std"] = numeric_df[col].std() if len(numeric_df[col]) > 1 else 0
        features[f"{prefix}_{col}_min"] = numeric_df[col].min()
        features[f"{prefix}_{col}_max"] = numeric_df[col].max()

    features[f"{prefix}_rows"] = len(df)
    return features


def map_stress_val_to_risk(stress_val_str):
    stress_val_str = str(stress_val_str).lower()
    if "stressed" in stress_val_str:
        return "HIGH"
    elif "neutral" in stress_val_str:
        return "MEDIUM"
    elif "good" in stress_val_str or "great" in stress_val_str:
        return "LOW"
    return "MEDIUM"


def extract_label_for_chunk(label_df, chunk_start, chunk_end, user_name):
    if label_df.empty or "Time" not in label_df.columns:
        return "MEDIUM"

    mask = (label_df["Time"] >= chunk_start) & (label_df["Time"] <= chunk_end)
    relevant_labels = label_df.loc[mask]

    if relevant_labels.empty:
        past_labels = label_df.loc[label_df["Time"] <= chunk_end]
        if not past_labels.empty:
            relevant_labels = past_labels.tail(1)
        else:
            relevant_labels = label_df.head(1)

    if "Stress_Val" in relevant_labels.columns:
        stress_values = relevant_labels["Stress_Val"].dropna()
        if not stress_values.empty:
            most_common = stress_values.mode().iloc[0]
            return map_stress_val_to_risk(most_common)

    numeric_df = relevant_labels.select_dtypes(include=[np.number])
    if not numeric_df.empty:
        avg_val = numeric_df.mean().mean()
        if avg_val < 4:
            return "LOW"
        elif avg_val < 8:
            return "MEDIUM"
        else:
            return "HIGH"

    return "MEDIUM"


def extract_user_features(user_folder, user_name):
    all_chunks_features = []
    
    keystrokes_file = find_file_by_keyword(user_folder, "keystrokes")
    mousedata_file = find_file_by_keyword(user_folder, "mousedata")
    mouse_speed_file = find_file_by_keyword(user_folder, "mouse_mov_speed")
    inactivity_file = find_file_by_keyword(user_folder, "inactivity")
    activewindows_file = find_file_by_keyword(user_folder, "activewindows")
    usercondition_file = find_file_by_keyword(user_folder, "usercondition")

    dfs = {}
    
    file_map = {
        "keystrokes": keystrokes_file,
        "mousedata": mousedata_file,
        "mouse_speed": mouse_speed_file,
        "inactivity": inactivity_file,
        "activewindows": activewindows_file,
    }

    for prefix, path in file_map.items():
        if path is not None:
            df = safe_read_tsv(path)
            dfs[prefix] = clean_dataframe(df)
        else:
            dfs[prefix] = pd.DataFrame()

    label_df = pd.DataFrame()
    if usercondition_file is not None:
        label_df = safe_read_tsv(usercondition_file)
        label_df = clean_dataframe(label_df)
    
    base_df_name = "mousedata"
    if dfs["mousedata"].empty:
        base_df_name = "keystrokes" if not dfs["keystrokes"].empty else "activewindows"
        
    base_df = dfs.get(base_df_name, pd.DataFrame())
    
    if base_df.empty:
        return []

    time_col = "Time" if "Time" in base_df.columns else "Press_Time"
    
    if time_col not in base_df.columns:
        return []

    base_df = base_df.dropna(subset=[time_col]).sort_values(by=time_col)
    
    chunk_size = 500 
    num_chunks = max(1, len(base_df) // chunk_size)

    for i in range(num_chunks):
        start_idx = i * chunk_size
        end_idx = min((i + 1) * chunk_size, len(base_df))
        
        chunk_base = base_df.iloc[start_idx:end_idx]
        if chunk_base.empty:
            continue
            
        chunk_start_time = chunk_base[time_col].min()
        chunk_end_time = chunk_base[time_col].max()
        
        features = {"user": user_name, "chunk_id": i}
        
        for prefix, df in dfs.items():
            if df.empty:
                continue
                
            t_col = "Time" if "Time" in df.columns else ("Press_Time" if "Press_Time" in df.columns else None)
            if t_col:
                mask = (df[t_col] >= chunk_start_time) & (df[t_col] <= chunk_end_time)
                chunk_df = df.loc[mask]
                features.update(get_numeric_features(chunk_df, prefix))
            else:
                features.update(get_numeric_features(df.head(0), prefix)) 

        features["risk"] = extract_label_for_chunk(label_df, chunk_start_time, chunk_end_time, user_name)
        
        all_chunks_features.append(features)

    return all_chunks_features


def main():
    all_rows = []

    if not os.path.exists(DATASET_FOLDER):
        print(f"Dataset folder not found: {DATASET_FOLDER}")
        return

    for user_name in os.listdir(DATASET_FOLDER):
        user_path = os.path.join(DATASET_FOLDER, user_name)

        if os.path.isdir(user_path):
            print(f"Processing: {user_name}")
            user_rows = extract_user_features(user_path, user_name)
            all_rows.extend(user_rows)

    if not all_rows:
        print("No data extracted.")
        return

    df = pd.DataFrame(all_rows)
    df = df.fillna(0)

    df.to_csv(OUTPUT_FILE, index=False)

    print("\nDataset prepared successfully.")
    print(f"Saved as: {OUTPUT_FILE}")
    print("Shape:", df.shape)

    if "risk" in df.columns:
        print("\nRisk value counts:")
        print(df["risk"].value_counts())

    print("\nPreview:")
    print(df.head())


if __name__ == "__main__":
    main()