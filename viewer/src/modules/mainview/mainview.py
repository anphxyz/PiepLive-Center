import tkinter as tk
from tkinter import ttk, messagebox
from src.utils import helper, store
from src.modules.mediatab import MediaGridView
from src.models import Q170_model, L500_model
from src.enums import Q180
from src.constants import WS
from src.modules.custom import LabeledCombobox
from src.modules.menu import MainMenu
from src.modules.login import Login
from src.enums import MediaType
from src.modules.schedule import Schedule
import PIL
from PIL import Image, ImageTk


class MainView(tk.Frame):
    superWrapper = None
    mediaListTab = None
    tab_image = None
    tab_video = None
    tab_camera = None
    tab_presenter = None

    def __init__(self, parent, *args, **kwargs):
        super(MainView, self).__init__(parent, *args, **kwargs)
        self.parent = parent
        self.after(100, self.initGUI)
    #
    def setStyle(self):
        style = ttk.Style()
        style.theme_create("TabStyle", parent="alt", settings={
            "scroll.TFrame":{"background":"#fff"},
            "TNotebook": {
                "configure": {"tabmargins": [5, 0, 0, 5]}  # L T R B
            },
            "TNotebook.Tab": {
                "configure": {"padding": [15, 5, 15, 5]}
            }
        })
        style.theme_use("TabStyle")
    #
    def initGUI(self):
        # if not login
        if not bool(store._get('FO100')):
            self.login = Login(self)
            self.login.open()
        #
        self.setStyle()
        self.updateMenu()
        self.showToolbar()
        self.showBigTabWrapper()

    def showBigTabWrapper(self):
        self.superWrapper = ttk.Notebook(self)
        self.superWrapper.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        #
        icSchedule = tk.PhotoImage(file=helper._ICONS_PATH + 'ic_clock_tab.png')
        self.schedule = Schedule(self)
        self.schedule.image = icSchedule
        self.superWrapper.add(self.schedule, text="Schedule", image=icSchedule, compound=tk.LEFT)
        #
        icMedia = tk.PhotoImage(file=helper._ICONS_PATH + 'ic_media_tab.png')
        self.mediaList = self.makeMediaListTab()
        self.mediaList.image = icMedia
        self.superWrapper.add(self.mediaList, text="Live View", image=icMedia, compound=tk.LEFT)
         #
        self.superWrapper.select(self.schedule)
        self.superWrapper.enable_traversal()

    #
    def makeMediaListTab(self):
        # 0
        mediaListTab = ttk.Notebook(self)
        mediaListTab.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        # 1
        icImg = tk.PhotoImage(file=helper._ICONS_PATH + 'ic_image.png')
        self.tab_image = self.makeMediaTab(MediaType.IMAGE)
        self.tab_image.image = icImg
        mediaListTab.add(self.tab_image, text="Images", image=icImg, compound=tk.LEFT)
        # 2
        icVid = tk.PhotoImage(file=helper._ICONS_PATH + 'ic_video.png')
        self.tab_video = self.makeMediaTab(MediaType.VIDEO)
        self.tab_video.image = icVid
        mediaListTab.add(self.tab_video, text="Videos", image=icVid, compound=tk.LEFT)
        # 3
        icCam = tk.PhotoImage(file=helper._ICONS_PATH + 'ic_camera.png')
        self.tab_camera = self.makeMediaTab(MediaType.CAMERA)
        self.tab_camera.image = icCam
        mediaListTab.add(self.tab_camera, text="Cameras", image=icCam, compound=tk.LEFT)
        # 4
        icPres = tk.PhotoImage(file=helper._ICONS_PATH + 'ic_presenter.png')
        self.tab_presenter = self.makeMediaTab(MediaType.PRESENTER)
        self.tab_presenter.image = icPres
        mediaListTab.add(self.tab_presenter, text="Presenters", image=icPres, compound=tk.LEFT)
        #
        mediaListTab.select(self.tab_image)
        mediaListTab.enable_traversal()
        #
        return mediaListTab
    #
    def updateMenu(self):
        self.menubar = MainMenu(self)
        self.parent.parent.config(menu=self.menubar)
    #
    def makeMediaTab(self, tType):
        return MediaGridView(self, tabType=tType, borderwidth=0, bg="#fff")
    #
    def hideToolbar(self):
        self.toolbar.pack_forget()
        self.updateMenu()
    #
    def showToolbar(self):
        self.toolbar = tk.Frame(self, relief=tk.FLAT, bg='#fff')
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        #
        if bool(store._get('FO100')):
            self.packRightToolbar()

    def packRightToolbar(self):
        rightToolbar = tk.Frame(self.toolbar, relief=tk.FLAT, bg='#fff')
        rightToolbar.pack(side=tk.RIGHT, fill=tk.Y)
        #
        imgCheck = ImageTk.PhotoImage(Image.open(helper._ICONS_PATH+'close-pink.png'))
        lblCommandClear = tk.Label(rightToolbar, bd=1, image=imgCheck, bg="#fff")
        lblCommandClear.photo = imgCheck
        lblCommandClear.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 20), pady=5)
        lblCommandClear.bind('<Button-1>', self.onClearResource)
        #
        imgCheck = ImageTk.PhotoImage(Image.open(helper._ICONS_PATH+'check-green.png'))
        lblCommandCheck = tk.Label(rightToolbar, bd=1, image=imgCheck, bg="#fff")
        lblCommandCheck.photo = imgCheck
        lblCommandCheck.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0), pady=5)
        lblCommandCheck.bind('<Button-1>', self.onNewResource)
        #
        cbxData = {q170['NV106']: q170['FO100'] for q170 in self.loadCbxQ170()}
        cbxQ170 = LabeledCombobox(rightToolbar, cbxData, callback=self.onSelectBussiness, selected=store.getCurrentActiveBusiness(), bd=1, relief=tk.FLAT)
        cbxQ170.pack(side=tk.RIGHT, padx=10, pady=10)
        #
        self.updateMenu()
    #
    def onSelectBussiness(self, fo100):
        self.FO100BU = fo100
    #
    def onClearResource(self, evt):
        if messagebox.askyesno("PiepMe", "Are you sure to clear your bussiness resource?"):
            self.tab_camera.clearData()
            self.tab_presenter.clearData()
    #
    def onNewResource(self, evt):
        if messagebox.askyesno("PiepMe", "Are you sure to renew your bussiness resource?"):
            store.setCurrentActiveBusiness(self.FO100BU)
            lsL500 = self.loadLsL500(self.FO100BU)
            if len(lsL500) > 0:
                #presenter
                presenter = list(filter(lambda l500: l500['LN508'] == 1, lsL500))
                self.tab_presenter.renewData(presenter)
                self.schedule.right.tab_presenter.f5(None)
                #camera
                camera = list(filter(lambda l500: l500['LN508'] == 0, lsL500))
                self.tab_camera.renewData(camera)
                self.schedule.right.tab_camera.f5(None)
    #
    def loadCbxQ170(self):
        q170 = Q170_model()
        rs = q170.getListProviderWithRole({
            'FO100': store._get('FO100') or 0,
            'FQ180': Q180.CHA_LIV_CEN
        })
        return rs[WS.ELEMENTS] if rs[WS.STATUS] == WS.SUCCESS else []
        
    #
    def loadLsL500(self, fo100):
        l500 = L500_model()
        rs = l500.l2019_listoftabL500_prov({
            'FO100': fo100,  # ID của DN
            'FO100M': 0,  # ID của member (BTV)
            'PL500': 0,  # ID Link
            'SORT': 1,  # 1: Cũ nhất, -1: Mới nhất
            'OFFSET': 0,
            'LIMIT': 200,
            'LOGIN': 'PiepLive Center'
        })
        return rs[WS.ELEMENTS] if rs[WS.STATUS] == WS.SUCCESS else []
