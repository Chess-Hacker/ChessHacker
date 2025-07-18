import tkinter as tk
from tkinter import ttk
import sys
import threading
import requests

def on_close():
    print("Closing the app... Performing cleanup.")
    root.after(50, root.destroy)

def launch_client():
	selected_site = site_var.get()
	selected_engine = engine_var.get()
	
	import master
	master_thread = threading.Thread(target=master.main, daemon=True)
	master_thread.start()

root = tk.Tk()
root.protocol("WM_DELETE_WINDOW", on_close)
root.title("Chess Hacker Launcher")
root.geometry("510x470")
root.resizable(False, False)
root.config(bg="#f7f7f7")
root.iconbitmap("Media/icon.ico")

frame = tk.Frame(root, bg="#f7f7f7", padx=30, pady=30)
frame.pack(fill="both", expand=True, padx=20, pady=20)

title_label = tk.Label(frame, text="Chess Hacker Launcher", font=("Helvetica", 24, "bold"), bg="#f7f7f7", anchor="w")
title_label.grid(row=0, column=0, columnspan=2, pady=10, sticky="w")

# Site selection
site_var = tk.StringVar(value="chess.com")
site_label = tk.Label(frame, text="Select Chess Website:", font=("Helvetica", 14), bg="#f7f7f7")
site_label.grid(row=1, column=0, sticky="w", pady=5)

site_options = ["chess.com"]#",lichess.org", "playchess.com"
site_menu = ttk.Combobox(frame, textvariable=site_var, values=site_options, state="readonly", font=("Helvetica", 12), width=20)
site_menu.grid(row=1, column=1, pady=10)

# Engine selection
engine_var = tk.StringVar(value="Stockfish")
engine_label = tk.Label(frame, text="Select Engine:", font=("Helvetica", 14), bg="#f7f7f7")
engine_label.grid(row=2, column=0, sticky="w", pady=5)

engine_options = ["Stockfish"]#, "Lc0", "Komodo"
engine_menu = ttk.Combobox(frame, textvariable=engine_var, values=engine_options, state="readonly", font=("Helvetica", 12), width=20)
engine_menu.grid(row=2, column=1, pady=10)

#Browser selection
browser_var = tk.StringVar(value="Chromium")
browser_label = tk.Label(frame, text="Select Browser:", font=("Helvetica", 14), bg="#f7f7f7")
browser_label.grid(row=3, column=0, sticky="w", pady=5)

browser_options = ["Chromium"]#, "Lc0", "Komodo"
browser_menu = ttk.Combobox(frame, textvariable=browser_var, values=browser_options, state="readonly", font=("Helvetica", 12), width=20)
browser_menu.grid(row=3, column=1, pady=10)

# Launch button
launch_button1 = tk.Button(frame, text="LAUNCH", font=("Helvetica", 14, "bold"), bg="black", fg="white", width=20, height=2, relief="flat", bd=0)
launch_button1.grid(row=5, column=0, columnspan=2, pady=20, padx=10)
launch_button1.config(command=launch_client)

# Footer
footer_label = tk.Label(root, text="Chess Hacker - Maxwell's Demons", font=("Helvetica", 10), fg="#888888", bg="#f7f7f7")
footer_label.pack(side="bottom", pady=10)

root.mainloop()
