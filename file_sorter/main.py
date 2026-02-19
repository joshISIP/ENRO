import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from datetime import datetime

from db.db_manager import (
    create_table,
    insert_document,
    fetch_documents,
    get_document_by_id,
    document_exists
)

from utils.pdf_classifier import classify_letter
from utils.file_scanner import scan_documents
from utils.drive_scanner import get_available_drives 
from utils.audit_logger import log_action  

# 🔥 Initialize database
create_table()
current_sort = {"column": None, "reverse": False}
def create_folder(folder_path):
    """Create a folder if it doesn't exist"""
    try:
        os.makedirs(folder_path, exist_ok=True)
        return True
    except Exception as e:
        messagebox.showerror("Folder Creation Error", str(e))
        return False 


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


import shutil

def get_file_type_folder(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return "PDF"
    elif ext == ".docx":
        return "Word"
    elif ext == ".xlsx":
        return "Excel"
    elif ext == ".pptx":
        return "PowerPoint"
    else:
        return "Other"



def select_folder():
    folder = filedialog.askdirectory(title="Select Folder")
    if not folder:
        return

    files = scan_documents(folder)

    if not files:
        messagebox.showwarning("No Files", "No supported documents found.")
        return

    sorted_root = os.path.join(folder, "Sorted_Documents")
    create_folder(sorted_root)

    count = 0
    for file_path in files:
        if document_exists(file_path):
            continue

        filename = os.path.basename(file_path)
        source = "USB" if ":\\" in file_path else "HDD"

        # 🔹 LEVEL 1: File Type Folder
        type_folder_name = get_file_type_folder(file_path)
        type_folder = os.path.join(sorted_root, type_folder_name)
        create_folder(type_folder)

        # 🔹 Classify document content
        classification = classify_letter(file_path)

        # 🔹 LEVEL 2: Classification Folder
        class_folder = os.path.join(type_folder, classification)
        create_folder(class_folder)

        # Final destination
        new_path = os.path.join(class_folder, filename)

        try:
            shutil.move(file_path, new_path)
        except:
            new_path = file_path  # fallback

        insert_document(filename, new_path, source, classification)
        count += 1
        
        log_action("ADD", filename, f"Source: {source}, Type: {classification}")

    messagebox.showinfo("Success", f"{count} files sorted into 2-level folders.")
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
        os.startfile(file_path)
        log_action(
            "OPEN",
            os.path.basename(file_path),
            "File opened by user"
        )
    except Exception as e:
        log_action("ERROR", os.path.basename(file_path), str(e))
        messagebox.showerror("Open Error", str(e))




def auto_scan_drives():
    drives = get_available_drives()
    total_saved = 0

    for drive in drives:
        log_action("AUTO_SCAN", "", F"Scanning drive {drive}")
        if drive.upper().startswith("C:"):
            continue

        sorted_root = os.path.join(drive, "Sorted_Documents")
        create_folder(sorted_root)

        files = scan_documents(drive)

        for file_path in files:
            if document_exists(file_path):
                continue

            filename = os.path.basename(file_path)
            source = "USB"

            # LEVEL 1: File type
            type_folder_name = get_file_type_folder(file_path)
            type_folder = os.path.join(sorted_root, type_folder_name)
            create_folder(type_folder)

            # LEVEL 2: Classification
            classification = classify_letter(file_path)
            class_folder = os.path.join(type_folder, classification)
            create_folder(class_folder)

            new_path = os.path.join(class_folder, filename)

            try:
                shutil.move(file_path, new_path)
            except:
                new_path = file_path

            insert_document(filename, new_path, source, classification)
            log_action("ADD", filename, f"Auto scanned from USB → {classification}")
            total_saved += 1

    messagebox.showinfo(
        "Auto Scan Complete",
        f"{total_saved} files sorted with 2-level folders."
    )

    load_documents()
 



    
    
def sort_by_type():
    """Sort documents by letter type"""
    current_sort["column"] = "Letter Type"
    current_sort["reverse"] = not current_sort["reverse"]
    load_documents(sort_by="letter_type")
    
    
def sort_by_date():
    """Sort documents by date added"""
    current_sort["column"] = "Date Added"
    current_sort["reverse"] = not current_sort["reverse"]
    load_documents(sort_by="date_added")
    
    
def open_audit_trail():
    if os.path.exists("audit_trail.log"):
        os.startfile("audit_trail.log")
        
    else:
        messagebox.showinfo("Audit log", "No audit log found yet.")


# ---------------- GUI ---------------- #

root = tk.Tk()
root.title("Document Sorter")
root.geometry("1000x550")
root.resizable(False, False)

title_lbl = tk.Label(root, text="Document Sorter", font=("Arial", 24, "bold"))

title_lbl.pack(pady=10)

top_frame = tk.Frame(root)
top_frame.pack(pady=10)

tk.Button(top_frame, text="➕ Add Documents",
          command=select_folder, width=15).grid(row=0, column=0, padx=5)

tk.Button(top_frame, text="⚡ Auto Scan USB",
          command=auto_scan_drives, width=18).grid(row=0, column=1, padx=5)

search_entry = tk.Entry(top_frame, width=30)
search_entry.grid(row=0, column=2, padx=5)

tk.Button(top_frame, text="🔍 Search",
          command=search_documents, width=10).grid(row=0, column=3, padx=5)

tk.Button(top_frame, text="📄 Audit Trail", command=open_audit_trail, width=15).grid(row=0, column=4, padx=5)


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
