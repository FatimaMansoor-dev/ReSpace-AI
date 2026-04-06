import cv2
import numpy as np
import random


def random_scale_and_crop(image, target_size=(1024, 1024), scale_range=(0.7, 1.0)):
    """
    Randomly scales the image and then crops it to target_size.

    Simulates different camera focal lengths and photographer framing choices.
    For example: a wide-angle shot of a full coworking space vs. a closer
    crop showing only the standing desks area.

    Args:
        image       : Input image as a NumPy array (uint8 BGR).
        target_size : Desired output (width, height). Default: (1024, 1024).
        scale_range : Range of scaling factors (min, max). Default: (0.7, 1.0).

    Returns:
        Cropped NumPy array of shape (target_size[1], target_size[0], 3), dtype uint8.
    """
    h, w = image.shape[:2]
    target_w, target_h = target_size

    # --- 1. Random scale factor ---
    scale = random.uniform(scale_range[0], scale_range[1])

    # New dimensions after scaling — must be at least as big as target crop
    new_w = max(int(w * scale), target_w)
    new_h = max(int(h * scale), target_h)

    # Downscale with INTER_AREA (best quality for shrinking)
    scaled = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # --- 2. Random crop to target_size ---
    max_x = new_w - target_w
    max_y = new_h - target_h

    start_x = random.randint(0, max_x) if max_x > 0 else 0
    start_y = random.randint(0, max_y) if max_y > 0 else 0

    cropped = scaled[start_y:start_y + target_h, start_x:start_x + target_w]
    return cropped


def horizontal_flip(image):
    """
    Flips the image horizontally (left <-> right).

    Simulates mirrored floor plans and room layouts — e.g., a room where
    natural light enters from the left vs. the right. The semantic content
    described by the text prompt is fully preserved.

    Args:
        image: Input image as a NumPy array (uint8 BGR).

    Returns:
        Horizontally flipped NumPy array, same shape and dtype as input.
    """
    return cv2.flip(image, 1)  # flipCode=1 → horizontal flip


def augment_image(image):
    """
    Applies both augmentations to a single image.

    Per original image this generates 2 augmented variants:
    1. A randomly scaled + cropped version  (suffix: 'scaled_crop')
    2. A horizontally flipped version       (suffix: 'horizontal_flip')

    Args:
        image: Input image as a NumPy array (uint8 BGR).

    Returns:
        List of (augmented_array, suffix_label) tuples.
    """
    augmented = []

    # Variant 1 — Scaling + Random Crop
    scaled_cropped = random_scale_and_crop(image)
    augmented.append((scaled_cropped, "scaled_crop"))

    # Variant 2 — Horizontal Flip
    flipped = horizontal_flip(image)
    augmented.append((flipped, "horizontal_flip"))

    return augmented
