import pandas as pd

# Define file paths
input_csv_path = 'output_csv/bremen_output_V2_with_placeOfBirth.csv'
output_csv_path = 'output_csv/bremen_data_V3.csv'

# Define columns to delete
columns_to_delete = [
    'rightsStatement', 
    'workID', 
    'repositoryName', 
    'recordID', 
    'recordLinks', 
    'recordMetadataDate', 
    'eventType', 
    'relatedWorkNotes', 
    'creditLine'
]

try:
    # Load the CSV file into a pandas DataFrame
    print(f"Loading {input_csv_path}...")
    df = pd.read_csv(input_csv_path)
    print("File loaded successfully.")

    # Identify which of the columns_to_delete actually exist in the DataFrame
    existing_columns_to_delete = [col for col in columns_to_delete if col in df.columns]
    missing_columns = [col for col in columns_to_delete if col not in df.columns]

    if missing_columns:
        print(f"Warning: The following specified columns were not found in the CSV and will be ignored: {', '.join(missing_columns)}")

    if existing_columns_to_delete:
        # Delete the specified columns
        print(f"Deleting columns: {', '.join(existing_columns_to_delete)}...")
        df.drop(columns=existing_columns_to_delete, inplace=True)
        print("Columns deleted successfully.")
    else:
        print("No columns to delete from the provided list were found in the CSV.")

    # Process 'displayMeasurements' column
    if 'displayMeasurements' in df.columns:
        print("Processing 'displayMeasurements' column...")
        # Extract measurements like "169 x 275 mm" from "Darstellung: 169 x 275 mm"
        # The .str[0] is used because extract returns a DataFrame
        df['displayMeasurements'] = df['displayMeasurements'].str.extract(r'(\d+\s*x\s*\d+\s*\w+)')[0]
        print("'displayMeasurements' column processed successfully.")
    else:
        print("Warning: Column 'displayMeasurements' not found, skipping processing.")

    # Save the modified DataFrame to a new CSV file
    print(f"Saving modified data to {output_csv_path}...")
    df.to_csv(output_csv_path, index=False)
    print(f"Successfully saved modified data to {output_csv_path}")

except FileNotFoundError:
    print(f"Error: The file {input_csv_path} was not found. Please check the file path.")
except Exception as e:
    print(f"An error occurred: {e}")
