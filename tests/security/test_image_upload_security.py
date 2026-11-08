"""
Security Tests: Image File Upload Protection & Magic Byte Verification
"""
import base64
import pytest
from app.detectors.image_checker import ImageChecker


def test_magic_bytes_detection():
    # Valid PNG header: 89 50 4E 47 0D 0A 1A 0A
    png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
    assert ImageChecker.validate_image_magic_bytes(png_bytes) is True

    # Valid JPEG header: FF D8 FF
    jpg_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01"
    assert ImageChecker.validate_image_magic_bytes(jpg_bytes) is True

    # Valid WebP header: RIFF....WEBP
    webp_bytes = b"RIFF\x12\x00\x00\x00WEBPVP8 "
    assert ImageChecker.validate_image_magic_bytes(webp_bytes) is True

    # Valid GIF header: GIF89a
    gif_bytes = b"GIF89a\x01\x00\x01\x00"
    assert ImageChecker.validate_image_magic_bytes(gif_bytes) is True

    # Malicious bash/script file disguised as image
    fake_img = b"#!/bin/bash\nrm -rf / # fake malware payload"
    assert ImageChecker.validate_image_magic_bytes(fake_img) is False

    # Arbitrary binary/executable MZ header
    exe_bytes = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00"
    assert ImageChecker.validate_image_magic_bytes(exe_bytes) is False


def test_load_base64_rejects_fake_image_payload():
    # Base64 payload containing a shell script
    fake_payload = base64.b64encode(b"#!/bin/sh\necho exploit\n").decode("ascii")
    with pytest.raises(ValueError) as exc:
        ImageChecker.load_image_from_base64(fake_payload)
    assert "Invalid image signature" in str(exc.value)
