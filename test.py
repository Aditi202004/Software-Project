import tkinter as tk

def on_trigger():
    # This function is called when the button is clicked.
    # It changes the button's text to "Abort".
    TRIGGER_BUTTON['text'] = "Abort"

# Create the main window
root = tk.Tk()
root.title("Change Button Text Example")

# Create a button
# Initially, the button could say something else, like "Start"
TRIGGER_BUTTON = tk.Button(root, text="Start", command=on_trigger)

# Place the button on the window
TRIGGER_BUTTON.pack(pady=20)

# Start the Tkinter event loop
root.mainloop()
