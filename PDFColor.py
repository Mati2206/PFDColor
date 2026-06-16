import os

import fitz  # PyMuPDF
from PIL import Image, ImageOps
import numpy as np
import io

def rgb_to_pdf_color(rgb: tuple[float, float, float]) -> tuple[bytes, bytes]:
    r, g, b = rgb
    return (f"{r} {g} {b} rg\n".encode(), f"{r} {g} {b} RG\n".encode())

def color_text(doc: fitz.Document, color_rgb: tuple[float, float, float]):
    rgb_fill, rgb_stroke = rgb_to_pdf_color(color_rgb)
    for page in doc:
        for xref in page.get_contents():
            raw_code = doc.xref_stream(xref)
            new_code = rgb_fill + rgb_stroke + raw_code
            doc.update_stream(xref, new_code)

def color_drawings(doc: fitz.Document, color_rgb: tuple[float, float, float]):
    rgb_fill, rgb_stroke = rgb_to_pdf_color(color_rgb)
    for page in doc:
        resources_list = page.get_xobjects()
        for resource in resources_list:
            xref = resource[0]
            raw_code = doc.xref_stream(xref)
            new_code = raw_code
            new_code = new_code.replace(b"\n0 g\n", b"\n" + rgb_fill + b"\n")
            new_code = rgb_fill + rgb_stroke + new_code
            doc.update_stream(xref, new_code)

def color_images(doc: fitz.Document, color_rgb: tuple[float, float, float]):
    
    pillow_color = tuple(int(c * 255) for c in color_rgb)

    for page in doc:
        image_list = page.get_images(full=True)
        
        for img_index, img_info in enumerate(image_list):
            xref = img_info[0]
            
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
        
            img = Image.open(io.BytesIO(image_bytes))
            if img.mode != "L":
                img = img.convert("L")

            final_img = ImageOps.colorize(img, black=pillow_color, white="white")
            
            output_buffer = io.BytesIO()
            final_img.save(output_buffer, format="PNG")
            new_image_bytes = output_buffer.getvalue()
        
            page.replace_image(xref, stream=new_image_bytes)

def PDFColor(input_pdf: str, output_pdf: str, color_rgb: tuple[float, float, float]):
    doc = fitz.open(input_pdf)

    color_text(doc, color_rgb)
    color_drawings(doc, color_rgb)
    color_images(doc, color_rgb)

    doc.save(output_pdf)
    doc.close()

# Run the script
PDFColor("2a.pdf", "done.pdf", color_rgb=(1, 0, 1))