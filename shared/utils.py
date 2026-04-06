import os
from dotenv import load_dotenv
from supabase import create_client, Client
from urllib.parse import unquote

# Detect project root by looking for a sentinel file (like requirements.txt)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def init_supabase() -> Client:
    """Initialize Supabase client by looking for .env at the root or standard locations."""
    # Check current directory, then project root
    standard_env_paths = [
        os.path.join(PROJECT_ROOT, '.env'),
        os.path.join(os.getcwd(), '.env'),
        os.path.join(PROJECT_ROOT, 'Data Annotation', '.env')
    ]
    
    for path in standard_env_paths:
        if os.path.exists(path):
            load_dotenv(path)
            break
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("SUPABASE_URL or SUPABASE_KEY missing from environment.")
        
    return create_client(url, key)

def download_image(supabase: Client, path_or_url: str, bucket_name: str = "Raw Images"):
    """
    Standardized image downloader that handles both Supabase URLs and relative paths.
    """
    if not path_or_url:
        return None
        
    # Extract path from URL if a full URL is provided
    if "storage/v1/object/public/" in path_or_url:
        path = path_or_url.split(f"public/{bucket_name}/")[-1]
        path = unquote(path)
    else:
        path = path_or_url

    try:
        response = supabase.storage.from_(bucket_name).download(path)
        return response
    except Exception as e:
        print(f"Error downloading image from {path}: {e}")
        return None
