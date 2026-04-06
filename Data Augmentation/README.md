# Data Augmentation Module

A modular, automated pipeline that applies geometry-preserving image augmentations to the preprocessed interior design dataset, doubling the effective size of the training corpus while maintaining full semantic alignment with text prompts.

## Augmentation Strategy

For a **conditional text-to-image generation** task, augmentations must not alter what the text prompt describes. Therefore only two transformations are applied:

| Augmentation | Real-World Simulation | Output per Image |
|---|---|---|
| **Scaling + Random Crop** | Different camera focal lengths & photographer framing | 1 variant |
| **Horizontal Flip** | Mirrored floor plans / reversed room layouts | 1 variant |

> **Not used**: Color Jitter, Blur, CutMix, Gaussian Noise — all break the semantic truth of the prompt.

## Folder Structure
```
Data Augmentation/
├── main.py                  # Orchestrator — fetches, augments, uploads
├── test_augmentor.py        # Offline unit tests (no Supabase needed)
├── README.md                # This file
└── src/
    └── utils/
        ├── augmentor.py     # Core augmentation functions (OpenCV)
        └── aug_db_manager.py# Supabase Storage + table I/O
```

## Database Setup (One-Time)

Run this SQL in the **Supabase SQL Editor** before executing `main.py`:

```sql
CREATE TABLE public.augmented_images (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_id UUID NOT NULL REFERENCES preprocessed_images(id),
    image_url   TEXT NOT NULL,
    aug_type    TEXT NOT NULL,  -- 'scaled_crop' or 'horizontal_flip'
    created_at  TIMESTAMPTZ DEFAULT now()
);
```

Also create a Storage bucket named **`Augmented Images`** in the Supabase Dashboard.

## Environment Variables

This module reuses the `.env` file from the adjacent `Data Annotation` project:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
```

## Running

```powershell
# From the ReSpace-AI root:
python "Data Augmentation/main.py"
```

The pipeline is **incremental** — images already present in `augmented_images` are automatically skipped on subsequent runs.

## Running Tests

```powershell
# No Supabase required:
cd d:\computer_vision_project
python -m pytest "ReSpace-AI/Data Augmentation/test_augmentor.py" -v
```

## Output Example

```
Starting augmentation for 10 image(s)...
--------------------------------------------------
  [OK] Saved augmented variant: img01_scaled_crop.jpg (type=scaled_crop)
  [OK] Saved augmented variant: img01_horizontal_flip.jpg (type=horizontal_flip)
...
--------------------------------------------------
Augmentation Complete!
  Original images processed : 10
  Augmented images generated: 20
  Failed downloads          : 0
  Failed uploads            : 0
--------------------------------------------------
```
