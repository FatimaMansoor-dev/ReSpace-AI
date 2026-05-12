import cv2
import numpy as np
import io
import os
from src.utils.aug_db_manager import AugDbManager
from src.utils.augmentor import augment_image


def run_augmentation():
    """
    Full augmentation pipeline:

    1. Fetch unprocessed records from 'preprocessed_images' table.
    2. Download each original image from Supabase Storage.
    3. Apply Scaling+Crop and Horizontal Flip augmentations.
    4. Encode results as JPEG and upload to 'Augmented Images' bucket.
    5. Record metadata in the 'augmented_images' table.
    6. Print a summary report.

    SQL to create the required table (run once in Supabase SQL Editor):

        CREATE TABLE public.augmented_images (
            id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            original_id UUID NOT NULL REFERENCES preprocessed_images(id),
            image_url   TEXT NOT NULL,
            aug_type    TEXT NOT NULL,  -- 'scaled_crop' or 'horizontal_flip'
            created_at  TIMESTAMPTZ DEFAULT now()
        );

        -- Also create the Storage bucket manually in Supabase Dashboard:
        -- Bucket name: "Augmented Images" (public or private, your choice)
    """
    db = AugDbManager()

    records = db.fetch_preprocessed_images(skip_augmented=True)
    if not records:
        print("No new preprocessed images to augment.")
        return

    # -------- TRAIN/TEST FILTER --------
    import json
    import os
    split_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "train_test_split.json")
    if os.path.exists(split_file):
        with open(split_file, "r") as f:
            splits = json.load(f)
            train_ids = set(splits.get("train", []))
        
        print(f"Active split metadata restricted to 'train' set only.")
        records = [r for r in records if r["id"] in train_ids]
        
        if not records:
            print("No remaining images to augment from the train split.")
            return
    else:
        print("[WARN] train_test_split.json not found! Run 'python split_data.py' first.")
        print("Falling back to augmenting ALL images...")
    # -----------------------------------
    total_processed   = 0
    total_augmented   = 0
    failed_downloads  = 0
    failed_uploads    = 0

    print(f"\nStarting augmentation for {len(records)} image(s)...\n" + "-" * 50)

    for record in records:
        record_id  = record.get("id")
        image_path = record.get("image_url") or record.get("filepath") or record.get("path")

        if not image_path:
            print(f"[SKIP] Record {record_id} has no image_url — skipping.")
            continue

        import re
        match = re.search(r'(\d+)', image_path)
        if match:
            num = int(match.group(1))
            normalized_path = f"{num:08d}.jpg"
            print(f"[INFO] Processing: {image_path} (Normalized to -> {normalized_path})")
            image_path = normalized_path
        else:
            print(f"[INFO] Processing: {image_path}")

        # 1. Download original image
        image_bytes = db.download_image(image_path)
        if not image_bytes:
            print(f"[WARN] Could not download {image_path}. Skipping.")
            failed_downloads += 1
            continue

        # 2. Decode to OpenCV array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img   = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            print(f"[WARN] Could not decode image bytes for {image_path}. Skipping.")
            failed_downloads += 1
            continue

        # 3. Apply augmentations (returns list of (array, suffix) tuples)
        augmented_variants = augment_image(img)

        # 4. Encode, upload, and record each variant
        base_name = os.path.splitext(os.path.basename(image_path))[0]

        for aug_array, suffix in augmented_variants:
            filename = f"{base_name}_{suffix}.jpg"

            # Encode as JPEG bytes
            success, buffer = cv2.imencode(".jpg", aug_array, [cv2.IMWRITE_JPEG_QUALITY, 95])
            if not success:
                print(f"[WARN] Failed to encode {filename}. Skipping.")
                failed_uploads += 1
                continue

            aug_bytes = buffer.tobytes()

            # Upload to Supabase Storage
            uploaded_url = db.upload_image_to_storage(aug_bytes, filename)
            if not uploaded_url:
                failed_uploads += 1
                continue

            # Save metadata to augmented_images table
            db.save_augmented_record(record_id, uploaded_url, suffix, record.get("prompt"))
            total_augmented += 1
            print(f"  [OK] Saved augmented variant: {filename} (type={suffix})")

        total_processed += 1

    # 5. Summary
    print("\n" + "-" * 50)
    print("Augmentation Complete!")
    print(f"  Original images processed : {total_processed}")
    print(f"  Augmented images generated: {total_augmented}")
    print(f"  Failed downloads          : {failed_downloads}")
    print(f"  Failed uploads            : {failed_uploads}")
    print("-" * 50)


if __name__ == "__main__":
    run_augmentation()
