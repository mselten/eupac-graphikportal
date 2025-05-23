import pandas as pd
import requests
import re
import time


# Define allowed categories
ALLOWED_CATEGORIES = {
    "military",
    "spirituality",
    "female_representation",
    "everyday_life",
    "historical_people",
    "landscape"
}

def chat_with_model(prompt, token):
    # Your existing API call logic
    url = "http://cadmus.fel.zcu.cz/api/chat/completions"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
        "model": "qwen3:30b-a3b",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=20)
        response.raise_for_status()
        assistant_response = response.json()['choices'][0]['message']['content']

        # Clean response: remove XML tags and extra spaces
        assistant_response = re.sub(r'<.*?>', '', assistant_response).strip()

        # Split and filter categories
        categories = [cat.strip() for cat in assistant_response.split(';')]
        valid_categories = [cat for cat in categories if cat in ALLOWED_CATEGORIES]

        # Return only valid categories or 'other'
        if valid_categories:
            return ';'.join(valid_categories)
        else:
            return "other"

    except Exception as e:
        print(f"⚠️ Error: {e}")
        return "other"

# Generate prompt for LLM
def generate_prompt(row):
    """
    Formats the prompt for the LLM based on row data.
    """
    return f"""
\\no_think
{row['title']}
{row['objectDescription']}
{row['subject']}
I gave you title, description and subjects of painting.
Based on this information decide what categories does this painting belong to. Choose only from these categories below:
- military
- spirituality
- female_representation
- historical_people
- landscape
Not any other category, once again only: military, spirituality, female_representation, everyday_life, historical_people, landscape.
You can choose one or more. If none of the categories above makes sense reply with "other".
Reply only with list of categories separated by ; no other text should be in reply.
"""

# Main function
def main():
    file_path = '../../output_csv/bremen_data_V4_translated.csv'
    cache_path = 'category-cache.csv'
    output_path = '../../output_csv/bremen_data_V5_categories.csv'
    token = "sk-57c28363b8b24cab9bfabdaff5bcff71"  # Your API token

    # Load original data
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return

    # Initialize new column
    if 'custom_category' not in df.columns:
        df['custom_category'] = ''

    # Load cache if exists
    try:
        cache_df = pd.read_csv(cache_path, index_col=0)
        # Update existing categories
        for idx in cache_df.index:
            if 'custom_category' in cache_df.columns:
                df.loc[idx, 'custom_category'] = cache_df.loc[idx, 'custom_category']
    except Exception as e:
        print(f"⚠️ Cache not found or invalid: {e}")

    # Process rows
    processed_count = 0
    total_rows = len(df)
    print(f"🔄 Starting processing {total_rows} rows...")

    for index, row in df.iterrows():
        # Skip if category already exists
        if pd.isna(df.loc[index, 'custom_category']) or df.loc[index, 'custom_category'] == '':
            print(f"🔄 Processing row {index + 1}/{total_rows}")
            prompt = generate_prompt(row)
            response = chat_with_model(prompt, token)
            df.loc[index, 'custom_category'] = response
            print(f"🎨 Row {index + 1} Category: {response}")
            processed_count += 1

            if processed_count % 1000 == 0:
                df.to_csv(cache_path, index=True)
                print(f"💾 Saved cache after {processed_count} rows")

    # Save final result
    df.to_csv(output_path, index=False)
    print(f"✅ Processing completed and saved to {output_path}")

if __name__ == "__main__":
    main()