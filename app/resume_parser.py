import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes  

def extract_text_from_pdf(uploaded_file):
    """
    Extract text from uploaded resume (PDF).
    Falls back to OCR if no extractable text is found.
    """
    try:
        file_bytes = uploaded_file.read()  
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()

        # Fallback to OCR for scanned PDFs
        if len(text.strip()) < 100:
            print("Fallback to OCR")
            images = convert_from_bytes(file_bytes)
            for image in images:
                text += pytesseract.image_to_string(image)

        return text.strip()

    except Exception as e:
        print("Error parsing PDF:", e)
        return ""




