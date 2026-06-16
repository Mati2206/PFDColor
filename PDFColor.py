import os, sys, subprocess

import fitz  # PyMuPDF
from PIL import Image, ImageOps
import io

def rgb_to_pdf_color(rgb: tuple[float, float, float]) -> tuple[bytes, bytes]:
    r, g, b = rgb
    return (f"{r} {g} {b} rg\n".encode(), f"{r} {g} {b} RG\n".encode())

def color_text(doc: fitz.Document, color_rgb: tuple[float, float, float]):
    rgb_fill, rgb_stroke = rgb_to_pdf_color(color_rgb)
    fill_cmd = rgb_fill.strip()
    stroke_cmd = rgb_stroke.strip()
    for page in doc:
        for xref in page.get_contents():
            raw_code = doc.xref_stream(xref)

            new_code = raw_code
            new_code = new_code.replace(b" 0 g", b" " + fill_cmd)
            new_code = new_code.replace(b"\n0 g", b"\n" + fill_cmd)
            new_code = new_code.replace(b" 0 G", b" " + stroke_cmd)
            new_code = new_code.replace(b"\n0 G", b"\n" + stroke_cmd)
            
            new_code = new_code.replace(b"0 0 0 rg", fill_cmd)
            new_code = new_code.replace(b"0 0 0 RG", stroke_cmd)

            new_code = rgb_fill + rgb_stroke + new_code
            doc.update_stream(xref, new_code)

# For specyfic pdf
def color_shapes(doc: fitz.Document, color_rgb: tuple[float, float, float]):
    for page in doc:
        paths = page.get_drawings()

        shape = fitz.Shape(page)

        for path in paths:
            stroke_opacity = path.get("stroke_opacity", 1.0)
            fill_opacity = path.get("fill_opacity", 1.0)
            if stroke_opacity is None: stroke_opacity = 1.0
            if fill_opacity is None: fill_opacity = 1.0

            color = color_rgb

            
            if path.get("fill") == (1.0, 1.0, 1.0) or path.get("color") == (1.0, 1.0, 1.0):
                color = (1, 1, 1)

            for item in path.get("items", []):
                item_type = item[0]

                if item_type == "l":
                    shape.draw_line(item[1], item[2])
                elif item_type == "re":
                    rect = item[1]
                    shape.draw_rect(rect)

            width = path.get("width", 1.0)
            if width is None:
                width = 1.0

            shape.finish(
                color=color,
                fill=color,
                width=width,
                stroke_opacity=stroke_opacity,
                fill_opacity=fill_opacity
            )

        shape.commit()

def color_drawings(doc: fitz.Document, color_rgb: tuple[float, float, float]):
    rgb_fill, rgb_stroke = rgb_to_pdf_color(color_rgb)
    fill_cmd = rgb_fill.strip()
    stroke_cmd = rgb_stroke.strip()
    for page in doc:
        for xref in page.get_contents():
            raw_code = doc.xref_stream(xref)
            
            new_code = raw_code
            new_code = new_code.replace(b"\n0 G\n", b"\n" + rgb_stroke + b"\n")
            new_code = new_code.replace(b"\n0 g\n", b"\n" + rgb_fill + b"\n")
            
            new_code = rgb_fill + rgb_stroke + new_code
            doc.update_stream(xref, new_code)

        resources_list = page.get_xobjects()
        for resource in resources_list:
            xref = resource[0]
            raw_code = doc.xref_stream(xref)
            new_code = raw_code
            
            new_code = new_code.replace(b" 0 g", b" " + fill_cmd)
            new_code = new_code.replace(b"\n0 g", b"\n" + fill_cmd)
            new_code = new_code.replace(b" 0 G", b" " + stroke_cmd)
            new_code = new_code.replace(b"\n0 G", b"\n" + stroke_cmd)
            
            new_code = new_code.replace(b"0 0 0 rg", fill_cmd)
            new_code = new_code.replace(b"0 0 0 RG", stroke_cmd)
            new_code = rgb_fill + rgb_stroke + new_code
            doc.update_stream(xref, new_code)
    

def color_images(doc: fitz.Document, color_rgb: tuple[float, float, float]):
    target_r, target_g, target_b = tuple(int(c * 255) for c in color_rgb)

    for page in doc:
        image_list = page.get_images(full=True)
        
        for img_info in image_list:
            xref = img_info[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
        
            img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
            
            data = img.getdata()
            new_data = []
            
            for item in data:
                if item[0] < 50 and item[1] < 50 and item[2] < 50 and item[3] > 0:
                    new_data.append((target_r, target_g, target_b, item[3]))
                else:
                    new_data.append(item)
            
            img.putdata(new_data)
            
            output_buffer = io.BytesIO()
            img.save(output_buffer, format="PNG")
            new_image_bytes = output_buffer.getvalue()
        
            page.replace_image(xref, stream=new_image_bytes)

def PDFColor(input_pdf: str, output_pdf: str, color_rgb: tuple[float, float, float], include_shapes=False):
    doc = fitz.open(input_pdf)

    if include_shapes:
        color_shapes(doc, color_rgb)
    color_text(doc, color_rgb)
    color_drawings(doc, color_rgb)
    color_images(doc, color_rgb)

    doc.save(output_pdf)
    doc.close()

if __name__ == "__main__":
    PDFColor("in.pdf", "done.pdf", (1,0,1))