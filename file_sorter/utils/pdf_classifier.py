import PyPDF2

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""
    except:
        pass
    return text.lower()


def classify_letter(pdf_path):
    text = extract_text_from_pdf(pdf_path)

    if any(word in text for word in ["invoice", "amount due", "billing", "payment due"]):
        return "Invoice"

    elif any(word in text for word in ["curriculum vitae", "resume", "education", "skills"]):
        return "Resume"

    elif any(word in text for word in ["contract", "agreement", "terms and conditions"]):
        return "Contract"

    elif any(word in text for word in ["request letter", "i am writing to request", "approval"]):
        return "Request Letter"

    elif any(word in text for word in ["report", "summary report", "findings"]):
        return "Report"

    else:
        return "Uncategorized"
