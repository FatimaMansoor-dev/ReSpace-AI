import cv2
import numpy as np
import io
import os
from PIL import Image
from src.utils.db_manager import SupabaseManager
from src.utils.image_processor import resize_and_normalize, detect_blur_and_bright_spot, sharpen_image
from src.utils.data_splitter import train_test_split
from src.utils.prompt_assigner import assign_prompts_to_images

def process_submitted_images(blur_threshold=250.0):
    """
    Main preprocessing flow:
    1. Fetch images from 'annotated_images' table.
    2. Resize, Normalize, and De-blur images.
    3. Save results to 'preprocessed_images' table.
    """
    db = SupabaseManager()
    submitted_records = db.fetch_annotated_images() 
    
    if not submitted_records:
        print("No records found in annotated_images table.")
        return

    # Initialize counters
    blur_count = 0
    good_count = 0
    processed_count = 0
    
    print(f"Processing {len(submitted_records)} annotated images...")
    
    for record in submitted_records:
        record_id = record.get('id')
        image_path = record.get('image_url') or record.get('filepath') or record.get('path')
        
        if not image_path:
            continue
            
        print(f"Processing image: {image_path}")
        image_bytes = db.download_image(image_path)
        
        if image_bytes:
            try:
                # Decode to cv2 image
                nparr = np.frombuffer(image_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if img is None:
                    print(f"Failed to decode image: {image_path}")
                    continue

                # 1. Blur Detection & Sharpening (De-blurring)
                is_blurry, has_bright_spot, _, _ = detect_blur_and_bright_spot(img, blur_threshold)
                
                final_img = img
                if is_blurry:
                    blur_count += 1
                    final_img = sharpen_image(img) # De-blur
                    print(f"Image {image_path} detected as blurry, applied sharpening.")
                else:
                    good_count += 1

                # 2. Resizing & Normalization
                # resize_and_normalize returns a float32 array in [0, 1] range
                # If we need to save the processed image itself, we would upload final_img to Supabase Storage first.
                preprocessed_img = resize_and_normalize(final_img)

                # 3. Save to preprocessed_images table (Minimal: ID and URL only)
                db.save_preprocessed_image(record_id, image_path)
                processed_count += 1
                    
            except Exception as e:
                print(f"Error processing image {image_path}: {e}")
                continue

    # Final summary output
    print("-" * 50)
    print(f"Preprocessing completed.")
    print(f"Total processed: {processed_count}")
    print(f"Number of blur images detected (and sharpened): {blur_count}")
    print(f"Number of good images: {good_count}")
    print("-" * 50)

if __name__ == "__main__":
    process_submitted_images()

