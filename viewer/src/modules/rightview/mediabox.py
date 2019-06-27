import vlc
import tkinter as tk
from tkinter import ttk, messagebox
from src.modules.custom import PLabel
from PIL import Image, ImageTk
from src.utils import helper


class MediaBox(tk.Frame):
    finished = False
    cell_width = 240
    cell_height = 135

    def __init__(self, parent, camera=None, *args, **kwargs):
        super(MediaBox, self).__init__(parent, *args, **kwargs)
        self.parent = parent
        self.set_data(camera)
        self.after(100, self.initGUI)

    def get_data(self):
        return {'name': self.name, 'url': self.url, 'type': self.mtype}

    def set_data(self, camera):
        self.name = camera['name']
        self.url = camera['url']
        self.mtype = camera['type']

    def initGUI(self):
        self.initTOP()
        self.initBOTTOM()
        if self.mtype == 'VIDEO':
            self.buffer = tk.Frame(
                self, bd=1, relief=tk.FLAT, borderwidth=1, bg='#f00', width=0, height=3)
            self.buffer.pack(side=tk.LEFT, fill=tk.Y)

    def initTOP(self):
        top = tk.Frame(self, bd=1, relief=tk.FLAT, bg="#ccc",
                       borderwidth=0, width=self.cell_width, height=self.cell_height)
        top.bind("<Button-1>", self.playOrPauseClick)
        # vlc
        self.Instance = vlc.Instance()
        self.player = self.Instance.media_player_new()
        self.player.audio_set_volume(0)
        self.initPlayerMedia()
        self.player.set_hwnd(top.winfo_id())
        self.play()
        #
        if self.mtype == 'VIDEO':
            self.after(100, self.playOrPause)

        top.pack(side=tk.TOP, expand=True)

    def initPlayerMedia(self):
        self.media = self.Instance.media_new(self.url)
        self.player.set_media(self.media)
        self.media.release()

    def updateProgress(self):
        events = self.player.event_manager()
        events.event_attach(
            vlc.EventType.MediaPlayerEndReached, self.on_end)
        nwidth = self.player.get_time() / self.media.get_duration() * self.cell_width
        self.buffer.config(width=nwidth)
        if self.finished:
            self.buffer.configure(width=self.cell_width)
        elif self.player.is_playing():
            self.after(1000, self.updateProgress)

    def on_end(self, evt):
        self.finished = True
        self.updatePlayIcon('f5')

    def initBOTTOM(self):
        bottom = tk.Frame(self, bd=1, relief=tk.FLAT, borderwidth=0,
                          width=self.cell_width, height=25)
        if self.mtype != 'IMG':
            # play
            imagePlay = ImageTk.PhotoImage(Image.open("src/icons/pause-b.png"))
            self.lblPlay = tk.Label(bottom, image=imagePlay, cursor='hand2')
            self.lblPlay.image = imagePlay
            self.lblPlay.bind("<Button-1>", self.playOrPauseClick)
            self.lblPlay.pack(side=tk.LEFT)
        # label
        lbl_name = PLabel(bottom, text=self.name, justify=tk.LEFT, elipsis=25, font=(
            "Roboto", 10), fg="#000")
        lbl_name.pack(side=tk.LEFT)
        # bin
        imageBin = ImageTk.PhotoImage(Image.open("src/icons/trash-b.png"))
        lbl_trash = tk.Label(bottom, image=imageBin, cursor='hand2')
        lbl_trash.image = imageBin
        lbl_trash.bind("<Button-1>", self.deleteCamera)
        lbl_trash.pack(side=tk.RIGHT)
        bottom.pack(side=tk.BOTTOM, fill=tk.X)

    def play(self):
        if self.mtype == 'VIDEO':
            if self.finished:
                self.buffer.configure(width=0)
                self.player.stop()
                self.finished = False
            #
            self.after(1000,  self.updateProgress)
        self.player.play()

    def playOrPauseClick(self, _):
        self.playOrPause()

    def playOrPause(self):
        # z
        if self.player.is_playing():
            self.player.pause()
            self.updatePlayIcon('play')
        else:
            self.play()
            self.updatePlayIcon('pause')

    def updatePlayIcon(self, ico):
        # icon change
        image = Image.open(f"src/icons/{ico}-b.png")
        imagetk = ImageTk.PhotoImage(image)
        self.lblPlay.configure(image=imagetk)
        self.lblPlay.image = imagetk

    def deleteCamera(self, evt):
        if messagebox.askyesno("PiepMe", "Are you sure to delete this resource?"):
            pass
        else:
            pass

    def remove(self, index):
        if self.parent.data:
            self.parent.data.pop(index)
            # self.saveLstCamToJSON()

    def saveLstCamToJSON(self):
        helper._write_lscam(
            list(
                map(
                    lambda cam: {'name': cam['name'], 'url': cam['url']},
                    list(self.parent.data)
                )
            )
        )
