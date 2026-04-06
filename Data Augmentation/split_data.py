import random
import json
import os
from src.utils.aug_db_manager import AugDbManager

def main():
    print("Connecting to database...")
    db = AugDbManager()
    
    # Fetch all preprocessed images, ignoring whether they were already augmented
    records = db.fetch_preprocessed_images(skip_augmented=False)
    
    if not records:
        print("No preprocessed images found in the database. Ensure database is populated.")
        return

    # Extract IDs
    all_ids = [r["id"] for r in records]
    
    # Shuffle for a random split
    random.seed() # ensures a fresh reshuffle on every run
    random.shuffle(all_ids)
    
    # Calculate 80/20 split
    split_index = int(0.8 * len(all_ids))
    train_ids = all_ids[:split_index]
    test_ids = all_ids[split_index:]
    
    split_data = {
        "train": train_ids,
        "test": test_ids
    }
    
    # Save locally
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "train_test_split.json")
    with open(output_path, "w") as f:
        json.dump(split_data, f, indent=4)
        
    print(f"Data successfully split and saved to {output_path}")
    print(f"Total Images: {len(all_ids)}")
    print(f"Train Set   : {len(train_ids)} (80%)")
    print(f"Test Set    : {len(test_ids)} (20%)")

if __name__ == "__main__":
    main()
