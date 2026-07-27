from pathlib import Path
from app.converters.base import BaseConversionStrategy
from app.converters.strategies import PdfFixStrategy, ImageToPdfStrategy, DefaultStrategy

# Chooses which strategy to use based on the input file's name or extension
class ConverterFactory:
    @staticmethod
    def get_strategy(file_path: Path) -> BaseConversionStrategy:
        filename = file_path.name.lower()
        ext = file_path.suffix.lower()

        # Check for bad PDF extensions like ._pdf or files ending with _pdf
        if ext in ["._pdf", "._pdf_"] or filename.endswith("_pdf"):
            return PdfFixStrategy()

        # Check image extensions
        if ext in [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]:
            return ImageToPdfStrategy()

        # Fallback default strategy
        return DefaultStrategy()