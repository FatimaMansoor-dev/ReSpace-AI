from db_manager import SupabaseManager
import json
import os
def assign_prompts_to_images(records, templates: list) -> str:
    """
    Fetch images from Supabase and assign 1 template per 16 images.
    Images  0–15  → template[0]
    Images 16–31  → template[1]
    Images 32–47  → template[2]
    ...and so on.
    """
    BATCH_SIZE = 16
    print(type(templates))
    print(templates)
 

    for i, record in enumerate(records):
        
        
        # i // BATCH_SIZE integer division, tells you which batch you're in
        # % len(templates) prevents going out of bounds if images > templates
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
            db.client.table("preprocessed_images")\
            .update({"prompt": prompt})\
            .eq("id", record.get("id"))\
            .is_("prompt", "null")\
            .execute()
            print(f"[{i}] Updated id={record.get('id')}")
        except Exception as e:
            print(f"[{i}] Failed id={record.get('id')}: {e}")
            continue

    return "successfully assigned"

db = SupabaseManager()
records = db.fetch_submitted_images() 


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
file_path = os.path.join(BASE_DIR, "prompts.json")

with open(file_path, "r") as f:
     TEMPLATES = json.load(f)
     templates = TEMPLATES["templates"]

assign_prompts_to_images(records, templates)
