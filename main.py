from fastapi import FastAPI
import pandas as pd
import glob

app = FastAPI()

print("AI model is starting...")

# =========================
# LOAD & PROCESS DATA
# =========================

def process_files():
    excel_files = glob.glob("*.xlsx")
    csv_files = glob.glob("*.csv")

    all_files = excel_files + csv_files
    all_data = []

    for file in all_files:
        print(f"Processing file: {file}")

        if file.endswith(".xlsx"):
            df = pd.read_excel(file, header=None)
        else:
            df = pd.read_csv(file, header=None)

        # Find UL1, UL2, UL3 row
        header_row = None
        for i, row in df.iterrows():
            if set(["UL1", "UL2", "UL3"]).issubset(set(row.values)):
                header_row = i
                break

        if header_row is None:
            continue

        df.columns = df.iloc[header_row]
        df = df[(header_row + 1):]
        df = df[["UL1", "UL2", "UL3"]]

        df = df.apply(pd.to_numeric, errors="coerce")
        df = df.dropna(how="all")

        if df.empty:
            continue

        def lane_status(val):
            if val == 0:
                return "Free"
            elif 0 < val < 22:
                return "In use"
            else:
                return "Occupied"

        for ul in ["UL1", "UL2", "UL3"]:
            df[f"{ul}_status"] = df[ul].apply(lane_status)

        all_data.append(df)

    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()


DATA = process_files()

# =========================
# API ENDPOINTS
# =========================

@app.get("/")
def home():
    return {"status": "API running", "rows_loaded": len(DATA)}


@app.get("/predict")
def predict():
    """
    Returns ONLY ONE prediction (UL1, UL2, UL3)
    """
    if DATA.empty:
        return {"error": "No valid data found"}

    latest = DATA.iloc[-1]

    return {
        "UL1": latest["UL1"],
        "UL2": latest["UL2"],
        "UL3": latest["UL3"],
        "UL1_status": latest["UL1_status"],
        "UL2_status": latest["UL2_status"],
        "UL3_status": latest["UL3_status"]
    }

