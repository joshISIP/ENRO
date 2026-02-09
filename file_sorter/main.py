import tkinter as tk
from tkinter import filedialog, messagebox
import os

from utils.file_scanner import scan_pdfs
from db.db_manager import insert_document



def select_folder():
    folder = filedialog.askdirectory(title="Select Folder")
    if not folder:
        return
    
    pdfs = scan_pdfs(folder)

    if not pdfs:
        messagebox.showwarning("No PDFs", "No PDF files found in this folder")
        return
    
    saved_count = 0

    for pdf_path in pdfs:
        title = os.path.basename(pdf_path)
        source = "USB" if ":\\\\" in pdf_path else "HDD"

        insert_document(
            title=title,
            file_path=pdf_path,
            source=source
        )

        saved_count += 1

    messagebox.showinfo(
        "Success",
        f"{saved_count} PDF files have been succesfully registered!"
    )



root = tk.Tk()
root.title("File Sorter")
root.geometry("500x200")
root.resizable(False, False)

label = tk.Label(root, text="File Sorter")
font=("Arial", 20)
label.pack(pady=20)


btn_scan = tk.Button(
    text="Select Folder",
    command=select_folder,
    width=30,
    height=2
)
btn_scan.pack(pady=20)





from db.db_manager import fetch_documents
print(fetch_documents())





root.mainloop()