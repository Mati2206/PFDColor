import fitz  # PyMuPDF

def colorRgbToPdf(color_rgb: tuple[float, float, float]) -> tuple:
    r, g, b = color_rgb
    return (f"{r} {g} {b} rh\n".encode(), f"{r} {g} {b} RG\n".encode())

def colorText(doc: fitz.Document, color_rgb: tuple[float, float, float]):
    r, g, b = color_rgb
    rgb_fill, rgb_stroke = colorRgbToPdf(color_rgb)

    for page in doc:
        for xref in page.get_contents():
            raw_code = doc.xref_stream(xref)
            new_code = rgb_fill + rgb_stroke + raw_code
            doc.update_stream(xref, new_code)

def colorDrawing(doc: fitz.Document, color_rgb: tuple[float, float, float]):
    r, g, b = color_rgb
    rgb_fill, rgb_stroke = colorRgbToPdf(color_rgb)

    for page in doc:
        resources_list = page.get_xobjects()
        
        for resource in resources_list:
            xref = resource[0]

            raw_code = doc.xref_stream(xref)
            new_code = raw_code
            new_code = new_code.replace(b"\n0 g\n", b"\n" + rgb_fill + b"\n")
            
            new_code = rgb_fill + rgb_stroke + new_code
            doc.update_stream(xref, new_code)

def PDFColor(input_pdf: str, output_pdf: str, color_rgb: tuple[float, float, float]):
    doc = fitz.open(input_pdf)

    colorText(doc, color_rgb)
    colorDrawing(doc, color_rgb)

    doc.save(output_pdf)
    doc.close()

# Run the script
PDFColor("1a.pdf", "done.pdf", color_rgb=(1.0, 0.0, 1.0))