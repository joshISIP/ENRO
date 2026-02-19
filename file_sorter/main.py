import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import webbrowser

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

# ===============================
# INIT DATABASE
# ===============================
create_table()

# ===============================
# MAIN WINDOW
# ===============================
root = tk.Tk()
root.title("DMS - Document Management System")
root.geometry("1100x650")
root.configure(bg="#f4f6f8")

selected_drive = tk.StringVar()

# ===============================
# SIDEBAR
# ===============================
sidebar = tk.Frame(root, bg="#2c3e50", width=200)
sidebar.pack(side="left", fill="y")

tk.Label(sidebar, text="DMS", fg="white", bg="#2c3e50",
         font=("Segoe UI", 18, "bold")).pack(pady=20)

# Audit viewer
def show_audit_trail():
    if not os.path.exists("audit_trail.log"):
        messagebox.showinfo("Audit Trail", "No logs found.")
        return

    win = tk.Toplevel(root)
    win.title("Audit Trail")
    win.geometry("700x400")

    text = tk.Text(win)
    text.pack(fill="both", expand=True)

    with open("audit_trail.log", "r", encoding="utf-8") as f:
        text.insert("1.0", f.read())

tk.Button(sidebar, text="📜 Audit Trail", bg="#34495e",
          fg="white", relief="flat",
          command=show_audit_trail).pack(fill="x", pady=5)

# ===============================
# MAIN AREA
# ===============================
main = tk.Frame(root, bg="white")
main.pack(side="right", fill="both", expand=True)

# ===============================
# TOP BAR
# ===============================
topbar = tk.Frame(main, bg="white")
topbar.pack(fill="x", pady=10, padx=10)

search_var = tk.StringVar()

ttk.Entry(topbar, textvariable=search_var, width=25).pack(side="left", padx=5)

# DRIVE DROPDOWN
drive_box = ttk.Combobox(topbar, textvariable=selected_drive, width=8)
drive_box['values'] = get_available_drives()
drive_box.pack(side="left", padx=5)
drive_box.set("Drive")

# ===============================
# CONTENT SPLIT (Folders + Files)
# ===============================
content = tk.Frame(main, bg="white")
content.pack(fill="both", expand=True)

# LEFT PANEL = Virtual folders
folder_panel = tk.Frame(content, width=250, bg="#ecf0f1")
folder_panel.pack(side="left", fill="y")

tk.Label(folder_panel, text="📁 Virtual Folders",
         bg="#ecf0f1", font=("Segoe UI", 12, "bold")).pack(pady=10)

folder_list = tk.Listbox(folder_panel, font=("Segoe UI", 11))
folder_list.pack(fill="both", expand=True, padx=10, pady=10)

# RIGHT PANEL = Files table
file_panel = tk.Frame(content, bg="white")
file_panel.pack(side="right", fill="both", expand=True)

columns = ("ID", "Title", "Path", "Source", "Type", "Date")
tree = ttk.Treeview(file_panel, columns=columns, show="headings")
tree.pack(fill="both", expand=True, padx=10, pady=10)

for col in columns:
    tree.heading(col, text=col)

# ===============================
# STATUS BAR
# ===============================
status = tk.Label(root, text="Ready", bd=1, relief="sunken", anchor="w")
status.pack(side="bottom", fill="x")

# ===============================
# FUNCTIONS
# ===============================

def refresh_table(data=None):
    tree.delete(*tree.get_children())
    docs = data if data else fetch_documents()

    for doc in docs:
        tree.insert("", "end", values=doc)

    status.config(text=f"{len(docs)} documents loaded")
    
def load_virtual_folders():
    folder_list.delete(0, tk.END)
    categories = get_categories()

    for cat, count in categories:
        folder_list.insert(tk.END, f"{cat} ({count})")

def open_virtual_folder(event):
    selection = folder_list.curselection()
    if not selection:
        return

    text = folder_list.get(selection[0])
    category = text.split(" (")[0]

    docs = get_documents_by_category(category)
    refresh_table(docs)

folder_list.bind("<<ListboxSelect>>", open_virtual_folder)



# SELECT FOLDER FROM DRIVE
def choose_folder():
    drive = selected_drive.get()
    if not drive or drive == "Drive":
        messagebox.showwarning("Warning", "Select a drive first")
        return None

    folder = filedialog.askdirectory(initialdir=drive)
    return folder


def scan_folder():
    folder = choose_folder()
    if not folder:
        return

    files = scan_documents(folder)

    for file in files:
        if document_exists(file):
            continue

        category = classify_letter(file)
        title = os.path.basename(file)

        insert_document(
            title=title,
            path=file,
            source=folder,
            letter_type=category
        )

        log_action("SCAN", title, category)

    refresh_table()
    load_virtual_folders()



def search_docs():
    keyword = search_var.get().lower()
    all_docs = fetch_documents()
    filtered = [d for d in all_docs if keyword in str(d).lower()]
    refresh_table(filtered)


def open_selected():
    selected = tree.focus()
    if not selected:
        messagebox.showwarning("Warning", "No document selected")
        return

    values = tree.item(selected, "values")
    path = values[2]

    if os.path.exists(path):
        webbrowser.open(path)
        log_action("OPEN", values[1], values[4])
    else:
        messagebox.showerror("Error", "File not found")

# ===============================
# BUTTONS
# ===============================
btn_frame = tk.Frame(topbar, bg="white")
btn_frame.pack(side="right")

ttk.Button(btn_frame, text="🔍 Search", command=search_docs).pack(side="left", padx=5)
ttk.Button(btn_frame, text="📂 Scan Folder", command=scan_folder).pack(side="left", padx=5)
ttk.Button(btn_frame, text="📄 Open", command=open_selected).pack(side="left", padx=5)

# ===============================
# START
# ===============================
refresh_table()
load_virtual_folders()
root.mainloop()

