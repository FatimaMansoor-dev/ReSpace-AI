-- Run this in the Supabase SQL Editor
CREATE TABLE IF NOT EXISTS interior_images (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
    image_url text NOT NULL,
    room_type text,
    color_theme text,
    use_case text,
    lighting text,
    color_palette text,
    furniture jsonb, -- Stores array of furniture items
    status text DEFAULT NULL -- Values: null, 'submitted', 'discarded'
);

-- Migration for existing table:
-- ALTER TABLE interior_images ADD COLUMN IF NOT EXISTS room_type text;
-- ALTER TABLE interior_images ADD COLUMN IF NOT EXISTS color_theme text;
-- ALTER TABLE interior_images ADD COLUMN IF NOT EXISTS use_case text;
-- ALTER TABLE interior_images ADD COLUMN IF NOT EXISTS lighting text;
-- ALTER TABLE interior_images ADD COLUMN IF NOT EXISTS color_palette text;
-- ALTER TABLE interior_images ADD COLUMN IF NOT EXISTS furniture jsonb;

-- Optional: Enable RLS or set permissions as needed
-- ALTER TABLE interior_images ENABLE ROW LEVEL SECURITY;
