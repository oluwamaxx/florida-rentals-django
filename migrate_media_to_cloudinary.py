import os
from pathlib import Path

import django
import cloudinary.uploader
from django.conf import settings


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


MEDIA_ROOT = Path(settings.MEDIA_ROOT)

# IMPORTANT:
# Start with 1 so we test one image first.
# After we confirm it works, we will change this to None
# and upload everything.
LIMIT = None

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".gif",
    ".bmp",
    ".tif",
    ".tiff",
}


def main():
    if not MEDIA_ROOT.exists():
        print(f"Media folder not found: {MEDIA_ROOT}")
        return

    files = [
        path
        for path in MEDIA_ROOT.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    ]

    files.sort()

    if not files:
        print("No image files were found in the media folder.")
        return

    if LIMIT is not None:
        files = files[:LIMIT]

    print(f"Found {len(files)} image(s) to upload.")
    print()

    uploaded = 0

    for file_path in files:
        relative_path = file_path.relative_to(MEDIA_ROOT).as_posix()

        # Cloudinary image public IDs should not contain the extension.
        public_id = f"media/{relative_path.rsplit('.', 1)[0]}"

        print(f"Uploading: {relative_path}")

        try:
            result = cloudinary.uploader.upload(
                str(file_path),
                public_id=public_id,
                resource_type="image",
                overwrite=True,
                invalidate=True,
                tags=["media"],
            )

            print("SUCCESS")
            print(f"Cloudinary ID: {result.get('public_id')}")
            print(f"URL: {result.get('secure_url')}")
            print()

            uploaded += 1

        except Exception as e:
            print("FAILED")
            print(f"Error: {e}")
            print()

    print("--------------------------------")
    print(f"Uploaded successfully: {uploaded}")
    print(f"Attempted: {len(files)}")
    print("--------------------------------")


if __name__ == "__main__":
    main()