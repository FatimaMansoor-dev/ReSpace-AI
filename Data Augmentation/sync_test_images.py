import json
import os
from src.utils.aug_db_manager import AugDbManager

def sync_test_to_db():
    """
    Reads the existing train_test_split.json and ensures all test images
    are stored in the 'test_images' table in the database.
    """
    db = AugDbManager()
    
    # 1. Load the existing split
    split_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "train_test_split.json")
    if not os.path.exists(split_file):
        print(f"[ERROR] {split_file} not found. Please run split_data.py first (or restore your JSON).")
        return

    with open(split_file, "r") as f:
        splits = json.load(f)
        test_ids = splits.get("test", [])

    if not test_ids:
        print("No test IDs found in the split file.")
        return

    print(f"Found {len(test_ids)} test IDs in local split file.")

    # 2. Clear existing test_images table to avoid duplicates
    db.clear_test_images()

    # 3. Fetch metadata for these IDs from preprocessed_images
    print(f"Fetching metadata for test images from database...")
    # Process in batches of 100 to avoid long query strings
    batch_size = 100
    all_test_records = []
    
    for i in range(0, len(test_ids), batch_size):
        batch_ids = test_ids[i:i + batch_size]
        records = db.fetch_records_by_ids(batch_ids)
        if records:
            all_test_records.extend(records)

    print(f"Retrieved {len(all_test_records)} records from database.")

    # 4. Save to test_images table
    if all_test_records:
        db.save_test_records(all_test_records)
        print("Sync complete!")
    else:
        print("No metadata found for the specified test IDs. Check if they exist in preprocessed_images.")

if __name__ == "__main__":
    sync_test_to_db()
