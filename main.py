from cProfile import label
from tkinter import filedialog

import numpy as np
import tkinter as tk

class ImageEditor:
    def __init__(self):
        self.root = root
        self.root.title("Image Editor")
        self.root.minsize(600, 400)

        frame1 = tk.Frame(self.root)
        frame2 = tk.Frame(self.root)
        self.root.grid_rowconfigure(0, weight=1)  # Single row
        self.root.grid_columnconfigure(0, weight=1, uniform="frame")  # Frame 1 takes 1/4 of the horizontal space
        self.root.grid_columnconfigure(1, weight=3, uniform="frame")  # Frame 2 takes 3/4 of the horizontal space


        # Frame 1
        button1 = tk.Button(frame1, text="Adjust Size")
        button2 = tk.Button(frame1, text="Brightness")
        button3 = tk.Button(frame1, text="Solarize")
        button4 = tk.Button(frame1, text="Convert to Negative")
        button5 = tk.Button(frame1, text="Highlight Edges")

        button1.pack(fill='x', side='bottom')
        button2.pack(fill='x', side='bottom')
        button3.pack(fill='x', side='bottom')
        button4.pack(fill='x', side='bottom')
        button5.pack(fill='x', side='bottom')

        # entry1 = tk.Entry(frame1)
        # label1 = tk.Label(frame1, text="Label1")


        # Frame 2 (larger)
        button6 = tk.Button(frame2, text="Open File", command=self.open_file)

        button6.pack(fill='x', side='top')


        # Grid init
        frame1.grid(row=0, column=0, sticky="nsew")
        frame2.grid(row=0, column=1, sticky="nsew")


    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image File", "*.png;*.jpg;*.pdf")])
        print(file_path)

# Main Window
root = tk.Tk() # instance of the main window
editor = ImageEditor()
root.mainloop()