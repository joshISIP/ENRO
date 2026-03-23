import PyPDF2

# ===============================
# PDF TEXT EXTRACTOR
# ===============================
def extract_text_from_pdf(path):
    text = ""
    try:
        with open(path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + " "
    except:
        pass

    return text.lower()


# ===============================
# SMART ENRO / LGU CLASSIFIER
# ===============================
def classify_letter(file_path):
    text = extract_text_from_pdf(file_path)

    # -----------------------------
    # NOTICE OF VIOLATION (High Priority)
    # -----------------------------
    if any(keyword in text for keyword in [
        "notice of violation",
        "violation",
        "non-compliance",
        "failure to comply",
        "environmental violation",
        "penalty",
        "fine imposed"
    ]):
        return "Notice of Violation"

    # -----------------------------
    # OFFICIAL RECEIPT
    # -----------------------------
    elif any(keyword in text for keyword in [
        "official receipt",
        "receipt no",
        "or no",
        "amount paid",
        "cash received",
        "payment received"
    ]):
        return "Official Receipt"

    # -----------------------------
    # MEMORANDUM
    # -----------------------------
    elif any(keyword in text for keyword in [
        "memorandum",
        "memo",
        "for:",
        "subject:",
        "from:",
        "date:"
    ]):
        return "Memorandum"

    # -----------------------------
    # CERTIFICATION
    # -----------------------------
    elif any(keyword in text for keyword in [
        "certification",
        "this is to certify",
        "certify that",
        "issued this",
        "signed this"
    ]):
        return "Certification"

    # -----------------------------
    # ENVIRONMENTAL REPORT
    # -----------------------------
    elif any(keyword in text for keyword in [
        "environmental report",
        "inspection report",
        "site inspection",
        "monitoring report",
        "compliance report",
        "solid waste",
        "waste management",
        "environmental assessment",
        "findings",
        "recommendation"
    ]):
        return "Environmental Report"

    else:
        return "Uncategorized"