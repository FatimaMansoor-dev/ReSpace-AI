import os
import csv
import json
from supabase import create_client, Client
from dotenv import load_dotenv

# 1. Load Environment Variables
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(ROOT_DIR, ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: SUPABASE_URL or SUPABASE_KEY not found in .env file.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. Config
EXPORT_FILE = os.path.join(ROOT_DIR, "analysis_dataset.csv")
IMAGES_LOCAL_DIR = os.path.join("examples", "dataset", "images")

def format_furniture(furniture_data):
    """Formats furniture JSONB into a readable string for CSV."""
    if not furniture_data:
        return ""
    if isinstance(furniture_data, list):
        return ", ".join(furniture_data)
    if isinstance(furniture_data, dict):
        return json.dumps(furniture_data)
    return str(furniture_data)

def fetch_all_records(table_name):
    """Fetches all records from a Supabase table, bypassing the 1000 limit."""
    all_records = []
    start = 0
    limit = 1000
    
    while True:
        response = supabase.table(table_name).select("*").range(start, start + limit - 1).execute()
        records = response.data
        if not records:
            break
        
        all_records.extend(records)
        
        if len(records) < limit:
            break
            
        start += limit
        
    return all_records

def export_for_analysis():
    print("Fetching data from public.annotated_images and public.augmented_images...")
    
    # Query annotated_images which contains the most enriched metadata
    try:
        # Join annotated_images with augmented_images to get full dataset
        # We'll use a local mapping for files since augmented_images.image_url refers to bucket
        annotated_records = fetch_all_records("annotated_images")
        print(f"Fetched {len(annotated_records)} records from annotated_images")
        
        augmented_records = fetch_all_records("augmented_images")
        print(f"Fetched {len(augmented_records)} records from augmented_images")
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    if not annotated_records:
        print("No records found in annotated_images.")
        return

    # Create a lookup for annotated metadata by id
    # Since augmented_images.original_id references preprocessed_images.id,
    # and preprocessed_images.id references annotated_images.id
    metadata_lookup = {rec["id"]: rec for rec in annotated_records if rec.get("id")}

    # Define columns
    headers = [
        "id", 
        "original_id", 
        "room_type", 
        "color_theme", 
        "use_case", 
        "lighting", 
        "color_palette", 
        "furniture", 
        "status", 
        "aug_type",
        "processed_at",
        "image_url",
        "local_path"
    ]

    print(f"Exporting data to {EXPORT_FILE}...")
    
    # Get list of local files to match
    local_files = os.listdir(os.path.join(ROOT_DIR, IMAGES_LOCAL_DIR))
    
    with open(EXPORT_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        
        # 1. First, export augmented images if they match metadata
        for aug in augmented_records:
            orig_id = aug.get("original_id")
            meta = metadata_lookup.get(orig_id, {})
            
            # Find matching local file
            # Format in dir: {aug_type}_{some_index}_{orig_id_suffix}_{aug_type}.jpg
            # Or similar. Let's try to match by part of the filename.
            # Example: horizontal_flip_0001_00000014_horizontal_flip.jpg
            # Note: orig_id might be a UUID, but files seem to have a numeric ID.
            # If we can't match exactly, we'll try to find any file containing 'horizontal_flip' and a unique part.
            
            # The user gave an example: horizontal_flip_0001_00000014_horizontal_flip.jpg
            # Let's assume the local_path can be matched or we just list what's in the folder.
            
            # For now, let's map the augmented record
            row = {
                "id": aug.get("id"),
                "original_id": orig_id,
                "room_type": meta.get("room_type"),
                "color_theme": meta.get("color_theme"),
                "use_case": meta.get("use_case"),
                "lighting": meta.get("lighting"),
                "color_palette": meta.get("color_palette"),
                "furniture": format_furniture(meta.get("furniture")),
                "status": meta.get("status"),
                "aug_type": aug.get("aug_type"),
                "processed_at": aug.get("created_at"),
                "image_url": aug.get("image_url"),
            }
            
            # Match local file
            # Example filename: horizontal_flip_0001_00000014_horizontal_flip.jpg
            # image_url from db: 00000014_horizontal_flip.jpg
            match = None
            aug_image_url = aug.get("image_url")
            for filename in local_files:
                # Basic matching based on aug_type and checking if image_url fragment is in filename
                if aug_image_url and aug_image_url in filename:
                    match = filename
                    break 
            
            if match:
                row["local_path"] = os.path.join(IMAGES_LOCAL_DIR, match)
                # Remove matched file from list if it's a 1-to-1 mapping (optional)
                # local_files.remove(match) 
            else:
                row["local_path"] = "Not found locally"
            
            writer.writerow(row)

    print("Export complete.")

if __name__ == "__main__":
    export_for_analysis()
