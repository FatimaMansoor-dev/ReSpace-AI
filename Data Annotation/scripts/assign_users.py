import os
from supabase import create_client, Client
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TABLE_NAME = os.getenv("TABLE_NAME", "interior_images")

USERS = ["muneeb", "fatima", "maham", "zobia"]
TARGET_COUNT = 1000

def assign_images():
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    for user in USERS:
        # Check current assignment count for this user
        res = supabase.table(TABLE_NAME).select("id", count="exact").eq("assigned_to", user).execute()
        current_count = res.count if hasattr(res, 'count') else len(res.data)
        
        need = TARGET_COUNT - current_count
        if need <= 0:
            print(f"User {user} already has {current_count} images.")
            continue
            
        print(f"User {user} has {current_count}, needs {need} more.")
        
        # Fetch unassigned pending images
        # Supabase python client limit might be 1000 by default, so we fetch in a loop if needed
        unassigned_res = supabase.table(TABLE_NAME).select("id").is_("assigned_to", "null").is_("status", "null").limit(need).execute()
        to_assign = [item['id'] for item in unassigned_res.data]
        
        if not to_assign:
            print(f"No more unassigned images available for {user}.")
            break
            
        print(f"Assigning {len(to_assign)} images to {user}...")
        
        # Update in chunks of 500
        for i in range(0, len(to_assign), 500):
            chunk = to_assign[i : i + 500]
            supabase.table(TABLE_NAME).update({"assigned_to": user}).in_("id", chunk).execute()
            print(f"  Batch {i//500 + 1} done.")

    print("Assignment check complete.")

if __name__ == "__main__":
    assign_images()
