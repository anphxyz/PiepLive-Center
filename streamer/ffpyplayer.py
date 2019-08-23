import kivy

from kivy.app import App
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.properties import ObjectProperty, BooleanProperty, StringProperty, NumericProperty
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout

import time, os
import subprocess
import numpy as np

kv ='''
<MyWidget>:
    id:mainView
    size_hint:1,1
    Button:
        id:btn_start
        size_hint:None,None
        width:120
        text:'Start'
        font_size: sp(12)
        on_press: root.playff()

'''
Builder.load_string(kv)

class MyWidget(BoxLayout):
    mainView = ObjectProperty()

    def __init__(self, *args, **kwargs):
        super(MyWidget, self).__init__(*args, **kwargs)
        self.pipe = None

    def playff(self):
        video_path="C:/Users/Thong/Desktop/piep-source/videos/anh-thuong-em-nhat-ma-30.mp4"

        cm = ["ffmpeg/ffplay.exe" , video_path]
        cm = ["ffmpeg/ffmpeg.exe","-y","-i",video_path,"-filter_complex","scale=-1:720","-ar","44100","-ab", "128k","-vb",'4M',"-r","25","aa.flv"]
        self.pipe = subprocess.Popen(cm, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out,err = self.pipe.communicate()
        while out:
            print(out,err)
    
    def on_stop(self):
        if self.pipe is not None:
            self.pipe.kill()

class TestApp(App):
    # mainView = ObjectProperty()
    
    def build(self):
        self.my = MyWidget()
        return self.my

    def on_stop(self):
        self.my.on_stop()

if __name__ == '__main__':
    TestApp().run()