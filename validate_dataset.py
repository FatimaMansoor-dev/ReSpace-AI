import os
import json

# Configuration
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
EXPORT_DIR = os.path.join(ROOT_DIR, "examples", "dataset")
METADATA_FILE = os.path.join(EXPORT_DIR, "metadata.jsonl")

def validate_dataset():
    print(f"🔍 Starting validation for: {METADATA_FILE}")
    
    if not os.path.exists(METADATA_FILE):
        print(f"❌ Error: Metadata file not found at {METADATA_FILE}")
        return

    total_lines = 0
    missing_files = []
    invalid_json = []
    empty_captions = []
    valid_count = 0

    with open(METADATA_FILE, "r") as f:
        for i, line in enumerate(f, 1):
            total_lines += 1
            line = line.strip()
            if not line:
                continue
                
            try:
                data = json.loads(line)
                image_rel_path = data.get("image")
                caption = data.get("caption")

                if not image_rel_path:
                    missing_files.append(f"Line {i}: 'image' key missing")
                    continue

                # Construct absolute path to image
                # image_rel_path is usually "images/filename.jpg"
                image_abs_path = os.path.join(EXPORT_DIR, image_rel_path)

                # Check if file exists
                if not os.path.exists(image_abs_path):
                    missing_files.append(f"Line {i}: File not found -> {image_rel_path}")
                elif os.path.getsize(image_abs_path) == 0:
                    missing_files.append(f"Line {i}: File is 0 bytes -> {image_rel_path}")
                else:
                    if not caption or len(caption.strip()) < 5:
                        empty_captions.append(f"Line {i}: Caption missing or too short")
                    else:
                        valid_count += 1

            except json.JSONDecodeError:
                invalid_json.append(f"Line {i}: Invalid JSON format")

    print("\n" + "="*50)
    print("📊 VALIDATION REPORT")
    print("="*50)
    print(f"Total entries checked: {total_lines}")
    print(f"✅ Valid entries:       {valid_count}")
    print(f"❌ Missing/Broken files: {len(missing_files)}")
    print(f"⚠️  Invalid JSON lines:  {len(invalid_json)}")
    print(f"📝 Empty captions:      {len(empty_captions)}")
    print("="*50)

    if missing_files:
        print("\n❌ TOP MISSING FILES (first 10):")
        for err in missing_files[:10]:
            print(f"  - {err}")
    
    if valid_count == total_lines and total_lines > 0:
        print("\n✨ Perfect! All metadata paths point to valid image files.")
    elif total_lines > 0:
        print(f"\n💡 Recommendation: Run 'python export_dataset.py' to fix the {len(missing_files)} missing files.")

if __name__ == "__main__":
    validate_dataset()
