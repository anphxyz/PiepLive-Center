import tkinter as tk
from .sortedlist import SortedList


class MultiScheduleLeft(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super(MultiScheduleLeft, self).__init__(parent, *args, **kwargs)
        self.schedule = None

    def initUI(self):
        self.schedule = SortedList(self, bg="#f00")
        self.schedule.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    