# Implements the actual file transformation logic for different file types.

import subprocess
import logging
import shutil
from pathlib import Path
from PIL import Image
from pypdf import PdfReader, PdfWriter
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


logger = logging.getLogger(__name__)
class EbookToPdfStrategy(BaseConversionStrategy):       # Inherits from BaseConversionStrategy
    def convert(self, input_path: Path, output_path: Path) -> Path:
        target_pdf = output_path.with_suffix('.pdf')        # Makes sure that final output file name ends with extension '.pdf'

        # CLI command for book layout
        cmd = [
            "ebook-convert",        #Calibres CLI binaray
            str(input_path),
            str(target_pdf),        # Input src and output srv destinations
            "--paper-size", "a4",
            "--pdf-page-margin-left", "36",
            "--pdf-page-margin-right", "36",
            "--pdf-page-margin-top", "36",
            "--pdf-page-margin-bottom", "36",
            "--pdf-default-font-size", "12",
            "--pdf-mono-font-size", "10",
            "--unsmarten-punctuation"
        ]
        try:
            # We set a generous time because book can take a long time to render
            process = subprocess.run(
                cmd, 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,         # Captures output and error log from Python Library
                text=True,
                check=True,
                timeout=300
            )
            logger.info(f"Ebook conversion output: {process.stdout}")
        except subprocess.TimeoutExpired:
            raise RuntimeError("Book conversion timed out. The file might be too large.")
        except FileNotFoundError:
            raise RuntimeError(
                "Calibre 'ebook-convert' was not found on the server."
                "Ensure Calibre is installed and added to the system PATH."
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Ebook conversion error: {e.stderr}")
            raise RuntimeError(f"Failed to process book file: {e.stderr}")
        return target_pdf