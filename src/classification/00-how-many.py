import pandas as pd

# Define the file path
file_path = '../../output_csv/bremen_data_V4_translated.csv'

# Load the CSV file into a DataFrame
try:
    df = pd.read_csv(file_path)
except Exception as e:
    print(f"Error reading the file: {e}")
    exit()

# Check if 'subject' and 'description' columns exist
if 'subject' not in df.columns or 'objectDescription' not in df.columns:
    print("The required columns 'subject' and 'description' are not present in the CSV file.")
    exit()

# Count rows where either 'subject' or 'description' is not empty
filled_rows = df[(df['subject'].notna()) | (df['objectDescription'].notna())]

# Calculate percentage
total_rows = len(df)
filled_percentage = (len(filled_rows) / total_rows) * 100 if total_rows > 0 else 0

# Output the result
print(f"Total rows: {total_rows}")
print(f"Rows with filled 'subject' or 'description': {len(filled_rows)}")
print(f"Percentage: {filled_percentage:.2f}%")