import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage

# Function to launch the client
def launch_client():
    selected_site = site_var.get()
    selected_engine = engine_var.get()
    user_input = text_input.get()  # Get the text input from Entry widget
    width = width_slider.get()     # Get the selected width from the slider
    height = height_slider.get()   # Get the selected height from the slider
    print(f"Launching {selected_site} with {selected_engine} engine!")
    print(f"User input: {user_input}")  # Print user input
    print(f"Selected resolution: {width}x{height}")  # Print selected resolution

# Create the main window
root = tk.Tk()
root.title("Chess Hacker Launcher")
root.geometry("550x580")  # Default resolution
root.config(bg="#f7f7f7")  # Set a background color close to Hugo Papermod style
root.iconbitmap("Media/icon.ico")

# Load the icon image (ensure you have the 'icon.png' image in the same directory)
icon = PhotoImage(file="Media/icon.png")

# Resize the icon to a fixed size (e.g., 40x40 pixels)
icon = icon.subsample(20, 20)  # Adjust values to scale to the size you want

# Create a frame for the form
frame = tk.Frame(root, bg="#f7f7f7", padx=30, pady=30)
frame.pack(fill="both", expand=True, padx=20, pady=20)

# Title label with icon
title_label = tk.Label(frame, text="Chess Hacker", font=("Helvetica", 24, "bold"), bg="#f7f7f7", anchor="w")
title_label.grid(row=0, column=1, columnspan=2, pady=10, sticky="w")

# Add the icon next to the title with padding
icon_label = tk.Label(frame, image=icon, bg="#f7f7f7")
icon_label.grid(row=0, column=0, sticky="w", padx=(10, 10))  # Added horizontal padding to prevent overlap

# Site selection
site_var = tk.StringVar(value="chess.com")  # Default site
site_label = tk.Label(frame, text="Select Chess Website:", font=("Helvetica", 14), bg="#f7f7f7")
site_label.grid(row=1, column=0, sticky="w", pady=5)

site_options = ["chess.com", "lichess.org", "playchess.com"]
site_menu = ttk.Combobox(frame, textvariable=site_var, values=site_options, state="readonly", font=("Helvetica", 12), width=20)
site_menu.grid(row=1, column=1, pady=10)

# Engine selection
engine_var = tk.StringVar(value="Stockfish")  # Default engine
engine_label = tk.Label(frame, text="Select Engine:", font=("Helvetica", 14), bg="#f7f7f7")
engine_label.grid(row=2, column=0, sticky="w", pady=5)

engine_options = ["Stockfish", "Lc0", "Komodo"]
engine_menu = ttk.Combobox(frame, textvariable=engine_var, values=engine_options, state="readonly", font=("Helvetica", 12), width=20)
engine_menu.grid(row=2, column=1, pady=10)

# Text input area (One line, maximum 16 characters)
text_label = tk.Label(frame, text="Enter key:", font=("Helvetica", 14), bg="#f7f7f7")
text_label.grid(row=3, column=0, sticky="w", pady=5)

# Create Entry widget with limit of 16 characters
text_input = tk.Entry(frame, font=("Helvetica", 12), width=22, bd=2, relief="solid")
text_input.grid(row=3, column=1, pady=10)

# Resolution Slider for width and height
resolution_label = tk.Label(frame, text="Window Resolution:", font=("Helvetica", 14), bg="#f7f7f7")
resolution_label.grid(row=4, column=0, columnspan=2, pady=10)

# Width slider (500 to 1000 pixels)
width_slider = tk.Scale(frame, from_=854, to=3840, orient="horizontal", font=("Helvetica", 12), length=250)
width_slider.set(1920)  # Default width
width_slider.grid(row=5, column=0, columnspan=2, pady=5)

# Height slider (500 to 800 pixels)
height_slider = tk.Scale(frame, from_=480, to=2160, orient="horizontal", font=("Helvetica", 12), length=250)
height_slider.set(950)  # Default height
height_slider.grid(row=6, column=0, columnspan=2, pady=5)

# Launch Button with black background and white text
launch_button = tk.Button(frame, text="Launch", font=("Helvetica", 14, "bold"), bg="black", fg="white", width=20, height=2, relief="flat", bd=0)
launch_button.grid(row=7, column=0, columnspan=2, pady=20)

# Update button design with rounded corners
launch_button.config(highlightthickness=0, relief="flat", padx=10, pady=10)

# Add a footer
footer_label = tk.Label(root, text="Chess Hacker - Maxwell's Demons", font=("Helvetica", 10), fg="#888888", bg="#f7f7f7")
footer_label.pack(side="bottom", pady=10)

# Launch button action
launch_button.config(command=launch_client)

# Run the Tkinter main loop
root.mainloop()
