import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared import init_supabase, download_image as common_download
from src.config import TABLE_NAME

class DatabaseManager:
    def __init__(self):
        self.client = init_supabase()

    def fetch_pending_images(self, username=None):
        """Fetch records where status is null and optionally assigned to a user."""
        try:
            query = self.client.table(TABLE_NAME).select("*").is_("status", "null")
            if username:
                query = query.eq("assigned_to", username)
            
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"Error fetching pending images: {e}")
            return []

    def download_image(self, file_path, bucket_name="Raw Images"):
        """Downloads image data directly from Supabase storage."""
        return common_download(self.client, file_path, bucket_name)

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

    def get_annotated_count(self, username=None):
        """Returns total count of records marked as 'submitted' for a specific user (or all)."""
        try:
            query = self.client.table(TABLE_NAME).select("id").ilike("status", "submitted")
            if username:
                query = query.eq("assigned_to", username)
            
            response = query.execute()
            
            count = len(response.data) if response.data else 0
            print(f"DEBUG: get_annotated_count found {count} records matching status 'submitted' (user: {username})")
            
            # If still 0, let's log what statuses DO exist to help debugging
            if count == 0:
                sample = self.client.table(TABLE_NAME).select("status").limit(5).execute()
                print(f"DEBUG: Sample statuses in DB: {[r.get('status') for r in sample.data] if sample.data else 'No data'}")
                
            return count
        except Exception as e:
            print(f"Error getting annotated count: {e}")
            return 0

    def get_room_counts(self, username=None):
        """Returns counts for each room type for records marked as 'submitted'."""
        try:
            query = self.client.table(TABLE_NAME).select("room_type").ilike("status", "submitted")
            if username:
                query = query.eq("assigned_to", username)
            
            response = query.execute()
            
            counts = {}
            if response.data:
                for record in response.data:
                    room = record.get("room_type")
                    if room:
                        counts[room] = counts.get(room, 0) + 1
            
            return counts
        except Exception as e:
            print(f"Error getting room counts: {e}")
            return {}
