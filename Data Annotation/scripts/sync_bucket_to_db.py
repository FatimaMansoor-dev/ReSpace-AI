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

    print(f"Listing files in bucket: {BUCKET_NAME}...")
    try:
        # List files in the bucket
        res = supabase.storage.from_(BUCKET_NAME).list()
        
        if not res:
            print("No files found in bucket.")
            return

        files_to_insert = []
        for file in res:
            file_name = file['name']
            
            # Skip folders and placeholders
            if file_name == '.emptyFolderPlaceholder' or file.get('id') is None or 'metadata' not in file:
                continue
            
            # Check if it has an image extension
            if not any(file_name.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                print(f"Skipping non-image file: {file_name}")
                continue
                
            # Use the path directly in the DB
            # We will generate the URL/Data on the fly in the app for security/privacy
            
            # Check if already exists to avoid duplicates
            existing = supabase.table(TABLE_NAME).select("id").eq("image_url", file_name).execute()
            
            if not existing.data:
                files_to_insert.append({
                    "image_url": file_name, # Storing just the name now
                    "status": None
                })
                print(f"Queued: {file_name}")
            else:
                print(f"Skipped (already in DB): {file_name}")

        if files_to_insert:
            supabase.table(TABLE_NAME).insert(files_to_insert).execute()
            print(f"Successfully synced {len(files_to_insert)} images to {TABLE_NAME}.")
        else:
            print("No new images to sync.")

    except Exception as e:
        print(f"Error during sync: {e}")

if __name__ == "__main__":
    sync_bucket_to_db()
