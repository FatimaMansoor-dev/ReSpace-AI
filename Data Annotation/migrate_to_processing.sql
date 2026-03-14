-- SQL for Supabase to migrate 'submitted' rows to a separate processing table
-- This script ensures idempotent execution (only new rows are migrated)

-- 1. Create the new table if it doesn't exist
-- It mirrors the structure of interior_images but adds a processed_at column
CREATE TABLE IF NOT EXISTS processed_interior_images (
    id UUID PRIMARY KEY REFERENCES interior_images(id),
    image_url TEXT,
    room_type TEXT,
    color_theme TEXT,
    use_case TEXT,
    lighting TEXT,
    color_palette TEXT,
    furniture JSONB,
    assigned_to TEXT,
    migrated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Create an index for optimized lookups
CREATE INDEX IF NOT EXISTS idx_processed_migrated_at ON processed_interior_images(migrated_at);

-- 3. SQL logic to insert 'submitted' rows that aren't already in the new table
INSERT INTO processed_interior_images (
    id, image_url, room_type, color_theme, use_case, lighting, color_palette, furniture, assigned_to
)
SELECT 
    id, image_url, room_type, color_theme, use_case, lighting, color_palette, furniture, assigned_to
FROM 
    interior_images
WHERE 
    status = 'submitted'
    AND id NOT IN (SELECT id FROM processed_interior_images)
ON CONFLICT (id) DO NOTHING;


ALTER TABLE processed_interior_images 
ADD COLUMN IF NOT EXISTS prompt TEXT;
```

**4.** You'll see a success message like:
```
Success. No rows returned.

-- 4. (Optional) Provide a view or confirmation of migrated rows
-- SELECT count(*) FROM processed_interior_images;
