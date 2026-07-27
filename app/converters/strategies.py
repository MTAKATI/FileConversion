# Implements the actual file transformation logic for different file types.

import shutil
from pathlib import Path
from PIL import Image
from pypdf import PDFReader, PdfWriter 
from app.converters.base import BaseConversionStrategy 

class PdfFixStrategy(BaseConversionStrategy):
    """Handles misnamed or broken ._pdf files by verifying/re-saving as clean .pdf"""
    def convert(self, input_path: Path, output_path:Path) -> Path:
        target_pdf = output_path.with_suffix(".pdf")
        try:
            reader = PdfReader(str(input_path))
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            with open(target_pdf, "wb") as f:
                writer.write(f)
        except Exception:
            # Fallback if reader fails but file is a readable PDF binary
            shutil.copy(input_path, target_pdf)
        return target_pdf


# Transforms standard image files (png, jpg, jpeg, webp) into a single page PDF docs
class ImageToPdfStrategy(BaseConversionStrategy):
    """Converts images (png, jpg, jpeg) to .pdf"""
    def convert(self, input_path: Path, output_path: Path) -> Path:
        target_pdf = output_path.with_suffix('.pdf')
        image = Image.open(input_path)
        if image.mode != "RGB":
            image = image.convert("RGB")
        image.save(target_pdf, "PDF")
        return target_pdf

class DefaultStrategy(BaseConversionStrategy):
    """Fallback strategy: Copies file to output path with .pdf extensions"""
    def convert(self, input_path: Path, output_path: Path) -> Path:
        target_pdf = output_path.with_suffix(".pdf")
        shutil.copy(input_path, target_pdf)
        return target_pdf