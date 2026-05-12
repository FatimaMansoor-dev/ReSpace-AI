import os
import sys
import urllib.parse

# Add project root to sys.path for shared utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from shared import init_supabase, download_image as common_download

AUGMENTED_BUCKET   = "Augmented Images"
AUGMENTED_TABLE    = "augmented_images"
PREPROCESSED_TABLE = "preprocessed_images"


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
