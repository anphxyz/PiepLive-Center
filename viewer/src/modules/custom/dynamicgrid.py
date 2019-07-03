import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import random


class DynamicGrid(tk.Frame):
    def __init__(self, parent, *args, **kwargs):

        super(DynamicGrid, self).__init__(parent, *args, **kwargs)
        #
        self.boxes = []
        #
        self.context = ScrolledText(self, wrap="char", bd=3, relief=tk.FLAT, highlightthickness=0, bg='#f2f2f2', state=tk.DISABLED)
        self.context.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def getContext(self):
        return self.context

    def after_effect(self, box):
        self.boxes.append(box)
        self.context.configure(state=tk.NORMAL)
        self.context.window_create(tk.END, window=box)
        self.context.configure(state=tk.DISABLED)
