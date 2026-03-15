from supabase import create_client, Client
import os
import sys

# Ensure Data Annotation folder is in sys.path to import its config
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.join(project_root, "Data Annotation"))

try:
    from src.config import SUPABASE_URL, SUPABASE_KEY, TABLE_NAME
except ImportError:
    # If standard import fails, try relative import if possible
    # Fallback to env variables if really needed, but let's assume standard works for now.
    raise ImportError("Could not find SUPABASE_URL and SUPABASE_KEY in Data Annotation/src/config.py")

class SupabaseManager:
    def __init__(self):
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.table_name = "annotated_images" # Use the table containing submitted images
        self.preprocessed_table = "preprocessed_images"

    def fetch_annotated_images(self, skip_processed=True):
        """Fetch all records from the annotated_images table, optionally skipping those already in preprocessed_images."""
        try:
            # 1. Get all images from annotated_images
            response = self.client.table(self.table_name).select("*").execute()
            all_records = response.data

            if not skip_processed or not all_records:
                return all_records

            # 2. Get IDs that have already been preprocessed
            processed_response = self.client.table(self.preprocessed_table).select("id").execute()
            processed_ids = {r['id'] for r in processed_response.data}

            # 3. Filter out records that are already in processed_ids
            # Ensure the comparison is done correctly (both UUID strings or objects)
            unique_records = [r for r in all_records if r['id'] not in processed_ids]
            
            print(f"Incremental Fetch: Found {len(all_records)} total, {len(unique_records)} remain after skipping {len(processed_ids)} already processed.")
            return unique_records
            
        except Exception as e:
            print(f"Error fetching annotated images: {e}")
            return []

    def save_preprocessed_image(self, record_id, image_url):
        """Save preprocessed image URL to the preprocessed_images table."""
        try:
            # Minimal record: only ID and URL
            data = {
                "id": record_id,
                "image_url": image_url
            }
            response = self.client.table(self.preprocessed_table).upsert(data).execute()
            return response.data
        except Exception as e:
            print(f"Error saving preprocessed image {record_id}: {e}")
            return None

    def download_image(self, file_path, bucket_name="Raw Images"):
        """Downloads raw image bytes from storage using Supabase SDK but with improved path handling."""
        try:
            import urllib.parse
            
            # 1. Clean up encoded spaces in bucket name for matching
            # Supabase URLs often use %20 for spaces
            clean_bucket = bucket_name.replace(" ", "%20")
            
            # 2. Extract relative path if a full URL was provided
            if "storage/v1/object/public/" in file_path:
                if f"/{bucket_name}/" in file_path:
                    file_path = file_path.split(f"/{bucket_name}/")[-1]
                elif f"/{clean_bucket}/" in file_path:
                    file_path = file_path.split(f"/{clean_bucket}/")[-1]
            
            # 3. Ensure the path is properly decoded before passing to Supabase SDK
            # The SDK handles its own encoding/networking, but if we pass it double-encoded
            # strings (like "folder%20name/img.jpg"), Supabase returns 400.
            actual_path = urllib.parse.unquote(file_path)
            
            # 4. Use the original SDK method which handles the auth and connection pooling
            # but wrap it to catch the specific timeout errors seen before.
            return self.client.storage.from_(bucket_name).download(actual_path)
            
        except Exception as e:
            print(f"Error downloading image from path '{file_path}': {e}")
            return None
