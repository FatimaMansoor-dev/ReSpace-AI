"""
Offline unit tests for augmentor.py
------------------------------------
These tests use only NumPy and OpenCV — no Supabase connection required.

Run with:
    cd d:\\computer_vision_project
    python -m pytest "ReSpace-AI/Data Augmentation/test_augmentor.py" -v
"""
import sys
import os
import numpy as np
import pytest

# Make sure augmentor is importable without installing as a package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from utils.augmentor import random_scale_and_crop, horizontal_flip, augment_image


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_image():
    """A synthetic 1200x900 3-channel BGR image with a colour gradient."""
    img = np.zeros((900, 1200, 3), dtype=np.uint8)
    img[:, :, 0] = np.linspace(0, 255, 1200, dtype=np.uint8)   # Blue gradient (left→right)
    img[:, :, 1] = np.linspace(0, 255, 900,  dtype=np.uint8).reshape(-1, 1)  # Green (top→bottom)
    img[:, :, 2] = 128  # Constant red
    return img


# ---------------------------------------------------------------------------
# random_scale_and_crop
# ---------------------------------------------------------------------------

class TestRandomScaleAndCrop:

    def test_output_shape_is_target_size(self, sample_image):
        result = random_scale_and_crop(sample_image, target_size=(1024, 1024))
        assert result.shape == (1024, 1024, 3), (
            f"Expected (1024, 1024, 3) but got {result.shape}"
        )

    def test_dtype_preserved(self, sample_image):
        result = random_scale_and_crop(sample_image)
        assert result.dtype == np.uint8, f"Expected uint8 but got {result.dtype}"

    def test_custom_target_size(self, sample_image):
        result = random_scale_and_crop(sample_image, target_size=(512, 512))
        assert result.shape == (512, 512, 3)

    def test_small_scale_still_produces_correct_shape(self, sample_image):
        """Even at the smallest scale (0.7) the crop must match target_size."""
        result = random_scale_and_crop(
            sample_image, target_size=(1024, 1024), scale_range=(0.7, 0.7)
        )
        assert result.shape == (1024, 1024, 3)


# ---------------------------------------------------------------------------
# horizontal_flip
# ---------------------------------------------------------------------------

class TestHorizontalFlip:

    def test_output_shape_unchanged(self, sample_image):
        result = horizontal_flip(sample_image)
        assert result.shape == sample_image.shape

    def test_dtype_preserved(self, sample_image):
        result = horizontal_flip(sample_image)
        assert result.dtype == sample_image.dtype

    def test_flip_is_mirror(self, sample_image):
        """The first column of the flipped image == last column of the original."""
        result = horizontal_flip(sample_image)
        np.testing.assert_array_equal(
            result[:, 0, :],
            sample_image[:, -1, :],
            err_msg="First column of flipped image should equal last column of original."
        )

    def test_double_flip_is_identity(self, sample_image):
        """Flipping twice must return the original image."""
        double_flipped = horizontal_flip(horizontal_flip(sample_image))
        np.testing.assert_array_equal(double_flipped, sample_image)


# ---------------------------------------------------------------------------
# augment_image
# ---------------------------------------------------------------------------

class TestAugmentImage:

    def test_returns_exactly_two_variants(self, sample_image):
        result = augment_image(sample_image)
        assert len(result) == 2, f"Expected 2 augmented variants, got {len(result)}"

    def test_suffix_labels_are_correct(self, sample_image):
        result = augment_image(sample_image)
        suffixes = [suffix for _, suffix in result]
        assert "scaled_crop"     in suffixes
        assert "horizontal_flip" in suffixes

    def test_all_variants_are_numpy_arrays(self, sample_image):
        result = augment_image(sample_image)
        for arr, _ in result:
            assert isinstance(arr, np.ndarray)

    def test_all_variants_are_uint8(self, sample_image):
        result = augment_image(sample_image)
        for arr, suffix in result:
            assert arr.dtype == np.uint8, (
                f"Variant '{suffix}' has dtype {arr.dtype}, expected uint8"
            )
