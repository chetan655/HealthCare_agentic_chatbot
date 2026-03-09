import os
from pathlib import Path
import uuid
from typing import Optional

class FileService:
    def __init__(self, upload_path: Path):
        self.upload_path = upload_path
        self.upload_path.mkdir(parents=True, exist_ok=True)

    async def save_image(self, image) -> Optional[Path]:
        if not image or not image.filename:
            # print()
            # print("no image", image)
            return None
        
        try:
            file_ext = os.path.splitext(image.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            image_path = self.upload_path / unique_filename

            content = await image.read()
            with open(image_path, "wb") as f:
                f.write(content)

            return image_path
        
        except Exception as e:
            raise Exception("Error saving file: ", e)
        
    def cleanup_file(self, path: Optional[Path]):
        if path and path.exists():
            try:
                path.unlink()
                print(f"File deleted: {path}")
            except Exception as e:
                print(f"Failed to delete file: {e}")