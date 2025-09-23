def  load_operation_list(operation_raw: str):
    return [op.strip() for op in operation_raw.split(",") if op.strip()]

def is_valid_serial(serial: str):
    return len(serial) == 22

def generate_csv(save_path, df: dict):
    import os, csv
    sn = df["SN Scanner"]
    filepath = os.path.join(save_path, f"LogResult_{sn}.csv")
    with open(filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(df.keys())  # Write header
        writer.writerow(df.values())  # Write values
    return  

def upload_result_to_fits(df):
    if df["Operation"] == "S500":
        print(df["Image Path"][0])
        return {
            "Top view": df["Image Path"][0],
            "Result": df["Final Result"]
        }