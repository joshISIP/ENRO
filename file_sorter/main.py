import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

from db.db_manager import (
    create_table,
    insert_document,
    fetch_documents,
    get_document_by_id,
    document_exists
)

from utils.pdf_classifier import classify_letter
from utils.file_scanner import scan_pdfs
from utils.drive_scanner import get_available_drives

# 🔥 Initialize database
create_table()


def load_documents(filter_text=""):
    for row in tree.get_children():
        tree.delete(row)

    documents = fetch_documents()

    for doc in documents:
        doc_id, title, path, source, letter_type, date_added = doc

        if filter_text.lower() in title.lower():
            tree.insert("", "end", values=(
                doc_id,
                title,
                letter_type,
                path,
                source,
                date_added
            ))


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
        if document_exists(pdf_path):
            continue

        title = os.path.basename(pdf_path)
        source = "USB" if ":\\" in pdf_path else "HDD"
        letter_type = classify_letter(pdf_path)

        insert_document(title, pdf_path, source, letter_type)
        count += 1

    messagebox.showinfo("Success", f"{count} PDFs registered successfully")
    load_documents()


def search_documents():
    keyword = search_entry.get()
    load_documents(keyword)


def open_selected_file():
    selected_item = tree.focus()

    if not selected_item:
        messagebox.showwarning("No Selection", "Please select a file first.")
        return

    values = tree.item(selected_item, "values")

    if not values:
        return

    doc_id = int(values[0])  # ensure it's integer

    file_path = get_document_by_id(doc_id)

    if not file_path:
        messagebox.showerror("Error", "File path not found in database.")
        return

    if not os.path.exists(file_path):
        messagebox.showerror(
            "File Not Found",
            "The file cannot be found.\nPlease insert the external drive."
        )
        return

    try:
        os.startfile(file_path)  # Windows default opener
    except Exception as e:
        messagebox.showerror("Open Error", str(e))



def auto_scan_drives():
    drives = get_available_drives()
    total_saved = 0

    for drive in drives:
        if drive.upper().startswith("C:"):
            continue

        pdfs = scan_pdfs(drive)

        for pdf_path in pdfs:
            if document_exists(pdf_path):
                continue

            title = os.path.basename(pdf_path)
            source = "USB"
            letter_type = classify_letter(pdf_path)

            insert_document(title, pdf_path, source, letter_type)
            total_saved += 1

    messagebox.showinfo(
        "Auto Scan Complete",
        f"{total_saved} new PDF files were registered."
    )

    load_documents()


# ---------------- GUI ---------------- #

root = tk.Tk()
root.title("PDF Sorter")
root.geometry("1000x550")
root.resizable(False, False)

title_lbl = tk.Label(
    root, text="PDF Sorter", font=("Arial", 24, "bold")
)
title_lbl.pack(pady=10)

top_frame = tk.Frame(root)
top_frame.pack(pady=10)

tk.Button(top_frame, text="➕ Add PDFs",
          command=select_folder, width=15).grid(row=0, column=0, padx=5)

tk.Button(top_frame, text="⚡ Auto Scan USB",
          command=auto_scan_drives, width=18).grid(row=0, column=1, padx=5)

search_entry = tk.Entry(top_frame, width=30)
search_entry.grid(row=0, column=2, padx=5)

tk.Button(top_frame, text="🔍 Search",
          command=search_documents, width=10).grid(row=0, column=3, padx=5)


columns = ("ID", "Title", "Letter Type", "Path", "Source", "Date Added")
tree = ttk.Treeview(root, columns=columns, show="headings", height=18)

for col in columns:
    tree.heading(col, text=col)

tree.column("ID", width=60)
tree.column("Title", width=250)
tree.column("Letter Type", width=150)
tree.column("Path", width=250)
tree.column("Source", width=80)
tree.column("Date Added", width=150)

tree.pack(pady=10)
tree.bind("<Double-1>", lambda event: open_selected_file())


load_documents()
root.mainloop()
