import tkinter as tk
from src.utils import tk_helper

class PopupNewSchedule(object):

    def __init__(self, parent, data):
        self.parent = parent
        self.media = data
        self.popup = None

    def setupData(self):
        self.mtype = self.media['type']
        self.duration = int(self.media['duration']) if 'duration' in self.media else 0
        self.id = self.media['id']
        #
        name = self.media['name']
        url = self.media['url']
        self.name.set(name)
        self.url.set(url)

    def initGUI(self, data):
        # first destroy
        if None is not self.popup:
            self.popup.destroy()
        self.popup = tk_helper.makePiepMePopup('Edit Media', w=450, h=180, padx=0, pady=0)
        self.initTabFileUI()

    def initTabFileUI(self):
        fFile = tk.Frame(self.popup)
        # var
        self.name = tk.StringVar()
        self.url = tk.StringVar()
        self.setupData()
        # name
        fName = tk.Frame(fFile, pady=10, padx=20)
        lName = tk.Label(fName, text="Name:", width=6, anchor=tk.W, font=UI.TXT_FONT)
        lName.pack(side=tk.LEFT, fill=tk.Y)
        self.eName = tk.Entry(fName, textvariable=self.name, width=100, borderwidth=5, relief=tk.FLAT)
        self.eName.pack(side=tk.LEFT, fill=tk.X)
        fName.pack(side=tk.TOP, fill=tk.X)
        # URL
        fUrl = tk.Frame(fFile, pady=10, padx=20)
        lUrl = tk.Label(fUrl, text="URL:", width=6, anchor=tk.W, font=UI.TXT_FONT)
        lUrl.pack(side=tk.LEFT, fill=tk.Y)
        self.eUrl = tk.Entry(fUrl, textvariable=self.url, width=45, borderwidth=5, relief=tk.FLAT)
        self.eUrl.pack(side=tk.LEFT, fill=tk.X)
        btnChoose = tk.Button(fUrl, text="Choose..", relief=tk.RAISED, padx=5, pady=5, command=self.askFileName, font=UI.TXT_FONT)
        btnChoose.configure(width=7)
        btnChoose.pack(side=tk.RIGHT, fill=tk.Y)
        fUrl.pack(side=tk.TOP, fill=tk.X)
        # error msg
        self.fError = tk.Frame(fFile)
        lError = tk.Label(self.fError, text="File not allowed!", fg="#f00")
        lError.pack(side=tk.LEFT, fill=tk.Y)
        # bot button
        fBtn = tk.Frame(fFile, pady=10, padx=20)
        btnCancel = tk.Button(fBtn, text="Cancel", bd=2, relief=tk.RAISED, command=self.popup.destroy)
        btnCancel.configure(width=7)
        btnCancel.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        btnOk = tk.Button(fBtn, text="OK", bd=2, bg="#ff2d55", fg="#fff", relief=tk.RAISED, command=self.onSave)
        btnOk.configure(width=7)
        btnOk.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        fBtn.pack(side=tk.BOTTOM, fill=tk.X)
        fFile.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def onSave(self):
        self.parent.saveToMediaList({
            'id':self.id,
            'name': self.name.get(), 
            'url': self.url.get(), 
            'type': self.mtype,
            'duration': self.duration
        })
        self.popup.destroy()