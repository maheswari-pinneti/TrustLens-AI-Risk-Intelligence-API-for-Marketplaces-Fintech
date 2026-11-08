"""
Unit tests for Image Similarity & Perceptual Hashing Detector
"""
import pytest
from PIL import Image
from app.detectors.image_checker import ImageChecker


def test_perceptual_hash_generation():
    img = Image.new("RGB", (100, 100), color=(255, 0, 0))
    hashes = ImageChecker.compute_hashes(img)
    assert "dhash" in hashes
    assert "phash" in hashes
    assert len(hashes["dhash"]) == 16  # 64-bit hex


def test_exact_duplicate_detection():
    checker = ImageChecker()
    img1 = Image.new("RGB", (100, 100), color=(0, 128, 255))
    h1 = ImageChecker.compute_hashes(img1)["primary_hash"]
    checker.register_hash(h1, source_id="lst_original_001")

    # Analyze identical image
    result = checker.analyze(image_input=img1)
    assert result["is_duplicate"] is True
    assert result["similarity_score"] == 1.0
    assert result["normalized_score"] == 1.0
    assert len(result["flags"]) >= 1
    assert "lst_original_001" in result["flags"][0]


def test_distinct_images_low_similarity():
    checker = ImageChecker()
    # Checker knows red image
    img_red = Image.new("RGB", (80, 80), color=(255, 0, 0))
    h_red = ImageChecker.compute_hashes(img_red)["primary_hash"]
    checker.register_hash(h_red, source_id="lst_red")

    # Pass noise or gradient image
    img_noise = Image.new("RGB", (80, 80))
    for x in range(80):
        for y in range(80):
            img_noise.putpixel((x, y), (x * 3, y * 3, (x + y)))

    result = checker.analyze(image_input=img_noise)
    assert result["is_duplicate"] is False
