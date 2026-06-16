import fitz  # PyMuPDF

def PDFColor(input_pdf, output_pdf, color_rgb):
    doc = fitz.open(input_pdf)
    r, g, b = color_rgb

    rgb_fill = f"{r} {g} {b} rg\n".encode()
    rgb_stroke = f"{r} {g} {b} RG\n".encode()
    
    for page in doc:

        for xref in page.get_contents():
            raw_code = doc.xref_stream(xref)
            new_code = rgb_fill + rgb_stroke + raw_code
            doc.update_stream(xref, new_code)
            
        resources_list = page.get_xobjects()
        
        for resource in resources_list:
            xref = resource[0]

            raw_code = doc.xref_stream(xref)
            new_code = raw_code
            new_code = new_code.replace(b"\n0 g\n", b"\n" + rgb_fill + b"\n")
            
            new_code = rgb_fill + rgb_stroke + new_code
            doc.update_stream(xref, new_code)
            

    doc.save(output_pdf)
    doc.close()
    print("Done! Deep label structures searched. Check the output file.")

# Run the script
PDFColor("1a.pdf", "done.pdf", color_rgb=(1, 0, 1))