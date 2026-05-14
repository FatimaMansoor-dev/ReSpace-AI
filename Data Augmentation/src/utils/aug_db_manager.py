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
        Fetch specific records from preprocessed_images by their IDs.
        """
        try:
            response = self.client.table(PREPROCESSED_TABLE).select("*").in_("id", ids).execute()
            return response.data
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

    def save_augmented_record(self, original_id: str, image_url: str, aug_type: str,  prompt: str):
        """
        Insert a row into the augmented_images table.

        Args:
            original_id: UUID of the source record in preprocessed_images.
            image_url:   Filename / path in the Augmented Images bucket.
            aug_type:    'scaled_crop' or 'horizontal_flip'.
        """
        try:
            data = {
                "original_id": original_id,
                "image_url":   image_url,
                "aug_type":    aug_type,
                "prompt": prompt
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
                formatted_records.append({
                    "original_id": r["id"],
                    "image_url":   r.get("image_url") or r.get("filepath") or r.get("path"),
                    "prompt":      r.get("prompt")
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
