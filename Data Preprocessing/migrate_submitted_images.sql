-- SQL Migration Script to Append 'submitted' Images to 'annotated_images' table
-- Run this in the Supabase SQL Editor

-- 1. Create the table 'annotated_images' if it doesn't already exist
CREATE TABLE IF NOT EXISTS annotated_images (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    original_id uuid UNIQUE, -- References the ID in interior_images to prevent duplicates
    created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
    image_url text NOT NULL,
    room_type text,
    color_theme text,
    use_case text,
    lighting text,
    color_palette text,
    furniture jsonb, 
    status text,
    assigned_to text,
    processed_at timestamp with time zone DEFAULT timezone('utc'::text, now())
);

-- 2. Append (INSERT) only new 'submitted' rows from 'interior_images'
-- The ON CONFLICT DO NOTHING ensures that we don't duplicate rows already in annotated_images
INSERT INTO annotated_images (
    original_id,
    image_url,
    room_type,
    color_theme,
    use_case,
    lighting,
    color_palette,
    furniture,
    status,
    assigned_to
)
SELECT 
    id AS original_id,
    image_url,
    room_type,
    color_theme,
    use_case,
    lighting,
    color_palette,
    furniture,
    status,
    assigned_to
FROM interior_images
WHERE status = 'submitted'
ON CONFLICT (original_id) DO NOTHING;

-- 3. (Optional) Feedback
-- SELECT count(*) FROM annotated_images;
