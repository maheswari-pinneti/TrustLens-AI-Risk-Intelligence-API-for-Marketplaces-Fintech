"""
Image Similarity and Perceptual Hashing Detector Module
"""
import base64
import io
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from PIL import Image, UnidentifiedImageError
import imagehash


class ImageChecker:
    """
    Computes perceptual hashes (dHash, pHash) to detect exact and near-duplicate images
    frequently reused across fraudulent, counterfeit, or stolen catalog listings.
    """

    # Maximum file size (10 MB)
    MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024
    # Max dimensions to prevent decompression bombs
    MAX_IMAGE_PIXELS = 25_000_000

    @staticmethod
    def validate_image_magic_bytes(data: bytes) -> bool:
        """
        Validates file header signatures (magic bytes) to ensure payload is genuine image
        and not an executable, shell script, or polyglot binary disguised as an image.
        """
        if not data or len(data) < 6:
            return False
        # JPEG: FF D8 FF
        if data.startswith(b"\xff\xd8\xff"):
            return True
        # PNG: 89 50 4E 47 0D 0A 1A 0A
        if data.startswith(b"\x89PNG\r\n\x1a\n"):
            return True
        # GIF: GIF87a or GIF89a
        if data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
            return True
        # WebP: RIFF....WEBP
        if len(data) >= 12 and data.startswith(b"RIFF") and data[8:12] == b"WEBP":
            return True
        return False

    def __init__(self, known_hashes: Optional[Dict[str, str]] = None):
        """
        known_hashes: Optional map of {perceptual_hash_hex: listing_or_catalog_id}
        """
        self.known_hashes: Dict[str, str] = known_hashes or {}

    def register_hash(self, hash_str: str, source_id: str) -> None:
        """Adds a known image hash to the reference repository."""
        self.known_hashes[hash_str.strip().lower()] = source_id

    @staticmethod
    def load_image_from_base64(b64_string: str) -> Image.Image:
        """Decodes base64 string (including data URI format) into PIL Image."""
        if "," in b64_string:
            b64_string = b64_string.split(",", 1)[1]
        
        image_bytes = base64.b64decode(b64_string)
        if len(image_bytes) > ImageChecker.MAX_FILE_SIZE_BYTES:
            raise ValueError("Image file size exceeds maximum permitted limit (10MB)")

        if not ImageChecker.validate_image_magic_bytes(image_bytes):
            raise ValueError("Invalid image signature: payload does not match supported image formats (JPEG, PNG, WebP, GIF)")

        image = Image.open(io.BytesIO(image_bytes))
        image.verify()  # Verify integrity
        # Reopen because verify() closes the stream
        image = Image.open(io.BytesIO(image_bytes))
        return image.convert("RGB")

    @staticmethod
    def compute_hashes(img: Image.Image) -> Dict[str, str]:
        """
        Generates difference hash (dhash) and perceptual hash (phash).
        """
        d_hash = str(imagehash.dhash(img))
        p_hash = str(imagehash.phash(img))
        a_hash = str(imagehash.average_hash(img))
        return {
            "dhash": d_hash,
            "phash": p_hash,
            "ahash": a_hash,
            "primary_hash": d_hash
        }

    def compute_hamming_distance(self, hash1: str, hash2: str) -> int:
        """Calculates bitwise difference between two hexadecimal hash strings."""
        h1 = imagehash.hex_to_hash(hash1)
        h2 = imagehash.hex_to_hash(hash2)
        return int(h1 - h2)

    def find_matches(
        self,
        target_hash: str,
        threshold_distance: int = 8
    ) -> List[Dict[str, Any]]:
        """
        Finds matches among registered known hashes within threshold Hamming distance.
        Distance 0: Exact duplicate.
        Distance <= 4: High-confidence near-duplicate (compressed, cropped, or filtered).
        """
        matches = []
        target_h = imagehash.hex_to_hash(target_hash)

        for ref_hash_str, source_id in self.known_hashes.items():
            try:
                ref_h = imagehash.hex_to_hash(ref_hash_str)
                dist = int(target_h - ref_h)
                if dist <= threshold_distance:
                    # 64-bit hash: similarity = (64 - dist) / 64
                    similarity = max(0.0, (64 - dist) / 64.0)
                    matches.append({
                        "source_id": source_id,
                        "reference_hash": ref_hash_str,
                        "hamming_distance": dist,
                        "similarity_score": round(similarity, 4),
                        "match_type": "EXACT" if dist == 0 else "NEAR_DUPLICATE"
                    })
            except Exception:
                continue

        return sorted(matches, key=lambda m: m["hamming_distance"])

    def analyze(
        self,
        image_input: Optional[Union[str, Image.Image]] = None,
        precomputed_hash: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyzes image for duplicates and suspicious reuse.
        Returns normalized score (0.0 to 1.0), similarity info, and flags.
        """
        flags = []
        computed_hash = precomputed_hash

        if image_input is not None:
            try:
                if isinstance(image_input, str):
                    if image_input.startswith("data:image") or len(image_input) > 200:
                        img = self.load_image_from_base64(image_input)
                    else:
                        img = Image.open(image_input).convert("RGB")
                else:
                    img = image_input

                hashes = self.compute_hashes(img)
                computed_hash = hashes["primary_hash"]
            except Exception as e:
                flags.append(f"Image analysis warning: Unable to parse image payload ({str(e)})")
                return {
                    "normalized_score": 0.2,
                    "image_hash": None,
                    "is_duplicate": False,
                    "similarity_score": 0.0,
                    "matches": [],
                    "flags": flags
                }

        if not computed_hash:
            return {
                "normalized_score": 0.0,
                "image_hash": None,
                "is_duplicate": False,
                "similarity_score": 0.0,
                "matches": [],
                "flags": []
            }

        # Match against known repository
        matches = self.find_matches(computed_hash)

        if not matches:
            return {
                "normalized_score": 0.0,
                "image_hash": computed_hash,
                "is_duplicate": False,
                "similarity_score": 0.0,
                "matches": [],
                "flags": []
            }

        best_match = matches[0]
        dist = best_match["hamming_distance"]
        sim = best_match["similarity_score"]

        if dist == 0:
            normalized_score = 1.0
            flags.append(f"Duplicate image detected: 100% exact match with existing listing '{best_match['source_id']}'")
            is_dup = True
        elif dist <= 4:
            normalized_score = 0.85
            flags.append(f"Near-duplicate image detected ({sim * 100:.1f}% perceptual match) with listing '{best_match['source_id']}'")
            is_dup = True
        elif dist <= 7:
            normalized_score = 0.45
            flags.append(f"Moderate image visual similarity ({sim * 100:.1f}%) with listing '{best_match['source_id']}'")
            is_dup = False
        else:
            normalized_score = 0.15
            is_dup = False

        return {
            "normalized_score": round(normalized_score, 4),
            "image_hash": computed_hash,
            "is_duplicate": is_dup,
            "similarity_score": sim,
            "matches": matches[:5],
            "flags": flags
        }
