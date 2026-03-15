-- SQL for Supabase to create the preprocessed_images table
-- Simplified to only store the ID and the image data or URL

CREATE TABLE IF NOT EXISTS preprocessed_images (
    id UUID PRIMARY KEY, -- Same ID as original for easy mapping
    image_url TEXT, -- URL to the processed image in storage
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Index for searching by image_url
CREATE INDEX IF NOT EXISTS idx_preprocessed_image_url ON preprocessed_images(image_url);
