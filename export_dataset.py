import os
import json
import requests
from concurrent.futures import ThreadPoolExecutor
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
EXPORT_DIR = os.path.join(ROOT_DIR, "examples", "dataset")
IMAGES_DIR = os.path.join(EXPORT_DIR, "images")
METADATA_FILE = os.path.join(EXPORT_DIR, "metadata.jsonl")
BUCKET_NAME = "Augmented Images"

# Create directories
os.makedirs(IMAGES_DIR, exist_ok=True)

def download_file_authenticated(bucket, filename, local_path):
    """Download a file using the Supabase Client to handle authentication and private buckets."""
    try:
        data = supabase.storage.from_(bucket).download(filename)
        if data:
            with open(local_path, 'wb') as f:
                f.write(data)
            return True
        return False
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
        return False

def generate_prompt_from_metadata(rec):
    """Reconstruct prompt from metadata fields."""
    room = rec.get("room_type", "room")
    theme = rec.get("color_theme", "neutral style")
    palette = rec.get("color_palette", "varied colors")
    use = rec.get("use_case", "general use")
    lighting = rec.get("lighting", "natural lighting")
    furniture = rec.get("furniture", [])
    
    if isinstance(furniture, list) and furniture:
        furniture_str = ", ".join(furniture)
    elif isinstance(furniture, str) and furniture:
        furniture_str = furniture
    else:
        furniture_str = "modern furniture"
        
    return f"A {theme} {room} for {use}, featuring a {palette} palette, {lighting}, and {furniture_str}."

def process_single_image(args):
    """Worker function for threading."""
    rec, meta_map, count_id = args
    original_id = rec.get("original_id")
    image_filename = rec.get("image_url")
    aug_type = rec.get("aug_type")
    
    meta = meta_map.get(original_id)
    if not meta:
        return None
    
    caption = generate_prompt_from_metadata(meta)
    
    local_filename = f"{aug_type}_{count_id:04d}_{image_filename}"
    local_path = os.path.join(IMAGES_DIR, local_filename)
    
    if download_file_authenticated(BUCKET_NAME, image_filename, local_path):
        return {
            "image": f"images/{local_filename}",
            "caption": caption
        }
    else:
        print(f"Failed to download from Storage: {image_filename}")
        return None

def main():
    print(f"🚀 Starting multi-threaded export to {EXPORT_DIR}...")
    
    try:
        # 1. Fetch ALL augmented images with pagination
        # Supabase/Postgrest usually defaults to 1000 limit per request.
        all_aug_records = []
        page_size = 1000
        offset = 0
        
        print("Fetching augmented image records from database...")
        while True:
            response = supabase.table("augmented_images").select("*").range(offset, offset + page_size - 1).execute()
            data = response.data
            if not data:
                break
            all_aug_records.extend(data)
            if len(data) < page_size:
                break
            offset += page_size
            
        if not all_aug_records:
            print("No augmented images found in database.")
            return

        # 2. Check what is already downloaded (to enable resuming)
        existing_images = set()
        if os.path.exists(IMAGES_DIR):
            existing_images = set(os.listdir(IMAGES_DIR))
            
        # Filter records that aren't downloaded yet or missing in metadata
        # We'll re-process metadata map logic to ensure accuracy
        
        # 2. Fetch metadata from annotated_images
        print("Fetching metadata from 'annotated_images' to build prompts...")
        meta_res = supabase.table("annotated_images").select("*").execute()
        meta_map = {r["id"]: r for r in meta_res.data}

        # Also try 'interior_images' if 'annotated_images' doesn't cover all IDs
        print("Checking 'interior_images' for remaining metadata...")
        int_res = supabase.table("interior_images").select("*").execute()
        for r in int_res.data:
            if r["id"] not in meta_map:
                meta_map[r["id"]] = r

        print(f"Total Database Records: {len(all_aug_records)} | Metadata available: {len(meta_map)}")
        
        # 3. Prepare tasks for missing OR partial downloads
        tasks = []
        skipped_count = 0
        
        # Determine existing files on disk for fast lookup
        files_on_disk = set(os.listdir(IMAGES_DIR)) if os.path.exists(IMAGES_DIR) else set()

        for i, rec in enumerate(all_aug_records):
            image_filename = rec.get("image_url")
            aug_type = rec.get("aug_type")
            local_filename = f"{aug_type}_{i:04d}_{image_filename}"
            local_path = os.path.join(IMAGES_DIR, local_filename)
            
            # CHECK: Only skip if file exists AND has content (is not 0 bytes)
            if local_filename in files_on_disk and os.path.getsize(local_path) > 0:
                skipped_count += 1
                continue
                
            tasks.append((rec, meta_map, i))

        if skipped_count > 0:
            print(f"⏭️ Skipping {skipped_count} valid images already found on disk.")

        if not tasks:
            print("All images already downloaded. Updating metadata.jsonl as a precaution...")
            # We skip downloading but still regenerate metadata.jsonl from existing folder
            # to be safe, but typically running the thread pool on empty tasks just finishes.
        
        # 4. Use ThreadPoolExecutor for concurrent downloads
        metadata_results = []
        # If resuming, we might want to preserve old metadata or just overwrite it entirely based on IMAGES_DIR
        # For simplicity, we overwrite metadata.jsonl with what's actually in the folder + new downloads
        
        MAX_THREADS = 10 
        print(f"Downloading {len(tasks)} remaining images using {MAX_THREADS} threads...")
        
        # We switch back to 'w' for metadata to ensure it perfectly matches the final disk state
        with open(METADATA_FILE, "w") as f:
            # First, add existing images to metadata.jsonl if they exist and we have meta
            if skipped_count > 0:
                print("Logging existing images to metadata...")
                for i, rec in enumerate(all_aug_records):
                    image_filename = rec.get("image_url")
                    aug_type = rec.get("aug_type")
                    local_filename = f"{aug_type}_{i:04d}_{image_filename}"
                    if local_filename in existing_images:
                        meta = meta_map.get(rec.get("original_id"))
                        if meta:
                            caption = generate_prompt_from_metadata(meta)
                            f.write(json.dumps({"image": f"images/{local_filename}", "caption": caption}) + "\n")
                f.flush()

            # Then download the rest
            with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
                for result in executor.map(process_single_image, tasks):
                    if result:
                        f.write(json.dumps(result) + "\n")
                        f.flush()
                        metadata_results.append(result)
                        if len(metadata_results) % 10 == 0:
                            print(f"New Downloads: {len(metadata_results)} images...")
            
        print(f"\n✅ Success! Dataset is ready in {EXPORT_DIR}")

    except Exception as e:
        print(f"An error occurred during export: {e}")

if __name__ == "__main__":
    main()
