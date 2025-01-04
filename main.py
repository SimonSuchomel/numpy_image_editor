import numpy as np
import tkinter as tk

class ImageEditor:
    def __init__(self):
        self.root = root
        self.root.title("Image Editor")

        self.canvas = tk.Canvas(root, width=400, height=600)
        self.canvas.pack()

        button = tk.Button(root, text="Test")
        button.pack()

# Main Window
root = tk.Tk() # instance of the main window
editor = ImageEditor()
root.mainloop()