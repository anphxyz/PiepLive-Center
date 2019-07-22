import tkinter as tk
from tkinter import ttk
from src.utils import tk_helper, helper, scryto
from src.constants import UI
import re

class PopupAddSchedule(object):

    def __init__(self, parent, data):
        self.popup = None
        self.popupRuntime = None
        self.parent = parent
        self.media = data
    
    def setupData(self, edit=False):
        self.url = self.media['url'] if 'url' in self.media else ''
        self.id = self.media['id'] if edit else scryto.hash_md5_with_time(self.url)
        self.eName = self.media['name'] if 'name' in self.media else ''
        self.mtype = self.media['type'] if 'type' in self.media else ''
        self.duration = int(self.media['duration']) if 'duration' in self.media else 0
        self.timepoint = int(self.media['timepoint']) if 'timepoint' in self.media else 0
        self.audio = self.media['audio'] if 'audio' in self.media else ''
        #

    def initGUI(self, edit=False):
        # first destroy
        if bool(self.popup):
            self.popup.destroy()
        self.popup = tk_helper.makePiepMePopup('Add to Schedule', w=400, h=200, padx=0, pady=0)
        # var
        self.setupData(edit=edit)
        self.name = tk.StringVar()
        self.name.set(self.eName)
        h,m,s = helper.convertSecNoToHMS(self.duration, toObj=True).values()
        #
        wrapper = tk.Frame(self.popup)
        wrapper.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        #1. Name
        fName = tk.Frame(wrapper, pady=10, padx=20)
        lName = tk.Label(fName, text="Name:", width=6, anchor=tk.W, font=UI.TXT_FONT)
        lName.pack(side=tk.LEFT, fill=tk.Y)
        name = tk.Entry(fName, textvariable=self.name, width=100, borderwidth=5, relief=tk.FLAT)
        name.bind("<FocusIn>", lambda args: name.select_range('0', tk.END))
        name.pack(side=tk.LEFT, fill=tk.X, padx=(10, 0))
        fName.pack(side=tk.TOP, fill=tk.X)
        #2. Duration
        fDura = tk.Frame(wrapper, pady=10, padx=20)
        fDura.pack(side=tk.TOP, fill=tk.X)
        #
        lDura = tk.Label(fDura, text="Duration:", width=7, anchor=tk.W, font=UI.TXT_FONT)
        lDura.pack(side=tk.LEFT, fill=tk.Y)
        ##
        self.hh = ttk.Combobox(fDura, values=[ x for x in range(0,100) ], width=4)
        self.hh.pack(side=tk.LEFT, fill=tk.X, padx=5)
        self.hh.current(h)
        ##
        separator = tk.Label(fDura, text=":", width=1, anchor=tk.W, font=UI.TXT_FONT)
        separator.pack(side=tk.LEFT, padx=5)
        ##
        self.mm = ttk.Combobox(fDura, values=[ x for x in range(0,60) ], width=4)
        self.mm.pack(side=tk.LEFT, fill=tk.X, padx=5)
        self.mm.current(m)
        ##
        separator = tk.Label(fDura, text=":", width=1, anchor=tk.W, font=UI.TXT_FONT)
        separator.pack(side=tk.LEFT, padx=5)
        ##
        self.ss = ttk.Combobox(fDura, values=[ x for x in range(0,60) ], width=4)
        self.ss.pack(side=tk.LEFT, fill=tk.X, padx=5)
        self.ss.current(s)
        #4. Button
        fBtn = tk.Frame(wrapper, pady=10, padx=20)
        btnCancel = tk.Button(fBtn, text="Cancel", bd=2, relief=tk.RAISED, command=self.popup.destroy)
        btnCancel.configure(width=7)
        btnCancel.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        btnOk = tk.Button(fBtn, text="OK", bd=2, bg="#ff2d55", fg="#fff", relief=tk.RAISED, command=self.onSave)
        btnOk.configure(width=7)
        btnOk.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        fBtn.pack(side=tk.BOTTOM, fill=tk.X)

    def showChangeRuntimeUI(self):
        # first destroy
        if bool(self.popupRuntime):
            self.popupRuntime.destroy()
        self.popupRuntime = tk_helper.makePiepMePopup('Change runtime', w=300, h=120, padx=0, pady=0)
        # var
        self.setupData(edit=True)
        H,M,S = helper.convertSecNoToHMS(self.timepoint, toObj=True).values()
        wrapper = tk.Frame(self.popupRuntime)
        wrapper.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        # #0. timepoint
        fTime = tk.Frame(wrapper, pady=20, padx=20)
        fTime.pack(side=tk.TOP, fill=tk.X)
        #
        lTime = tk.Label(fTime, text="Runtime:", width=7, anchor=tk.W, font=UI.TXT_FONT)
        lTime.pack(side=tk.LEFT, fill=tk.Y)
        ##
        self.HH = ttk.Combobox(fTime, values=[ x for x in range(0,100) ], width=4)
        self.HH.pack(side=tk.LEFT, fill=tk.X, padx=5)
        self.HH.current(H)
        ##
        separator = tk.Label(fTime, text=":", width=1, anchor=tk.W, font=UI.TXT_FONT)
        separator.pack(side=tk.LEFT, padx=5)
        ##
        self.MM = ttk.Combobox(fTime, values=[ x for x in range(0,60) ], width=4)
        self.MM.pack(side=tk.LEFT, fill=tk.X, padx=5)
        self.MM.current(M)
        ##
        separator = tk.Label(fTime, text=":", width=1, anchor=tk.W, font=UI.TXT_FONT)
        separator.pack(side=tk.LEFT, padx=5)
        ##
        self.SS = ttk.Combobox(fTime, values=[ x for x in range(0,60) ], width=4)
        self.SS.pack(side=tk.LEFT, fill=tk.X, padx=5)
        self.SS.current(S)
         #1. Button
        fBtn = tk.Frame(wrapper, pady=10, padx=20)
        btnCancel = tk.Button(fBtn, text="Cancel", bd=2, relief=tk.RAISED, command=self.popupRuntime.destroy)
        btnCancel.configure(width=7)
        btnCancel.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        btnOk = tk.Button(fBtn, text="OK", bd=2, bg="#ff2d55", fg="#fff", relief=tk.RAISED, command=self.onSaveRuntime)
        btnOk.configure(width=7)
        btnOk.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        fBtn.pack(side=tk.BOTTOM, fill=tk.X)

    def limithh(self, *arg):
       tk_helper.verifyHMS_val(self.hh)

    def limitmm(self, *arg):
       tk_helper.verifyHMS_val(self.mm)

    def limitss(self, *arg):
       tk_helper.verifyHMS_val(self.ss)

    def limitHH(self, *arg):
       tk_helper.verifyHMS_val(self.HH)

    def limitMM(self, *arg):
       tk_helper.verifyHMS_val(self.MM)

    def limitSS(self, *arg):
       tk_helper.verifyHMS_val(self.SS)

    def onSave(self):
        self.parent.saveToSchedule({
            'id':self.id,
            'name': self.name.get(), 
            'url': self.url, 
            'type': self.mtype,
            'duration': helper.convertHMSNoToSec({'h': self.hh.get(), 'm': self.mm.get(), 's': self.ss.get()}),
            'timepoint':self.timepoint,
            'audio':self.audio
        })
        self.popup.destroy()

    def onSaveRuntime(self):
        self.parent.calcRuntime({
            'id':self.id,
            'name': self.eName, 
            'url': self.url, 
            'type': self.mtype,
            'duration': self.duration,
            'timepoint': helper.convertHMSNoToSec({'h': self.HH.get(), 'm': self.MM.get(), 's': self.SS.get()}),
            'audio':self.audio
        })
        self.popupRuntime.destroy()
