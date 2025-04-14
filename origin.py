import tkinter as tk
from tkinter import ttk
import sys
import threading
import requests

token = None
Isdemo=True

def on_close():
    print("Closing the app... Performing cleanup.")
    global token,Isdemo
    if Isdemo==False:
        response = requests.get("https://chess-demo.mihneaspiridon.workers.dev/",headers={"Action": "Release","Token": f"{token}"})
        print(response.status_code)
    root.after(50, root.destroy)

def launch_client_Key():
	global Isdemo
	selected_site = site_var.get()
	selected_engine = engine_var.get()
	selected_resolution = resolution_var.get()
	user_input = text_input.get()
	global token
	token = user_input
	print(f"Launching {selected_site} with {selected_engine} engine!")
	print(f"User input:{user_input}")
	print(f"Selected resolution: {selected_resolution}")

	response = requests.get("https://chess-demo.mihneaspiridon.workers.dev/",
                        headers={
                            "Action": "Bind",
                            "Token": f"{token}"
                        })
	print(response.status_code)
	if response.status_code==200:
		Isdemo=False
		text_input.config(state="readonly")
		with open("token.txt", "w") as f:
			f.write(f"{token}\n")
		import master
		master_thread = threading.Thread(target=master.main, daemon=True)
		master_thread.start()

def launch_client_Demo():
	selected_site = site_var.get()
	selected_engine = engine_var.get()
	user_input = text_input.get()
	import master
	master_thread = threading.Thread(target=master.main, daemon=True)
	master_thread.start()

root = tk.Tk()
root.protocol("WM_DELETE_WINDOW", on_close)
root.title("Chess Hacker Launcher")
root.geometry("620x470")
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

# Text input area
text_label = tk.Label(frame, text="Enter key:", font=("Helvetica", 14), bg="#f7f7f7")
text_label.grid(row=4, column=0, sticky="w", pady=5)

text_input = tk.Entry(frame, font=("Helvetica", 12), width=22, bd=2, relief="solid")
text_input.grid(row=4, column=1, pady=10)

# Launch button
launch_button = tk.Button(frame, text="Launch", font=("Helvetica", 14, "bold"), bg="black", fg="white", width=20, height=2, relief="flat", bd=0)
launch_button.grid(row=5, column=0, columnspan=1, pady=20, padx=10)
launch_button.config(command=launch_client_Key)
launch_button1 = tk.Button(frame, text="Demo", font=("Helvetica", 14, "bold"), bg="black", fg="white", width=20, height=2, relief="flat", bd=0)
launch_button1.grid(row=5, column=1, columnspan=1, pady=20, padx=10)
launch_button1.config(command=launch_client_Demo)

# Footer
footer_label = tk.Label(root, text="Chess Hacker - Maxwell's Demons", font=("Helvetica", 10), fg="#888888", bg="#f7f7f7")
footer_label.pack(side="bottom", pady=10)

root.mainloop()
