# Data Preprocessing Module

This modular project assumes there's a table in your Supabase DB containing images with a `submitted` status. It then fetches, processes, and evaluates them for quality based on Sahil Utekar's methods.

## Preprocessing Steps
1.  **Resize + Normalize**: Resizes images to $1024 \times 1024$ and normalizes pixel values to $[0, 1]$.
2.  **Blur & Bright Spot Detection**: Uses the variance of the Laplacian filter to detect blur and binary thresholding for bright spots.

### Core Logic:
-   `is_blurry = laplacian_variance < threshold`
-   `has_bright_spot = 5000 < binary_variance < 8500` (from reference blog)

## Folder Structure
```
Data Preprocessing/
    ├── main.py                # Main script controlling workflow
    └── src/                   # Source code
        └── utils/
            ├── db_manager.py  # Supabase database & storage logic
            └── image_processor.py # OpenCV preprocessing & detection logic
```

## Setup & Running
1.  Ensure you have `opencv-python`, `numpy`, and `supabase` packages installed.
2.  The script expects a `submitted` status in the `status` column of your Supabase table.
3.  The configuration (URL, Keys) is imported from the adjacent `Data Annotation` project's `src/config.py`.

Run the main file to see results:
```powershell
python -m "Data Preprocessing.main"
```
Or simply:
```powershell
python "Data Preprocessing/main.py"
```

## Output Example
```text
Processing 10 'submitted' images...
--------------------------------------------------
Preprocessing completed.
Number of blur images detected : 2
Number of good images : 8
--------------------------------------------------
```
