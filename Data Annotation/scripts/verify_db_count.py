import os
from supabase import create_client, Client
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TABLE_NAME = os.getenv("TABLE_NAME", "interior_images")

def verify_count():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Missing Supabase credentials.")
        return

    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Get total count
    res = supabase.table(TABLE_NAME).select("*", count="exact").execute()
    print(f"Total rows in {TABLE_NAME}: {res.count}")

if __name__ == "__main__":
    verify_count()
