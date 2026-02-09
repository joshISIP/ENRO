import os

def scan_pdfs(folder_path):
    """
    Scan the given folder for PDF files.
    Returns a list of full file paths.
    """

    pdf_files = []
    if not os.path.exists(folder_path):
        return  pdf_files
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".pdf"):
                full_path = os.path.join(root, file)
                pdf_files.append(full_path)

    return pdf_files