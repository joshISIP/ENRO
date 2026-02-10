import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

from utils.file_scanner import scan_pdfs
from db.db_manager import insert_document, fetch_documents

import subprocess
from db.db_manager import get_document_by_id


from utils.drive_scanner import get_available_drives
from db.db_manager import document_exists







def load_documents(filter_text=""):
    for row in tree.get_children():
        tree.delete(row)

    documents = fetch_documents()

    for doc in documents:
        doc_id, title, path, source, date_added = doc

        if filter_text.lower() in title.lower():
            tree.insert("", "end", values=(doc_id, title, path, source, date_added))

            

def select_folder():
    folder = filedialog.askdirectory(title="Select Folder")
    if not folder:
        return
    
    pdfs = scan_pdfs(folder)

    if not pdfs:
        messagebox.showwarning("No PDFs", "No PDF files found in this folder")
        return
    
    count = 0
    for pdf_path in pdfs:
        title = os.path.basename(pdf_path)
        source = "USB" if ":\\\\" in pdf_path else "HDD"
        insert_document(title, pdf_path, source)
        count += 1

    messagebox.showinfo("Success", f"{count} PDFs registered successfully")
    load_documents()

def search_documents():
    keyword = search_entry.get()
    load_documents(keyword)







def open_pdf(event):
    selected = tree.focus()
    if not selected:
        return
    
    values = tree.item(selected, "values")
    doc_id = values[0]

    file_path = get_document_by_id(doc_id)

    if not file_path or not os.path.exists(file_path):
        messagebox.showerror(
            "File Not Found",
            "The PDF file could not be found. \nPlease make sure the external drive is inserted."
        )
        return
    
    try:
        os.startfile(file_path)
    except Exception as e:
        messagebox.showerror("Error", str(e))





def auto_scan_drives():
    drives = get_available_drives()
    total_saved = 0

    for drive in drives:
        # Skip system drive C:
        if drive.upper().startswith("C:"):
            continue

        pdfs = scan_pdfs(drive)

        for pdf_path in pdfs:
            if document_exists(pdf_path):
                continue  # Skip duplicates

            title = os.path.basename(pdf_path)
            source = "USB" if drive.upper() != "C:\\" else "HDD"

            insert_document(title, pdf_path, source)
            total_saved += 1

    messagebox.showinfo(
        "Auto Scan Complete",
        f"{total_saved} new PDF files were registered."
    )

    load_documents()










root = tk.Tk()
root.title("PDF Sorter")
root.geometry("900x550")
root.resizable(False, False)

title_lbl = tk.Label(
    root, text="PDF Sorter", font=("Arial", 24, "bold"), fg="#333"
)
title_lbl.pack(pady=10)

top_frame = tk.Frame(root)
top_frame.pack(pady=10)

btn_add = tk.Button(
    top_frame,
    text="➕ Add PDFs",
    command=select_folder,
    width=15
)
btn_add.grid(row=0, column=0, padx=5)

btn_auto = tk.Button(
    top_frame,
    text="⚡ Auto Scan USB/HDD",
    command=auto_scan_drives,
    width=18
)
btn_auto.grid(row=0, column=1, padx=5)

search_entry = tk.Entry(top_frame, width=30)
search_entry.grid(row=0, column=2, padx=5)

btn_search = tk.Button(
    top_frame,
    text="🔍 Search",
    command=search_documents,
    width=10
)
btn_search.grid(row=0, column=3, padx=5)





























columns = ("ID", "Title", "Path", "Source", "Date Added")

tree = ttk.Treeview(root, columns=columns, show="headings", height=18)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor=tk.CENTER, width=200 if col != "Title" else 300)
    tree.column("ID", width=60)
    tree.column("Title", width=380)
    tree.column("Source", width=100)
    tree.column("Date Added", width=200)

    

tree.pack(pady=10)
tree.bind("<Double-1>", open_pdf)

load_documents()

root.mainloop()

