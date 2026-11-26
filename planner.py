import tkinter as tk
import json
import os
from datetime import datetime
from tkinter import messagebox, ttk

DATE_FORMAT = "%m-%d-%Y"
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assignments.json")

assignments = []

def validate_assignment(name, due_date, difficulty):
    name = str(name).strip()

    if not name:
        raise ValueError("Enter an assignment name.")

    due_date = str(due_date).strip()

    try:
        datetime.strptime(due_date, DATE_FORMAT)
    except ValueError:
        raise ValueError("Due date must be in MM-DD-YYYY format.")

    try:
        difficulty = int(str(difficulty).strip())
    except ValueError:
        raise ValueError("Difficulty must be a whole number from 1 to 5.")
    
    if not 1 <= difficulty <= 5:
        raise ValueError("Difficulty must be a whole number from 1 to 5.")

    return {
        "name": name,
        "due_date": due_date,
        "difficulty": difficulty,
    }

def load_assignments(path):
    if not os.path.exists(path):
        return []
    
    with open(path, encoding="utf-8") as file:
        data = json.load(file)

    loaded = []

    for item in data:
        assignment = validate_assignment(item["name"], item["due_date"], item["difficulty"])
        assignment["completed"] = bool(item.get("completed", False))
        loaded.append(assignment)

    return loaded

def save_assignments(path, items):
    temp_path = path + ".tmp"

    with open(temp_path, "w", encoding="utf-8") as file:
        json.dump(items, file, indent=2)

    os.replace(temp_path, path)

def load_data():
    try:
        return load_assignments(DATA_FILE)
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        messagebox.showerror(
            "Could not load assignments, starting with an empty list."
        )
        
        return []

def save_data():
    save_assignments(DATA_FILE, assignments)

def add_assignment():
    try:
        assignment = validate_assignment(
            name_entry.get(), due_entry.get(), difficulty_entry.get()
        )
    except ValueError as error:
        messagebox.showerror("Invalid assignment", str(error))

        return
    
    assignment["completed"] = False
    assignments.append(assignment)
    save_data()
    refresh_list()
    clear_form()

def clear_form():
    name_entry.delete(0, tk.END)
    due_entry.delete(0, tk.END)
    difficulty_entry.delete(0, tk.END)
    name_entry.focus_set()

def refresh_list():
    sort_assignments(assignments)
    tree.delete(*tree.get_children())

    for index, assignment in enumerate(assignments):
        status = "✓ Done" if assignment["completed"] else "To Do"
        
        tree.insert(
            "",
            tk.END,
            iid=str(index),
            values=(status, assignment["name"], assignment["due_date"], assignment["difficulty"]),
            tags=("done",) if assignment["completed"] else (),
        )

def toggle_complete():
    selection = tree.selection()

    if not selection:
        messagebox.showinfo("No assignment selected", "Select an assignment in the list.")

        return
    
    assignment = assignments[int(selection[0])]
    assignment["completed"] = not assignment["completed"]
    save_data()
    refresh_list()

def delete_selected():
    selection = tree.selection()

    if not selection:
        messagebox.showinfo("No assignment selected", "Select an assignment in the list.")

        return
    
    assignment = assignments[int(selection[0])]

    if not messagebox.askyesno("Delete assignment", f"Delete \"{assignment['name']}\"?"):
        return
    
    assignments.remove(assignment)
    save_data()
    refresh_list()

def sort_key(assignment):
    due = datetime.strptime(assignment["due_date"], DATE_FORMAT)
    
    return (due, -assignment["difficulty"])

def sort_assignments(items):
    items.sort(key=sort_key)

root = tk.Tk()
root.title("Homework Planner")
root.geometry("680x460")
root.minsize(560, 380)

title = tk.Label(root, text="Homework Planner", font=("Helvetica", 16, "bold"))
title.pack(pady=10)

form = ttk.LabelFrame(root, text="New assignment", padding=10)
form.pack(fill="x", padx=12)

ttk.Label(form, text="Name").grid(row=0, column=0, sticky="w")
name_entry = ttk.Entry(form, width=30)
name_entry.grid(row=1, column=0, padx=(0, 10), sticky="ew")

ttk.Label(form, text="Due date").grid(row=0, column=1, sticky="w")
due_entry = ttk.Entry(form, width=16)
due_entry.grid(row=1, column=1, padx=(0, 10))

ttk.Label(form, text="Difficulty").grid(row=0, column=2, sticky="w")
difficulty_entry = ttk.Entry(form, width=6)
difficulty_entry.grid(row=1, column=2, padx=(0, 10))

add_button = ttk.Button(form, text="Add", command=add_assignment)
add_button.grid(row=1, column=3)

form.columnconfigure(0, weight=1)
name_entry.bind("<Return>", lambda event: add_assignment())

list_frame = ttk.Frame(root, padding=(12, 10))
list_frame.pack(fill="both", expand=True)

columns = ("status", "name", "due_date", "difficulty")
tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
tree.heading("status", text="Status")
tree.heading("name", text="Assignment")
tree.heading("due_date", text="Due date")
tree.heading("difficulty", text="Difficulty")
tree.column("status", width=80, anchor="center")
tree.column("name", width=300)
tree.column("due_date", width=120, anchor="center")
tree.column("difficulty", width=90, anchor="center")

scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
tree.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

tree.tag_configure("done", foreground="gray")

actions = ttk.Frame(root, padding=(12, 0, 12, 12))
actions.pack(fill="x")
ttk.Button(actions, text="Toggle Complete", command=toggle_complete).pack(side="left")
ttk.Button(actions, text="Delete", command=delete_selected).pack(side="left", padx=8)

assignments = load_data()
refresh_list()

root.mainloop()