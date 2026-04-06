import os
import sys
import urllib.parse
from supabase import create_client, Client

# Share credentials from Data Annotation config
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
sys.path.append(os.path.join(project_root, "Data Annotation"))

try:
    from src.config import SUPABASE_URL, SUPABASE_KEY
except ImportError:
    raise ImportError(
        "Could not import credentials from 'Data Annotation/src/config.py'. "
        "Make sure that module is set up with a valid .env file."
    )

AUGMENTED_BUCKET   = "Augmented Images"
AUGMENTED_TABLE    = "augmented_images"
PREPROCESSED_TABLE = "preprocessed_images"


class AugDbManager:
    def __init__(self):
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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
        Download raw image bytes from Supabase Storage.
        Handles both plain filenames and full storage URLs.
        """
        try:
            clean_bucket = bucket_name.replace(" ", "%20")

            if "storage/v1/object/public/" in file_path:
                if f"/{bucket_name}/" in file_path:
                    file_path = file_path.split(f"/{bucket_name}/")[-1]
                elif f"/{clean_bucket}/" in file_path:
                    file_path = file_path.split(f"/{clean_bucket}/")[-1]

            actual_path = urllib.parse.unquote(file_path)
            return self.client.storage.from_(bucket_name).download(actual_path)

        except Exception as e:
            print(f"Error downloading image '{file_path}': {e}")
            return None

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

    def save_augmented_record(self, original_id: str, image_url: str, aug_type: str):
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
            }
            self.client.table(AUGMENTED_TABLE).insert(data).execute()
        except Exception as e:
            print(f"Error saving augmented record (id={original_id}, type={aug_type}): {e}")
