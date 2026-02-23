import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from root directory
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TABLE_NAME = os.getenv("TABLE_NAME", "interior_images")

def verify_assignment():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Error: SUPABASE_URL or SUPABASE_KEY missing.")
        return

    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    print("Verifying image assignments...")
    try:
        # Get counts grouped by assigned_to
        # Note: raw SQL might be easier but we'll use filters for simplicity
        users = ["muneeb", "fatima", "maham", "zobia"]
        
        for user in users:
            res = supabase.table(TABLE_NAME).select("id", count="exact").eq("assigned_to", user).execute()
            count = res.count if hasattr(res, 'count') else len(res.data)
            print(f"User: {user} | Assigned Images: {count}")
            
        unassigned = supabase.table(TABLE_NAME).select("id", count="exact").is_("assigned_to", "null").execute()
        unassigned_count = unassigned.count if hasattr(unassigned, 'count') else len(unassigned.data)
        print(f"Unassigned: {unassigned_count}")

    except Exception as e:
        print(f"Error during verification: {e}")

if __name__ == "__main__":
    verify_assignment()
