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
    1. Fetch images with 'submitted' status from DB.
    2.generate prompts for images
    3. For each image, download bytes, decode to image, and process.
    4. Count and report results.
    """
    db = SupabaseManager()
    submitted_records = db.fetch_submitted_images()
    
    if not submitted_records:
        print("No images with 'submitted' status found.")
        return
    # Load your templates from prompts.json
    import json
    with open("prompts.json", "r") as f:
        templates = json.load(f)["templates"]
    ###function to assign prompt to images
    assign_prompts_to_images(submitted_records,templates)
 
    
    
    # Initialize counters as requested
    blur_count = 0
    good_count = 0
    
    # Store comparisons for popups
    comparisons = []
    
    print(f"Processing {len(submitted_records)} 'submitted' images...")
    
    for record in submitted_records:
        # Assuming either 'image_url' or 'filepath' column exists in submitted_records
        # Based on Data Annotation/src/database.py it looks like it's stored in some column
        # Let's check for common names like 'filepath' or 'image_url'
        image_path = record.get('image_url') or record.get('filepath') or record.get('path')
        
        if not image_path:
            continue
            
        # Download bytes
        image_bytes = db.download_image(image_path)
        
        if image_bytes:
            # Decode to cv2 image
            try:
                # Use PIL to safely open bytes then convert to NumPy
                nparr = np.frombuffer(image_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if img is None:
                    continue

                # Step 1: Preprocessing steps (Resize + Normalize)
                # Resize and normalize for potentially future tasks (returned, but not used now as per requirement)
                normalized_img = resize_and_normalize(img)
                
                # Step 2: Blur Detection
                is_blurry, has_bright_spot, _, _ = detect_blur_and_bright_spot(img, blur_threshold)
                
                # Report as requested: print number of blur images detected : and number of good images.
                if is_blurry:
                    blur_count += 1
                    # Apply filter
                    sharpened = sharpen_image(img)
                    # Store comparison for later
                    comparisons.append({
                        "original": img.copy(),
                        "sharpened": sharpened,
                        "path": image_path
                    })
                else:
                    good_count += 1
                    
            except Exception as e:
                print(f"Error processing image {image_path}: {e}")
                continue
    #split fetch_submitted_images but doesnot store anywhere
    train_records,test_records=train_test_split(submitted_records)
    # Final summary output as requested
    print("-" * 50)
    print(f"Preprocessing completed.")
    print(f"Number of blur images detected : {blur_count}")
    print(f"Number of good images : {good_count}")
    print("-" * 50)

    # Show popups for blurry images after entire code ends
    if comparisons:
        print(f"Showing comparison popups for {len(comparisons)} blurry images...")
        for comp in comparisons:
            # Stack images horizontally for side-by-side view
            # (Resize for easier viewing if necessary)
            h, w = comp["original"].shape[:2]
            scale = 600 / max(h, w)
            orig_small = cv2.resize(comp["original"], (int(w * scale), int(h * scale)))
            sharp_small = cv2.resize(comp["sharpened"], (int(w * scale), int(h * scale)))
            
            # Combine
            combined = np.hstack((orig_small, sharp_small))
            
            # Add labels
            cv2.putText(combined, "Original (Blur)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(combined, "Sharpened", (int(w * scale) + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Show window
            window_name = f"Blur Fix: {os.path.basename(comp['path'])}"
            cv2.imshow(window_name, combined)
            print(f"Displaying {window_name}. Press any key to see next or ESC to close all.")
            
            key = cv2.waitKey(0)
            cv2.destroyWindow(window_name)
            if key == 27: # ESC key
                break
        
        cv2.destroyAllWindows()

if __name__ == "__main__":
    process_submitted_images()
