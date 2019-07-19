import vlc
import tkinter as tk
from src.modules.custom import PLabel
import PIL
from PIL import Image, ImageTk
from src.utils import helper
from src.constants import UI
from .mediaitem import MediaItem
from src.enums import MediaType
from src.modules.custom import ToolTip, CanvasC

class MediaItemDnD(MediaItem):

    def __init__(self, parent, parentTab=None, media=None, *args, **kwargs):
        super(MediaItemDnD, self).__init__(parent, *args, **kwargs)
        self.parent = parent
        self.parentTab = parentTab
        self.set_data(media)
        self.initGUI()

    def initGUI(self):
        #
        wrapper = tk.Frame(self)
        wrapper.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # push to schedule
        imgPush = ImageTk.PhotoImage(Image.open(f"{helper._ICONS_PATH}push-left-b.png"))
        lblPush = tk.Label(wrapper, image=imgPush, cursor='hand2')
        lblPush.image = imgPush
        lblPush.bind("<Button-1>", self.callParentAddSchedule)
        lblPush.pack(side=tk.LEFT, padx=5, pady=5)
         # traffic lignt
        if self.parentTab.tabType == MediaType.PRESENTER:
            self.light = CanvasC(wrapper, width=15, height=15, borderwidth=0, highlightthickness=0)
            self.light.pack(side=tk.LEFT)
            self.light.create_circle(6, 6, 6, fill="#F00", width=0)
        #
        checkbox = tk.Checkbutton(wrapper, variable=self.checked, onvalue=True, offvalue=False, height=1, width=1, bd=0, relief=tk.FLAT)
        checkbox.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
        # label
        lbl_name = PLabel(wrapper, text=self.name, justify=tk.LEFT, elipsis=(35, 30)[self.parentTab.tabType == MediaType.VIDEO], font=UI.TXT_FONT, fg="#000", cursor='hand2')
        ToolTip(lbl_name, self.name)
        lbl_name.pack(side=tk.LEFT)
        # bin
        imageBin = ImageTk.PhotoImage(Image.open(f"{helper._ICONS_PATH}trash-b.png"))
        lbl_trash = tk.Label(wrapper, image=imageBin, cursor='hand2')
        lbl_trash.image = imageBin
        lbl_trash.bind("<Button-1>", self.deleteMedia)
        ToolTip(lbl_trash, "Delete")
        lbl_trash.pack(side=tk.RIGHT)
        self.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # edit
        imageBin = ImageTk.PhotoImage(Image.open(f"{helper._ICONS_PATH}pen-b.png"))
        lblPen = tk.Label(wrapper, image=imageBin, cursor='hand2')
        lblPen.image = imageBin
        lblPen.bind("<Button-1>", self.editMedia)
        ToolTip(lblPen, "Edit")
        lblPen.pack(side=tk.RIGHT)
        self.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        #duration
        if self.parentTab.tabType == MediaType.VIDEO:
            hms = helper.convertSecNoToHMS(self.duration)
            dura = PLabel(wrapper, text=hms, fg='#ff2d55', font=UI.TXT_FONT)
            dura.pack(side=tk.RIGHT, padx=10)
    
    def editMedia(self, evt):
        self.parentTab.showEditMedia(self.get_data())

    def deleteMedia(self, evt):
        super(MediaItemDnD, self).deleteMedia(evt)
        self.parentTab.tabRefresh(None)

    def callParentAddSchedule(self, evt):
        self.parentTab.callShowPopup(self.get_data())