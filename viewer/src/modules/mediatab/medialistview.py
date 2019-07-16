import tkinter as tk
from src.modules.custom import DDList
from . import MediaTab
from src.modules.mediaitem import MediaItemDnD
from PIL import ImageTk, Image
from src.utils import helper
from src.modules.custom import VerticalScrolledFrame, ToolTip
from src.enums import MediaType

class MediaListView(MediaTab):
    def __init__(self, parent, *args, **kwargs):
        self.tabType = kwargs['tabType']
        del kwargs['tabType']
        if 'schedule' in (kwargs):
            self.schedule = kwargs['schedule']
            del kwargs['schedule']
        super(MediaListView, self).__init__(parent, *args, **kwargs)
        self.tbBgColor = '#F9EBEA' if self.tabType == MediaType.SCHEDULE else '#D5DBDB'
        self.parent = parent
        self.scrollZ = VerticalScrolledFrame(self)
        self.ddlist = self.makeDDList(self.scrollZ.interior)
        self.initUI()

    def makeDDList(self, ref):
        return DDList(ref, 
            400,
            50,
            offset_x=5,
            offset_y=5,
            gap=5,
            item_borderwidth=1,
            item_relief=tk.FLAT,
            borderwidth=0,
            bg="#ccc")

    def initUI(self):
        super(MediaListView, self).initUI()
        self.showCmdSaveSortedMediaLst()
        if self.tabType == MediaType.IMAGE or self.tabType == MediaType.VIDEO:
            self.showAddCamBtn()
        #
        self.scrollZ.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.ddlist.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def addMediaToList(self, media):
        item = self.ddlist.create_item()
        ui = MediaItemDnD(item, parentTab=self, media=media)
        self._LS_MEDIA_UI.append(ui)
        ui.pack(padx= (4,0), pady= (4,0), expand=True)
        self.ddlist.add_item(item)

    def showCmdSaveSortedMediaLst(self):
        imageBin = ImageTk.PhotoImage(Image.open(f"{helper._ICONS_PATH}check-green.png"))
        self.cmdSaveSorted = tk.Label(self.toolbar, image=imageBin, cursor='hand2', bg=self.tbBgColor)
        self.cmdSaveSorted.image = imageBin
        self.cmdSaveSorted.bind("<Button-1>", self.saveSortedList)
        self.cmdSaveSorted.pack(side=tk.RIGHT, padx=(0, 15), pady=5)
        ToolTip(self.cmdSaveSorted, "Save sorted medias")

    def clearView(self):
        super(MediaListView, self).clearView()
        self.ddlist._clear_all()

    def saveSortedList(self, evt):
        print('saveSortedList=========')