import os
from supabase import create_client, Client
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TABLE_NAME = os.getenv("TABLE_NAME", "interior_images")

def check_counts():
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    total = supabase.table(TABLE_NAME).select("id", count="exact").execute().count
    pending = supabase.table(TABLE_NAME).select("id", count="exact").is_("status", "null").execute().count
    empty_status = supabase.table(TABLE_NAME).select("id", count="exact").eq("status", "").execute().count
    submitted = supabase.table(TABLE_NAME).select("id", count="exact").eq("status", "submitted").execute().count
    discarded = supabase.table(TABLE_NAME).select("id", count="exact").eq("status", "discarded").execute().count
    
    unassigned = supabase.table(TABLE_NAME).select("id", count="exact").is_("assigned_to", "null").execute().count
    unassigned_pending = supabase.table(TABLE_NAME).select("id", count="exact").is_("assigned_to", "null").is_("status", "null").execute().count
    
    with open("debug_results.txt", "w") as f:
        f.write("-" * 30 + "\n")
        f.write(f"Total Images: {total}\n")
        f.write(f"Pending (status IS NULL): {pending}\n")
        f.write(f"Empty Status (status = ''): {empty_status}\n")
        f.write(f"Submitted: {submitted}\n")
        f.write(f"Discarded: {discarded}\n")
        f.write(f"Unassigned Total: {unassigned}\n")
        f.write(f"Unassigned AND Pending (IS NULL): {unassigned_pending}\n")
        f.write("-" * 30 + "\n")
        
        users = ["muneeb", "fatima", "maham", "zobia"]
        for user in users:
            u_total = supabase.table(TABLE_NAME).select("id", count="exact").eq("assigned_to", user).execute().count
            u_pending = supabase.table(TABLE_NAME).select("id", count="exact").eq("assigned_to", user).is_("status", "null").execute().count
            f.write(f"User {user:10}: Assigned={u_total:5}, Pending={u_pending:5}\n")
        f.write("-" * 30 + "\n")
    
    print("Results written to debug_results.txt")

if __name__ == "__main__":
    check_counts()
