import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from root directory
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET_NAME = "Raw Images" 
TABLE_NAME = os.getenv("TABLE_NAME", "interior_images")

def sync_bucket_to_db():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print(f"Error: SUPABASE_URL or SUPABASE_KEY missing. (Checked path: {os.path.abspath(env_path)})")
        return

    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    print(f"Fetching existing images from database: {TABLE_NAME}...")
    try:
        # Fetch all existing image URLs to avoid per-file DB queries
        existing_res = supabase.table(TABLE_NAME).select("image_url").execute()
        existing_urls = {item['image_url'] for item in existing_res.data}
        print(f"Found {len(existing_urls)} existing images in database.")
    except Exception as e:
        print(f"Error fetching existing images: {e}")
        return

    print(f"Listing files in bucket: {BUCKET_NAME}...")
    all_files = []
    limit = 1000  # Larger limit for fewer requests
    offset = 0
    
    try:
        while True:
            # List files in the bucket with pagination
            res = supabase.storage.from_(BUCKET_NAME).list(options={
                'limit': limit,
                'offset': offset,
                'sortBy': {'column': 'name', 'order': 'asc'}
            })
            
            if not res:
                break
                
            all_files.extend(res)
            print(f"Fetched {len(all_files)} files so far...")
            
            if len(res) < limit:
                break
            
            offset += limit

        if not all_files:
            print("No files found in bucket.")
            return

        files_to_insert = []
        skipped_count = 0
        
        for file in all_files:
            file_name = file['name']
            
            # Skip folders and placeholders
            if file_name == '.emptyFolderPlaceholder' or file.get('id') is None:
                continue
            
            # Check if it has an image extension
            if not any(file_name.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                print(f"Skipping non-image file: {file_name}")
                continue
            
            # Check if already exists in our local set
            if file_name in existing_urls:
                skipped_count += 1
                continue
            
            files_to_insert.append({
                "image_url": file_name,
                "status": None
            })
            print(f"Queued: {file_name}")

        print(f"Total files in bucket: {len(all_files)}")
        print(f"Total skipped (already in DB): {skipped_count}")

        if files_to_insert:
            # Insert in batches of 1000 to be safe
            batch_size = 1000
            for i in range(0, len(files_to_insert), batch_size):
                batch = files_to_insert[i:i + batch_size]
                supabase.table(TABLE_NAME).insert(batch).execute()
                print(f"Successfully synced batch {i//batch_size + 1} ({len(batch)} images) to {TABLE_NAME}.")
        else:
            print("No new images to sync.")

    except Exception as e:
        print(f"Error during sync: {e}")

if __name__ == "__main__":
    sync_bucket_to_db()
