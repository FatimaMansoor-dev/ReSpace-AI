-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.annotated_images (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  original_id uuid UNIQUE,
  created_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  image_url text NOT NULL,
  room_type text,
  color_theme text,
  use_case text,
  lighting text,
  color_palette text,
  furniture jsonb,
  status text,
  assigned_to text,
  processed_at timestamp with time zone DEFAULT timezone('utc'::text, now()),
  CONSTRAINT annotated_images_pkey PRIMARY KEY (id)
);
CREATE TABLE public.augmented_images (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  original_id uuid NOT NULL,
  image_url text NOT NULL,
  aug_type text NOT NULL,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT augmented_images_pkey PRIMARY KEY (id),
  CONSTRAINT augmented_images_original_id_fkey FOREIGN KEY (original_id) REFERENCES public.preprocessed_images(id)
);
CREATE TABLE public.interior_images (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  created_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  image_url text NOT NULL,
  room_type text,
  color_theme text,
  use_case text,
  lighting text,
  color_palette text,
  furniture jsonb,
  status text,
  assigned_to text,
  CONSTRAINT interior_images_pkey PRIMARY KEY (id)
);
CREATE TABLE public.preprocessed_images (
  id uuid NOT NULL,
  image_url text,
  processed_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  CONSTRAINT preprocessed_images_pkey PRIMARY KEY (id)
);