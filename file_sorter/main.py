import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

from utils.file_scanner import scan_pdfs
from db.db_manager import insert_document, fetch_documents

import subprocess
from db.db_manager import get_document_by_id






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










root = tk.Tk()
root.title("PDF Sorter")
root.geometry("900x550")
root.resizable(False, False)

title_lbl = tk.Label(root, text="PDF Sorter System", font=("Arial", 18))
title_lbl.pack(pady=10)

top_frame = tk.Frame(root)
top_frame.pack(pady=5)

add_btn = tk.Button(top_frame, text="Add PDFs", command=select_folder, width=15)
add_btn.pack(side=tk.LEFT, padx=5)

search_entry = tk.Entry(top_frame, width=30)
search_entry.pack(side=tk.LEFT, padx=5)

search_btn = tk.Button(top_frame, text="Search", command=search_documents)
search_btn.pack(side=tk.LEFT, padx=5)










columns = ("ID", "Title", "Source", "Date Added")

tree = ttk.Treeview(root, columns=columns, show="headings", height=18)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor=tk.CENTER, width=200 if col != "Title" else 300)
    

tree.pack(pady=10)
tree.bind("<Double-1>", open_pdf)

load_documents()

root.mainloop()

