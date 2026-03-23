import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import webbrowser
import threading 

from db.db_manager import (
    create_table,
    insert_document,
    fetch_documents,
    document_exists,
    get_categories,
    get_documents_by_category
)


from utils.pdf_classifier import classify_letter
from utils.file_scanner import scan_documents
from utils.audit_logger import log_action
from utils.drive_scanner import get_available_drives
from utils.monthly_stats import print_monthly_report, get_monthly_stats, get_total_scanned_per_month

# INIT DB
create_table()
# ================= WINDOW =================
root = tk.Tk()
root.title("DMS - Document Management System")
root.geometry("1150x650")
root.configure(bg="#f4f6f8")

selected_drive = tk.StringVar()

is_scanning = False

# ================= SIDEBAR =================
sidebar = tk.Frame(root, bg="#2c3e50", width=200)
sidebar.pack(side="left", fill="y")

tk.Label(sidebar, text="DMS", fg="white", bg="#2c3e50",
         font=("Segoe UI", 18, "bold")).pack(pady=20)

# ================= MAIN =================
main = tk.Frame(root, bg="white")
main.pack(side="right", fill="both", expand=True)

root.rowconfigure(0, weight=1)
root.columnconfigure(1, weight=1) 

# ================= TOPBAR =================
topbar = tk.Frame(main, bg="white")
topbar.pack(fill="x", pady=10, padx=15)

search_var = tk.StringVar()

# Search Bar
ttk.Entry(topbar, textvariable=search_var, width=25).pack(side="left", padx=5)


# DRIVE DROPDOWN
drive_box = ttk.Combobox(topbar, textvariable=selected_drive, width=8)
drive_box['values'] = get_available_drives()
drive_box.pack(side="left", padx=5)
drive_box.set("Drive")

# ================= EXPLORER =================
explorer = tk.Frame(main)
explorer.pack(fill="both", expand=True)

# Grid layout for responsiveness
explorer.columnconfigure(0, weight=1)  # sidebar tree
explorer.columnconfigure(1, weight=4)  # table
explorer.rowconfigure(0, weight=1)

# LEFT TREE
folder_tree = ttk.Treeview(explorer)
folder_tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

# CENTER TABLE
columns = ("Name", "Type", "Category", "Date", "Source")
tree = ttk.Treeview(explorer, columns=columns, show="headings")
tree.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="w", stretch=True, width=120)
# ================= FUNCTIONS =================

def load_folder_tree():
    folder_tree.delete(*folder_tree.get_children())
    root_node = folder_tree.insert("", "end", text="📁 Documents", open=True)

    for cat, count in get_categories():
        folder_tree.insert(root_node, "end", text=f"{cat} ({count})")


def show_files(docs=None):
    tree.delete(*tree.get_children())
    docs = docs if docs else fetch_documents()

    for doc in docs:
        _, title, path, source, category, date = doc
        ext = os.path.splitext(title)[1].upper()
        tree.insert("", "end", values=(title, ext, category, date, source))


def on_folder_click(event):
    selected = folder_tree.focus()
    if not selected:
        return

    text = folder_tree.item(selected, "text")

    # Root click = show all
    if text == "📁 Documents":
        show_files()
        return

    # Remove count
    category = text.split(" (")[0].strip().lower()

    # Normalize database comparison
    all_docs = fetch_documents()
    filtered = []

    for doc in all_docs:
        db_category = (doc[4] or "").strip().lower()
        if db_category == category:
            filtered.append(doc)

    show_files(filtered)
    
    
def open_file(event=None):
    selected = tree.focus()
    if not selected:
        return

    filename = tree.item(selected, "values")[0]

    for doc in fetch_documents():
        if doc[1] == filename and os.path.exists(doc[2]):
            webbrowser.open(doc[2])
            log_action("OPEN", filename, doc[4])
            break


def choose_folder():
    drive = selected_drive.get()
    if not drive or drive == "Drive":
        messagebox.showwarning("Warning", "Select drive first")
        return None
    return filedialog.askdirectory(initialdir=drive)


def scan_finished():
    global is_scanning

    is_scanning = False

    show_files()
    load_folder_tree()
    messagebox.showinfo("Done", "Scan completed ✅")
    
def scan_folder():
    global is_scanning

    if is_scanning:
        messagebox.showwarning("Scanning", "Scan already in progress...")
        return

    folder = choose_folder()
    if not folder:
        return

    is_scanning = True

    threading.Thread(
        target=scan_worker,
        args=(folder,),
        daemon=True
    ).start()  


def scan_worker(folder):
    for file in scan_documents(folder):
        if document_exists(file):
            continue

        title = os.path.basename(file)
        category = classify_letter(file).strip().title()

        insert_document(title, file, folder, category, "")
        log_action("SCAN", title, category)

    # ✅ CALL ONCE AFTER LOOP FINISHES
    root.after(0, scan_finished)
    
    
def show_monthly_stats():
    try:
        year = int(stats_year.get())
        month = int(stats_month.get())
        report = print_monthly_report(year, month)
        messagebox.showinfo("Monthly Stats", report)
    except ValueError:
        messagebox.showerror("Error", "Enter valid year/month (e.g. 2026 / 3)")

def search_docs():
    keyword = search_var.get().lower()
    filtered = [d for d in fetch_documents() if keyword in str(d).lower()]
    show_files(filtered)





# ================= BINDS =================
folder_tree.bind("<<TreeviewSelect>>", on_folder_click)
tree.bind("<Double-1>", open_file)

# Search Button (beside search bar)
ttk.Button(topbar, text="🔍 Search", command=search_docs).pack(side="left", padx=5)

# Stats inputs
stats_year = tk.StringVar(value="2026")
stats_month = tk.StringVar(value="3")
ttk.Entry(topbar, textvariable=stats_year, width=5).pack(side="left", padx=2)
ttk.Label(topbar, text="/").pack(side="left")
ttk.Entry(topbar, textvariable=stats_month, width=3).pack(side="left", padx=2)
ttk.Button(topbar, text="📊 Stats", command=lambda: show_monthly_stats()).pack(side="left", padx=5)

# Scan Button
ttk.Button(topbar, text="📂 Scan", command=scan_folder).pack(side="left", padx=5)

# ================= START =================
show_files()
load_folder_tree()
root.mainloop()

