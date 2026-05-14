import os
import sys
import urllib.parse

# Add project root to sys.path for shared utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from shared import init_supabase, download_image as common_download

AUGMENTED_BUCKET   = "Augmented Images"
AUGMENTED_TABLE    = "augmented_images"
PREPROCESSED_TABLE = "preprocessed_images"
TEST_TABLE         = "test_images"
ANNOTATED_TABLE    = "annotated_images"


class AugDbManager:
    def __init__(self):
        self.client = init_supabase()

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def fetch_preprocessed_images(self, skip_augmented=True):
        """
        Fetch records from preprocessed_images.

        Args:
            skip_augmented: If True, exclude IDs already present in
                            augmented_images (incremental mode).

        Returns:
            List of record dicts.
        """
        try:
            response = self.client.table(PREPROCESSED_TABLE).select("*").execute()
            all_records = response.data

            if not skip_augmented or not all_records:
                return all_records

            # Get original_ids already augmented (avoid re-processing)
            aug_response = (
                self.client.table(AUGMENTED_TABLE)
                .select("original_id")
                .execute()
            )
            augmented_ids = {r["original_id"] for r in aug_response.data}

            unique = [r for r in all_records if r["id"] not in augmented_ids]
            
            # --- Merge with annotations ---
            if unique:
                unique_ids = [r["id"] for r in unique]
                ann_response = self.client.table(ANNOTATED_TABLE).select("*").in_("id", unique_ids).execute()
                ann_data = {r["id"]: r for r in ann_response.data}
                
                for r in unique:
                    ann = ann_data.get(r["id"], {})
                    r["annotation"] = {
                        "room_type": ann.get("room_type"),
                        "color_theme": ann.get("color_theme"),
                        "use_case": ann.get("use_case"),
                        "lighting": ann.get("lighting"),
                        "color_palette": ann.get("color_palette"),
                        "furniture": ann.get("furniture")
                    }
            # ------------------------------

            print(
                f"Incremental fetch: {len(all_records)} total preprocessed | "
                f"{len(augmented_ids)} already augmented | "
                f"{len(unique)} to process."
            )
            return unique

        except Exception as e:
            print(f"Error fetching preprocessed images: {e}")
            return []

    def fetch_records_by_ids(self, ids):
        """
        Fetch specific records from preprocessed_images and merge with annotation data.
        """
        try:
            # 1. Fetch from preprocessed_images
            response = self.client.table(PREPROCESSED_TABLE).select("*").in_("id", ids).execute()
            pre_records = response.data
            
            if not pre_records:
                return []

            # 2. Fetch corresponding annotations from annotated_images
            # We join on the 'id' field as confirmed by database mapping
            ann_response = self.client.table(ANNOTATED_TABLE).select("*").in_("id", ids).execute()
            ann_data = {r["id"]: r for r in ann_response.data}

            # 3. Merge
            for r in pre_records:
                ann = ann_data.get(r["id"], {})
                # Extract relevant annotation fields into a structured dict
                r["annotation"] = {
                    "room_type": ann.get("room_type"),
                    "color_theme": ann.get("color_theme"),
                    "use_case": ann.get("use_case"),
                    "lighting": ann.get("lighting"),
                    "color_palette": ann.get("color_palette"),
                    "furniture": ann.get("furniture")
                }
            
            return pre_records
        except Exception as e:
            print(f"Error fetching records by IDs: {e}")
            return []

    def download_image(self, file_path, bucket_name="Raw Images"):
        """
        Download raw image bytes from Supabase Storage using standardized shared utility.
        """
        return common_download(self.client, file_path, bucket_name)

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def upload_image_to_storage(self, image_bytes: bytes, filename: str) -> str | None:
        """
        Upload JPEG bytes to the 'Augmented Images' Supabase Storage bucket.

        Args:
            image_bytes: Raw JPEG bytes of the augmented image.
            filename:    Target filename in the bucket (e.g. '<id>_scaled_crop.jpg').

        Returns:
            The filename (used as image_url) on success, None on failure.
        """
        try:
            self.client.storage.from_(AUGMENTED_BUCKET).upload(
                path=filename,
                file=image_bytes,
                file_options={"content-type": "image/jpeg"},
            )
            print(f"Uploaded '{filename}' to '{AUGMENTED_BUCKET}' bucket.")
            return filename
        except Exception as e:
            print(f"Error uploading '{filename}': {e}")
            return None

    def save_augmented_record(self, original_id: str, image_url: str, aug_type: str,  prompt: str, annotation: dict = None):
        """
        Insert a row into the augmented_images table with individual annotation columns.
        """
        try:
            annotation = annotation or {}
            data = {
                "original_id":   original_id,
                "image_url":     image_url,
                "aug_type":      aug_type,
                "prompt":        prompt,
                "room_type":     annotation.get("room_type"),
                "color_theme":   annotation.get("color_theme"),
                "use_case":      annotation.get("use_case"),
                "lighting":      annotation.get("lighting"),
                "color_palette": annotation.get("color_palette"),
                "furniture":     annotation.get("furniture")
            }
            self.client.table(AUGMENTED_TABLE).insert(data).execute()
        except Exception as e:
            print(f"Error saving augmented record (id={original_id}, type={aug_type}): {e}")

    def save_test_records(self, records):
        """
        Bulk insert records into the test_images table.
        """
        try:
            formatted_records = []
            for r in records:
                ann = r.get("annotation") or {}
                formatted_records.append({
                    "original_id":   r["id"],
                    "image_url":     r.get("image_url") or r.get("filepath") or r.get("path"),
                    "prompt":        r.get("prompt"),
                    "room_type":     ann.get("room_type"),
                    "color_theme":   ann.get("color_theme"),
                    "use_case":      ann.get("use_case"),
                    "lighting":      ann.get("lighting"),
                    "color_palette": ann.get("color_palette"),
                    "furniture":     ann.get("furniture")
                })
            
            if formatted_records:
                self.client.table(TEST_TABLE).insert(formatted_records).execute()
                print(f"Successfully saved {len(formatted_records)} records to {TEST_TABLE}.")
        except Exception as e:
            print(f"Error saving test records: {e}")

    def clear_test_images(self):
        """
        Remove all records from test_images table.
        """
        try:
            # In Supabase, a delete without a filter might be restricted. 
            # We use a filter that matches everything if possible, or just catch the need for manual truncate.
            self.client.table(TEST_TABLE).delete().neq("image_url", "null").execute()
            print(f"Cleared {TEST_TABLE} table.")
        except Exception as e:
            print(f"Note: Could not clear {TEST_TABLE} automatically (might need manual TRUNCATE): {e}")
