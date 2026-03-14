import cv2
import numpy as np
import json
from src.utils.db_manager import SupabaseManager
PROMPTS_FILE  = "prompts.json"
def resize_and_normalize(image, target_size=(1024, 1024)):
    """
    Resize image to target_size and normalize pixel values.
    """
    # Resize
    resized = cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)
    
    # Normalize to [0, 1] range
    normalized = resized.astype(np.float32) / 255.0
    
    return normalized

def detect_blur_and_bright_spot(image, blur_threshold=250.0):
    """
    Detects if an image is blurry or has bright spots.
    Returns (is_blurry, has_bright_spot, laplacian_variance, binary_variance)
    """
    # # Convert image to grayscale for analysis
    # if len(image.shape) == 3:
    #     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # else:
    #     gray = image

    # Apply binary thresholding for bright spot detection
    _, binary_image = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY)

    # Apply Laplacian filter for edge detection
    laplacian = cv2.Laplacian(image, cv2.CV_64F)

    # Calculate variances
    binary_variance = binary_image.var()
    laplacian_variance = laplacian.var()

    # Determine conditions
    is_blurry = laplacian_variance < blur_threshold
    
    # Check bright spot condition based on variance of binary image (as per Sahil Utekar's blog)
    # Note: 5000 < binary_variance < 8500 range was mentioned
    has_bright_spot = 5000 < binary_variance < 8500

    return is_blurry, has_bright_spot, laplacian_variance, binary_variance

def sharpen_image(image):
    """
    Applies a sharpening filter to the image using a standard kernel.
    """
    # Standard sharpening kernel
    kernel = np.array([[-1, -1, -1],
                       [-1,  9, -1],
                       [-1, -1, -1]])
    # Apply filtering
    sharpened = cv2.filter2D(image, -1, kernel)
    return sharpened


def assign_prompts_to_images(records, templates: list) -> str:
    """
    Fetch images from Supabase and assign 1 template per 16 images.
    Images  0–15  → template[0]
    Images 16–31  → template[1]
    Images 32–47  → template[2]
    ...and so on.
    """
    BATCH_SIZE = 16

 
    
 

    db = SupabaseManager()
    

    for i, record in enumerate(records):
        if record.get("prompt"):
            print(f"[{i}] ⏭️ Skipping — prompt already exists")
            continue
        #i // BATCH_SIZE integer division, tells you which batch you're in
        #% len(templates)prevents going out of bounds if images > templates
        template_index = (i // BATCH_SIZE) % len(templates)
        template = templates[template_index]

    # Fill template with actual values from Supabase record
        prompt = template.format(
        room_type     = record.get("room_type",     "room"),
        color_theme   = record.get("color_theme",   "neutral"),
        color_palette = record.get("color_palette", "beige and white"),
        use_case      = record.get("use_case",      "relaxation"),
        lighting      = record.get("lighting",      "natural"),
        furniture     = record.get("furniture",     "modern furniture")
    )

    # UPDATE Supabase table with the prompt only if NULL
        try:
            db.client.table("processed_interior_images")\
            .update({"prompt": prompt})\
            .eq("id", record.get("id"))\
            .is_("prompt", "null")\
            .execute()
            print(f"[{i}] Updated id={record.get('id')}")

        
            
        except Exception as e:
            print(f"[{i}] Failed id={record.get('id')}: {e}")
            continue

    
    return "successfully assigned"
def train_test_split(records: list, test_size: float = 0.2, shuffle: bool = True, random_seed: int = 42):
    """
    Splits records into train and test sets.

    Args:
        records    : Full list of records (e.g. dicts from Supabase)
        test_size  : Fraction of data for test set (default 0.2 → 80/20 split)
        shuffle    : Whether to shuffle before splitting (default True)
        random_seed: Seed for reproducibility (default 42)

    Returns:
        train_records, test_records
    """
    if not records:
        raise ValueError("Records list is empty.")

    if not (0.0 < test_size < 1.0):
        raise ValueError("test_size must be between 0 and 1.")

    data = records.copy()

    if shuffle:
        rng = np.random.default_rng(random_seed)
        rng.shuffle(data)

    split_index = int(len(data) * (1 - test_size))

    train_records = data[:split_index]
    test_records  = data[split_index:]

    print(f"Total: {len(data)} | Train: {len(train_records)} | Test: {len(test_records)}")

    return train_records, test_records