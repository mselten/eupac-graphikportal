import pandas as pd
import json
from deep_translator import GoogleTranslator
import asyncio
from tqdm import tqdm

semaphore = asyncio.Semaphore(4)

async def translate_batch(batch_str, cache):
    print(f"[BATCH] Sending batch: {batch_str}")
    async with semaphore:
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: GoogleTranslator(source='de', target='en').translate(batch_str)
            )
            print(f"[BATCH] Received translated batch: {result}")
            return result
        except Exception as e:
            print(f"[ERROR] Error translating batch: {e}")
            return batch_str

async def translate_cell(cell, cache):
    if isinstance(cell, float) and pd.isna(cell):
        return ''
    if not isinstance(cell, str):
        cell = str(cell)
    parts = [part.strip() for part in cell.split(';')]
    translated_parts = []
    parts_to_translate = []

    # Check cache for existing translations
    for part in parts:
        if part in cache:
            print(f"[CACHE] Using cached translation for: {part}")
            translated_parts.append(cache[part])
        else:
            parts_to_translate.append(part)

    # Split into batches of 20
    batches = [parts_to_translate[i:i+20] for i in range(0, len(parts_to_translate), 20)]
    for batch in batches:
        batch_str = '; '.join(batch)
        translated_batch = await translate_batch(batch_str, cache)
        translated_batch_parts = translated_batch.split('; ')
        # Update cache with individual translations
        for original, translated in zip(batch, translated_batch_parts):
            cache[original] = translated
        # Add to translated parts
        translated_parts.extend(translated_batch_parts)

    # Reconstruct the translated cell
    translated_cell = '; '.join(translated_parts)

    # Process the final cell: lowercase, split by ';', remove duplicates
    translated_cell = translated_cell.lower()
    terms = [term.strip() for term in translated_cell.split(';')]
    unique_terms = list(set(terms))  # remove duplicates
    translated_cell = '; '.join(unique_terms)

    return translated_cell

async def translate_column(df, column_name, cache):
    print(f"[COLUMN] Starting translation of column '{column_name}'")
    tasks = [translate_cell(row[column_name], cache) for _, row in df.iterrows()]
    results = await asyncio.gather(*tasks)  # Preserves order
    print(f"[COLUMN] Completed translation of column '{column_name}'")
    return results

async def save_cache_periodically(cache, cache_file):
    """Save the cache every 5 seconds."""
    while True:
        try:
            with open(cache_file, 'w') as f:
                json.dump(cache, f)
            print("[INFO] Cache saved every 5 seconds.")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"[ERROR] Failed to save cache: {e}")
            await asyncio.sleep(10)  # Wait before retrying

async def main():
    cache_file = '../output/translation_cache.json'
    cache = {}

    try:
        # Load cache
        try:
            with open(cache_file, 'r') as f:
                cache = json.load(f)
        except FileNotFoundError:
            cache = {}

        # Start periodic cache saving
        save_task = asyncio.create_task(save_cache_periodically(cache, cache_file))

        # Load CSV and translate
        df = pd.read_csv('../output_csv/bremen_output.csv')
        print("Starting translation...")
        df['subject_translated'] = await translate_column(df, 'subject', cache)

        # Cancel the save task after translation completes
        save_task.cancel()
        try:
            await save_task
        except asyncio.CancelledError:
            print("[INFO] Cache save task cancelled.")

        # Save cache and CSV on success
        with open(cache_file, 'w') as f:
            json.dump(cache, f)
        df.to_csv('../output_csv/bremen_output_translated.csv', index=False)
        print("Translation completed and saved.")

    except KeyboardInterrupt:
        print("\n[INFO] Translation interrupted by user.")
        print("[INFO] Saving cache...")
        with open(cache_file, 'w') as f:
            json.dump(cache, f)
        print("[INFO] Cache saved. Exiting gracefully.")

    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")
        print("[INFO] Saving cache...")
        with open(cache_file, 'w') as f:
            json.dump(cache, f)
        print("[INFO] Cache saved. Re-raising error.")
        raise

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"[CRITICAL] Unexpected error: {e}")
        print("[INFO] Cache saved if possible.")