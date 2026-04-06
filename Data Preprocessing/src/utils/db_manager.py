import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from shared import init_supabase, download_image as common_download

class SupabaseManager:
    def __init__(self):
        self.client = init_supabase()
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
        """Downloads raw image bytes from storage using standardized shared utility."""
        return common_download(self.client, file_path, bucket_name)
