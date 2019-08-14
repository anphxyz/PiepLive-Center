import tkinter as tk
from tkinter import ttk, messagebox
from .scheduleddlist import ScheduleDDList
from src.modules.custom import DDList
from src.utils import helper, scryto
from src.modules.custom import ToolTip
from PIL import Image, ImageTk
from src.modules.mediaitem import ScheduleHeadItem, ScheduleHeadItemEdit
from datetime import datetime, timedelta


class SortedList(ScheduleDDList):
    def __init__(self, parent, *args, **kwargs):
        super(SortedList, self).__init__(parent, *args, **kwargs)
        self.parent = parent
        self.wrapperWidth = 300
        self.tbBgColor = "#E8DAEF"
        self.titleTxt = "Schedule List"
        self.initUI()

    def initUI(self):
        super(SortedList, self).initUI()
        self.showListSchedule()

    def showListSchedule(self):
        # 1. default
        self.addToScheduleGUI(
            {"path": "", "id": "STORE_SCHEDULE", "name": "RUNNING SCHEDULE"}
        )
        # 2. list
        self._LS_SCHEDULE_DATA = self.loadSchedule()
        for media in self._LS_SCHEDULE_DATA:
            self.addToScheduleGUI(media)

    def packRightToolbar(self):
        super(SortedList, self).packRightToolbar()
        # add
        self.showAddCamBtn()
        self.showDupplicateBtn()

    def addToScheduleGUI(self, data):
        item = self.ddlist.create_item(value=data, freeze=data['id'] == 'STORE_SCHEDULE')
        ui = ScheduleHeadItem(item, parentTab=self, media=data)
        self._LS_SCHEDULE_UI.append(ui)
        ui.pack(expand=True)
        self.ddlist.add_item(item)

    def showDupplicateBtn(self):
        imAdd = ImageTk.PhotoImage(Image.open(f"{helper._ICONS_PATH}duplicate-24.png"))
        self.cmdAdd = tk.Label(
            self.tbright, image=imAdd, cursor="hand2", bg=self.tbBgColor
        )
        self.cmdAdd.image = imAdd
        self.cmdAdd.bind("<Button-1>", self.duplicateSchedule)
        self.cmdAdd.pack(side=tk.RIGHT, padx=5, pady=5)
        ToolTip(self.cmdAdd, "Duplicate schedule")

    def showAddCamBtn(self):
        imAdd = ImageTk.PhotoImage(Image.open(f"{helper._ICONS_PATH}add-rgb24.png"))
        self.cmdAdd = tk.Label(
            self.tbright, image=imAdd, cursor="hand2", bg=self.tbBgColor
        )
        self.cmdAdd.image = imAdd
        self.cmdAdd.bind("<Button-1>", self.createSchedule)
        self.cmdAdd.pack(side=tk.LEFT, padx=5, pady=5)
        ToolTip(self.cmdAdd, "Create schedule")

    def createSchedule(self, evt):
        editableFiltered = list(
            filter(
                lambda ui: isinstance(ui, ScheduleHeadItemEdit), self._LS_SCHEDULE_UI
            )
        )
        if 0 == len(editableFiltered):  # no one element edit able
            item = self.ddlist.create_item(value={})
            ui = ScheduleHeadItemEdit(item, parentTab=self)
            self._LS_SCHEDULE_UI.append(ui)
            ui.pack(expand=True)
            self.ddlist.add_item(item)

    def duplicateSchedule(self, evt):
        filtered = list(
            filter(lambda x: x.checked.get() and bool(x.path), self._LS_SCHEDULE_UI)
        )
        if len(filtered) > 0:
            if messagebox.askyesno(
                "PiepMe", "Are you sure duplicate all selected schedule?"
            ):
                for sch in filtered:
                    schDate = self.findLastDateInSchedule()
                    toPath = datetime.strftime(schDate, "%d%m%Y")
                    # 1. file
                    copied = helper.duplicate_schedule_container(sch.path, toPath)
                    # 2. sorted
                    self.addSchedule(
                        {
                            "path": copied,
                            "id": scryto.hash_md5_with_time(copied),
                            "name": sch.name + " (copy)",
                        }
                    )
                self.f5(evt)

    def loadScheduleDE(self, sch):
        self.clearScheduleActived()
        self.parent.schedule.setData(sch)
        self.parent.schedule.showListSchedule()

    def clearScheduleActived(self):
        for sch in self._LS_SCHEDULE_UI:
            if sch.actived:
                sch.changeBgFollowActivation()

    def rmvSchedule(self, lsId):
        ls = self.loadSchedule()
        # saved rest
        restFiltered = list(filter(lambda x: x["id"] not in lsId, ls))
        self.clearData()
        self.writeSchedule(restFiltered)
        # rmv all file not belong in sorted list
        rmvFitered = list(filter(lambda x: x["id"] in lsId, ls))
        for sch in rmvFitered:
            helper.delete_schedule_container(sch["path"])

    def saveSchedule(self, sch):
        ls = self.loadSchedule()
        # check edit
        filtered = list(filter(lambda x: x["id"] == sch["id"], ls))
        if len(filtered) > 0:
            self.saveEdit(ls, sch)
        elif helper.new_schedule_container(sch["path"]):  # create
            self.addToScheduleGUI(sch)
            self.addSchedule(sch)
        else:
            pass  # alert somethings when create failed: dupplicate name..
        #
        self.f5(None)

    def saveEdit(self, ls, sch):
        newLs = list(map(lambda x: sch if x["id"] == sch["id"] else x, ls))
        self.clearData()
        self.writeSchedule(newLs)

    def findLastDateInSchedule(self):
        if not bool(self._LS_SCHEDULE_DATA):
            return datetime.today()
        else:
            fmt = "%d%m%Y"
            flag = datetime.strptime(self._LS_SCHEDULE_DATA[0]["path"], fmt)
            for sch in self._LS_SCHEDULE_DATA:
                cr = datetime.strptime(sch["path"], fmt)
                if cr > flag:
                    flag = cr
            #
            return flag + timedelta(days=1)

    def generateNameFromDate(self, date):
        # Return the day of the week as an integer, where Monday is 0 and Sunday is 6.
        wDay = date.weekday()
        weekDay = [
            "Thứ Hai",
            "Thứ Ba",
            "Thứ Tư",
            "Thứ Năm",
            "Thứ Sáu",
            "Thứ Bảy",
            "Chủ Nhật",
        ]
        return weekDay[wDay] + " - " + datetime.strftime(date, "%d/%m/%Y")

    def loadSchedule(self):
        return helper._load_sorted_schedule()

    def addSchedule(self, data):
        helper._add_to_sorted_schedule(data)

    def writeSchedule(self, data):
        helper._write_sorted_schedule(data)