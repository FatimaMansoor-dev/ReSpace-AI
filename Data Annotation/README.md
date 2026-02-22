# Interior Design Dataset Generator

A modular, professional GUI application for annotating interior design images and generating structured datasets for AI model fine-tuning.

## Features
- **Structured Data Storage**: Captures Room Type, Color Theme, Use Case, Lighting, Color Palette, and Furniture.
- **Multi-User Collaboration**: Uses Supabase status tracking (`submitted`, `discarded`) to prevent duplicate work.
- **Incremental Sync**: Utility script to sync images from Supabase Storage buckets to the database.
- **Modern UI**: Built with `customtkinter` for a premium dark-themed experience.

## Project Structure
- `main.py`: Application entry point.
- `src/`: Core logic and UI components.
  - `config.py`: Centralized constants and environment loading.
  - `database.py`: Supabase CRUD operations.
  - `ui/`: Modular UI panels (`MainWindow`, `ImagePanel`, `FormPanel`).
- `scripts/`: Utility scripts for maintenance and synchronization.
- `setup.sql`: Database schema definition.
- `prompts.json`: A library of 40 diverse prompt templates for training.

## Setup Instructions

### 1. Prerequisites
- Python 3.10+
- Supabase Account

### 2. Environment Variables
Create a `.env` file in the root directory:
```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
TABLE_NAME=interior_images
```

### 3. Database Setup
Run the contents of `setup.sql` in your Supabase SQL Editor to create the necessary tables.

### 4. Installation
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 5. Synchronize Images
Place your images in a Supabase Storage bucket named `Raw Images`, then run:
```powershell
python scripts/sync_bucket_to_db.py
```

## Usage
Launch the application to start annotating:
```powershell
python main.py
```
- Select attributes from the dropdowns.
- Multi-select furniture items.
- Click **Submit Annotation** to save the structured data to Supabase.
- Use **Pass / Discard** to skip irrelevant images.

## License
MIT
