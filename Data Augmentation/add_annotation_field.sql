-- SQL Script to add separate annotation columns to existing tables
-- Run this in Supabase SQL Editor

-- 1. Add columns to test_images
ALTER TABLE public.test_images 
ADD COLUMN IF NOT EXISTS room_type TEXT,
ADD COLUMN IF NOT EXISTS color_theme TEXT,
ADD COLUMN IF NOT EXISTS use_case TEXT,
ADD COLUMN IF NOT EXISTS lighting TEXT,
ADD COLUMN IF NOT EXISTS color_palette TEXT,
ADD COLUMN IF NOT EXISTS furniture JSONB;

-- 2. Add columns to augmented_images
ALTER TABLE public.augmented_images 
ADD COLUMN IF NOT EXISTS room_type TEXT,
ADD COLUMN IF NOT EXISTS color_theme TEXT,
ADD COLUMN IF NOT EXISTS use_case TEXT,
ADD COLUMN IF NOT EXISTS lighting TEXT,
ADD COLUMN IF NOT EXISTS color_palette TEXT,
ADD COLUMN IF NOT EXISTS furniture JSONB;
