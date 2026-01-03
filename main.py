import pandas as pd
import glob

print("AI model is starting...")

try:
    # =========================
    # Step 1: Get all CSV & XLSX files
    # =========================
    excel_files = glob.glob("*.xlsx")
    csv_files = glob.glob("*.csv")

    all_files = excel_files + csv_files
    all_data = []

    for file in all_files:
        print(f"Processing file: {file}")
        
        # Read file without assuming headers
        if file.endswith(".xlsx"):
            df = pd.read_excel(file, header=None)
        else:
            df = pd.read_csv(file, header=None)
        
        # Find row with UL1, UL2, UL3
        header_row = None
        for i, row in df.iterrows():
            if set(['UL1','UL2','UL3']).issubset(set(row.values)):
                header_row = i
                break
        
        if header_row is None:
            print(f"Skipping {file}: UL1, UL2, UL3 not found.")
            continue

        # Set proper headers and keep only rows below
        df.columns = df.iloc[header_row]
        df = df[(header_row + 1):]
        df = df[['UL1', 'UL2', 'UL3']]

        # Convert to numeric
        df = df.apply(pd.to_numeric, errors='coerce')
        df = df.dropna(how='all')  # keep rows where at least one UL has a number

        if df.empty:
            print(f"Skipping {file}: no numeric data under UL1, UL2, UL3.")
            continue

        # =========================
        # Step 2: Determine lane status per UL
        # =========================
        def lane_status(val):
            if val == 0:
                return "Free"
            elif 0 < val < 22:
                return "In use"
            else:  # val >= 22
                return "Occupied, please move to green lane"

        for ul in ['UL1', 'UL2', 'UL3']:
            df[f'{ul}_status'] = df[ul].apply(lane_status)

        all_data.append(df)

    if all_data:
        # =========================
        # Step 3: Combine all data and save a single JSON
        # =========================
        final_output = pd.concat(all_data, ignore_index=True)
        final_output.to_json("all_lanes_status.json", orient="records")
        print("All files processed successfully! Output saved as all_lanes_status.json")
    else:
        print("No valid numeric data found in any file. No output generated.")

except Exception as e:
    print(f"AI model failed: {e}")
