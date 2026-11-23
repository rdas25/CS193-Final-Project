import tkinter as tk

root = tk.Tk()
root.title("Homework Planner")
root.geometry("680x460")
root.minsize(560, 380)

title = tk.Label(root, text="Homework Planner", font=("Helvetica", 16, "bold"))
title.pack(pady=10)

root.mainloop()