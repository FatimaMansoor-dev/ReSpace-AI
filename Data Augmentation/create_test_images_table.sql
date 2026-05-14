-- SQL Script to create the test_images table
-- Run this in your Supabase SQL Editor

CREATE TABLE IF NOT EXISTS public.test_images (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_id UUID NOT NULL REFERENCES public.preprocessed_images(id),
    image_url   TEXT NOT NULL,
    prompt      TEXT,
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- Optional: Clear table if you want a fresh start
-- TRUNCATE TABLE public.test_images;
