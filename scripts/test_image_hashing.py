"""
Image Similarity & Perceptual Hashing Demonstration Script
Generates test product image assets and verifies exact & near-duplicate detection.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.detectors.image_checker import ImageChecker

IMAGES_DIR = ROOT_DIR / "data" / "sample_images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def create_test_images():
    """Generates synthetic product images for similarity testing."""
    # 1. Original Sneaker Product Photo
    img_orig = Image.new("RGB", (400, 400), color=(240, 244, 248))
    draw = ImageDraw.Draw(img_orig)
    # Draw stylized sneaker shape
    draw.polygon([(80, 280), (140, 180), (280, 180), (340, 240), (320, 280), (80, 280)], fill=(30, 41, 59))
    draw.ellipse([(140, 220), (260, 260)], fill=(14, 165, 233))
    draw.rectangle([(60, 280), (340, 305)], fill=(255, 255, 255), outline=(100, 116, 139), width=2)
    orig_path = IMAGES_DIR / "sneaker_original.jpg"
    img_orig.save(orig_path, "JPEG", quality=95)

    # 2. Near-Duplicate (Re-compressed, cropped, and slightly blurred copy)
    img_near = img_orig.crop((10, 10, 390, 390)).resize((400, 400))
    img_near = img_near.filter(ImageFilter.GaussianBlur(radius=0.8))
    near_path = IMAGES_DIR / "sneaker_reuploaded_copy.jpg"
    img_near.save(near_path, "JPEG", quality=65)

    # 3. Unrelated Different Product Photo (e.g. Gold Watch)
    img_diff = Image.new("RGB", (400, 400), color=(15, 23, 42))
    draw_diff = ImageDraw.Draw(img_diff)
    draw_diff.ellipse([(100, 100), (300, 300)], fill=(234, 179, 8), outline=(254, 240, 138), width=8)
    draw_diff.ellipse([(130, 130), (270, 270)], fill=(30, 41, 59))
    draw_diff.line([(200, 200), (200, 150)], fill=(255, 255, 255), width=4)
    draw_diff.line([(200, 200), (240, 200)], fill=(255, 255, 255), width=3)
    diff_path = IMAGES_DIR / "watch_different.jpg"
    img_diff.save(diff_path, "JPEG", quality=95)

    print(f"Created sample images in: {IMAGES_DIR}")
    return orig_path, near_path, diff_path


def test_hashing_workflow():
    orig_path, near_path, diff_path = create_test_images()

    checker = ImageChecker()

    # Compute hashes
    h_orig = checker.compute_hashes(Image.open(orig_path))
    h_near = checker.compute_hashes(Image.open(near_path))
    h_diff = checker.compute_hashes(Image.open(diff_path))

    print("\n" + "=" * 65)
    print(" 📷 PERCEPTUAL HASH EXTRACTION")
    print("=" * 65)
    print(f"Original Sneaker dHash:      {h_orig['primary_hash']}")
    print(f"Re-uploaded Copy dHash:      {h_near['primary_hash']}")
    print(f"Unrelated Watch dHash:       {h_diff['primary_hash']}")
    print("-" * 65)

    dist_near = checker.compute_hamming_distance(h_orig["primary_hash"], h_near["primary_hash"])
    sim_near = (64 - dist_near) / 64 * 100

    dist_diff = checker.compute_hamming_distance(h_orig["primary_hash"], h_diff["primary_hash"])
    sim_diff = (64 - dist_diff) / 64 * 100

    print(f"Hamming Distance (Orig vs Copy):      {dist_near:2d} bits / 64  -->  {sim_near:.1f}% Similarity")
    print(f"Hamming Distance (Orig vs Different): {dist_diff:2d} bits / 64  -->  {sim_diff:.1f}% Similarity")

    # Register original hash in checker
    checker.register_hash(h_orig["primary_hash"], source_id="lst_sneaker_authentic_001")

    # Analyze re-uploaded copy
    analysis = checker.analyze(image_input=str(near_path))

    print("\n" + "=" * 65)
    print(" 🔍 DUPLICATE DETECTION RESULT")
    print("=" * 65)
    print(f"Is Duplicate:     {analysis['is_duplicate']}")
    print(f"Similarity Score: {analysis['similarity_score'] * 100:.1f}%")
    print(f"Risk Score Contrib: {analysis['normalized_score'] * 20.0:.1f} / 20.0 pts")
    print("Triggered Flags:")
    for flag in analysis["flags"]:
        print(f"  • {flag}")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    test_hashing_workflow()
