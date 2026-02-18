import os

SUPPORTED_EXTENSIONS = (".pdf", ".docx", ".xlsx", ".pptx")

def scan_documents(folder_path):
    """Scan folder for supported documents"""
    found_files = []

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(SUPPORTED_EXTENSIONS):
                found_files.append(os.path.join(root, file))

    return found_files
