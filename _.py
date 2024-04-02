import tkinter as tk
from tkinter import ttk

# Create a Tkinter window
root = tk.Tk()

# Create a Panedwindow widget
progress = ttk.Panedwindow(root, orient=tk.HORIZONTAL)  # Set orient to HORIZONTAL for two panes, one left and one right

# Add widgets for the left pane
left_frame = ttk.Frame(progress, width=100, height=200, relief=tk.SUNKEN, style="Left.TFrame")
left_label = tk.Label(left_frame, text="Left Pane", background="lightgreen")  # Set background color for left pane
left_label.pack(expand=True, fill=tk.BOTH)
progress.add(left_frame)

# Add widgets for the right pane
right_frame = ttk.Frame(progress, width=100, height=200, relief=tk.SUNKEN, style="Right.TFrame")
right_label = tk.Label(right_frame, text="Right Pane", background="lightblue")  # Set background color for right pane
right_label.pack(expand=True, fill=tk.BOTH)
progress.add(right_frame)

# Style configuration for left and right frames
style = ttk.Style()
style.configure("Left.TFrame", background="lightblue")
style.configure("Right.TFrame", background="lightgreen")

# Pack the Panedwindow widget
progress.pack(fill=tk.BOTH, expand=True)

# Run the Tkinter event loop
root.mainloop()
