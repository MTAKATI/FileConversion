import os
import shutil
from pathlib import Path
from PIL import Image
from pypdf import PdfReader, PdfWriter

def convert_to_pdf(input_file_path, output_dir=None):
    """
    Converts various file extensions to PDF. 
    Handles images, text, and misnamed PDF files (like ._pdf or _pdf).
    """
    input_path = Path(input_file_path)
    
    if not input_path.exists():
        print(f"Error: File balance not found at {input_file_path}")
        return None

    # Determine output directory and path
    out_dir = Path(output_dir) if output_dir else input_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = out_dir / f"{input_path.stem}.pdf"

    # Normalize the extension to lowercase for checking
    ext = input_path.suffix.lower()

    print(f"Processing: {input_path.name} (Extension: {ext if ext else 'None'})")

    try:
        # 1. Handle PDF variations (._pdf, _pdf, .pdf)
        # If the file extension ends with 'pdf' or the user forgot the dot
        if ext.endswith('pdf') or input_path.name.endswith('_pdf'):
            print("-> Detected PDF/misnamed PDF file. Standardizing extension...")
            
            # Verify if it's a valid PDF using pypdf
            try:
                reader = PdfReader(input_path)
                writer = PdfWriter()
                for page in reader.pages:
                    writer.add_page(page)
                with open(output_path, "wb") as f:
                    writer.write(f)
                print(f"✓ Successfully fixed and saved to: {output_path}")
            except Exception:
                # If pypdf fails, fall back to a direct file copy rename
                shutil.copy(input_path, output_path)
                print(f"✓ Copied and renamed to: {output_path}")
            return output_path

        # 2. Handle Images (.jpg, .png, .jpeg, .bmp, etc.)
        elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']:
            print("-> Converting image to PDF...")
            image = Image.open(input_path)
            # PDF requires RGB mode
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            image.save(output_path, "PDF")
            print(f"✓ Successfully converted image to: {output_path}")
            return output_path

        # 3. Handle Plain Text (.txt, .log, .py, etc.)
        elif ext in ['.txt', '.log', '.py', '.json', '.csv']:
            print("-> Converting text file to PDF...")
            # We use Pillow to draw text onto a PDF canvas simply
            from PIL import ImageDraw, ImageFont
            
            with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            # Create a blank white A4-sized image (approx 2480x3508 pixels at 300 dpi)
            img = Image.new('RGB', (2480, 3508), color=(255, 255, 255))
            canvas = ImageDraw.Draw(img)
            
            # Write text line by line
            y_offset = 100
            for line in lines[:80]: # Limiting to first page for simplicity
                canvas.text((100, y_offset), line.strip(), fill=(0, 0, 0))
                y_offset += 40
                
            img.save(output_path, "PDF")
            print(f"✓ Successfully converted text to: {output_path}")
            return output_path

        else:
            print(f"⚠ Extension '{ext}' is not explicitly supported by this basic script.")
            print("If this is a Microsoft Office file (docx/xlsx), you will need specific libraries like 'docx2pdf'.")
            return None

    except Exception as e:
        print(f"❌ Failed to convert {input_path.name}. Error: {e}")
        return None

# --- Example Usage ---
if __name__ == "__main__":
    # Test with a misnamed PDF file
    convert_to_pdf("27 Jun 2026._pdf") 
    
    # # Test with a standard image
    # convert_to_pdf("photo.jpg")