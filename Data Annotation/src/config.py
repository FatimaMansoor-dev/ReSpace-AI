import os
from dotenv import load_dotenv

# Load environment variables from project root
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TABLE_NAME = os.getenv("TABLE_NAME", "interior_images")

# UI Constants
ROOM_TYPES = ["Bedroom", "Kitchen", "Lounge", "Dining Room"]
COLOR_THEMES = [
    "Modern White", "Sleek Charcoal", "Earthy Terracotta", 
    "Royal Blue", "Soft Beige", "Emerald Green", "Pastel Pink"
]

COLOR_PALETTES = ["Neutral", "Warm", "Pastel", "Dark Mode", "Brand-specific"]

LIGHTING_CONDITIONS = ["Natural Daylight", "Warm Indoor Lighting", "LED Office Lighting"]

FURNITURE_TYPES = ["Desks", "Sofas", "Shelves", "Table", "Chair", "Bed", "Lighting Fixtures", "Plants", "Partitions"]

USE_CASES = {
    "Bedroom": ["Kids", "Couple", "Adults", "Guest", "Master Suite", "Minimalist Retreat"],
    "Kitchen": ["Professional Chef", "Small Family", "Open Concept", "Modern Minimalist", "Industrial Loft"],
    "Lounge": ["Home Theater", "Formal Entertaining", "Cozy Family", "Reading Nook", "Social Hub"],
    "Dining Room": ["Formal", "Casual Family", "Bistro Style", "Elegant Party", "Rustic"]
}

# Image Settings
IMAGE_DISPLAY_SIZE = (800, 600)
APP_GEOMETRY = "1200x800"
APP_TITLE = "Interior Design Dataset Generator"
