from supabase import create_client, Client
from src.config import SUPABASE_URL, SUPABASE_KEY, TABLE_NAME

class DatabaseManager:
    def __init__(self):
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    def fetch_pending_images(self):
        """Fetch records where status is null."""
        try:
            response = self.client.table(TABLE_NAME).select("*").is_("status", "null").execute()
            return response.data
        except Exception as e:
            print(f"Error fetching pending images: {e}")
            return []

    def download_image(self, file_path, bucket_name="Raw Images"):
        """Downloads image data directly from Supabase storage."""
        try:
            # Handle if the DB contains a full URL instead of just a path
            # URLs often encode spaces as %20
            clean_bucket = bucket_name.replace(" ", "%20")
            
            if "storage/v1/object/public/" in file_path:
                # Extract part after bucket name, handling both literal and encoded bucket names
                if f"/{bucket_name}/" in file_path:
                    file_path = file_path.split(f"/{bucket_name}/")[-1]
                elif f"/{clean_bucket}/" in file_path:
                    file_path = file_path.split(f"/{clean_bucket}/")[-1]
            
            # Decode URL characters just in case it's still encoded
            import urllib.parse
            actual_path = urllib.parse.unquote(file_path)
            
            return self.client.storage.from_(bucket_name).download(actual_path)
        except Exception as e:
            print(f"Error downloading image from path '{file_path}' (resolved as '{actual_path if 'actual_path' in locals() else 'N/A'}'): {e}")
            return None

    def submit_annotation(self, record_id, data: dict):
        """Mark record as submitted and store structured fields."""
        try:
            print(f"DEBUG: Submitting structured data for ID: {record_id}")
            update_payload = {
                "room_type": data.get("room"),
                "color_theme": data.get("color_theme"),
                "use_case": data.get("use_case"),
                "lighting": data.get("lighting"),
                "color_palette": data.get("color_palette"),
                "furniture": data.get("furniture"), # Expected to be a list
                "status": "submitted"
            }
            res = self.client.table(TABLE_NAME).update(update_payload).eq("id", record_id).execute()
            print(f"DEBUG: Supabase update response: {res.data}")
            return True
        except Exception as e:
            print(f"Error submitting annotation: {e}")
            return False

    def discard_image(self, record_id):
        """Mark record as discarded."""
        try:
            self.client.table(TABLE_NAME).update({
                "status": "discarded"
            }).eq("id", record_id).execute()
            return True
        except Exception as e:
            print(f"Error discarding image: {e}")
            return False
