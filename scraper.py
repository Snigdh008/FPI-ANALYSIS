import pandas as pd
import glob

# Find all cleaned CSV files
csv_files = sorted(glob.glob("*_cleaned.csv"))

# List to store extracted data
data_list = []

# Month mapping for different abbreviations
month_corrections = {
    "January": "Jan", "February": "Feb", "March": "Mar", "April": "Apr",
    "May": "May", "June": "Jun", "July": "Jul", "August": "Aug",
    "September": "Sep", "October": "Oct", "November": "Nov", "December": "Dec",
    "JUNE": "Jun", "JULY": "Jul"  # Handling uppercase names like "JUNE15"
}

# Loop through each cleaned CSV file
for file in csv_files:
    try:
        # Extract Date from filename (e.g., April152020_cleaned.csv → 15-Apr-2020)
        date_str = file.replace("_cleaned.csv", "")

        # Fix month abbreviation issues
        for full_month, short_month in month_corrections.items():
            if full_month in date_str:
                date_str = date_str.replace(full_month, short_month)

        # Convert to standard date format
        formatted_date = pd.to_datetime(date_str, format="%b%d%Y", errors='coerce')

        # Skip if the date couldn't be parsed
        if pd.isna(formatted_date):
            print(f"⚠️ Skipping {file} (Invalid date format)")
            continue

        # Keep only data from 2020 to 2025
        if formatted_date.year < 2020 or formatted_date.year > 2025:
            continue  # Skip data outside range

        # Format date as 15-Jan-20
        formatted_date_str = formatted_date.strftime("%d-%b-%y")

        # Read the CSV file
        df = pd.read_csv(file)

        # Ensure at least 3 columns exist
        if df.shape[1] < 3:
            print(f"⚠️ Skipping {file} (Not enough columns)")
            continue

        # Extract relevant columns: Sector & AUC for that date
        df_final = df.iloc[:, [0, 2]].copy()

        # Rename columns
        df_final.columns = ["Sector", "AUC as on Date"]
        df_final.insert(0, "Date", formatted_date_str)

        # Store the formatted data
        data_list.append(df_final)

    except Exception as e:
        print(f"❌ Error processing {file}: {e}")

# Combine all data into one DataFrame
if data_list:
    final_df = pd.concat(data_list, ignore_index=True)

    # Convert Date column to datetime format and sort
    final_df["Date"] = pd.to_datetime(final_df["Date"], format="%d-%b-%y")
    final_df = final_df.sort_values(by="Date")

    # Convert Date column back to 15-Jan-20 format
    final_df["Date"] = final_df["Date"].dt.strftime("%d-%b-%y")

    # Save to CSV
    final_df.to_csv("FPI_Data.csv", index=False)
    print("✅ Data sorted & saved in 'FPI_Data.csv'")
else:
    print("⚠️ No valid data found to process.")

