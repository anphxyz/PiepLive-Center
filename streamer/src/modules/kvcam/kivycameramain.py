import sys
import cv2
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.properties import ObjectProperty, BooleanProperty, StringProperty, NumericProperty
from kivy.graphics.texture import Texture
from src.modules.rightcontentview.itemcamera import ItemCamera
from threading import Thread, Event
import subprocess as sp

_CAM_NUMS_FRAME = '-2562047788015215'


class KivyCameraMain(Image):
    capture = ObjectProperty(None)
    crFrame = ObjectProperty(None)
    name = StringProperty('')
    url = StringProperty('')
    resource_type = StringProperty('')
    event_capture = None
    default_frame = 'src/images/splash.jpg'
    pipe = None
    f_parent = None
    typeOld = ''

    def __init__(self, **kwargs):
        super(KivyCameraMain, self).__init__(**kwargs)
        self.show_captured_img(self.default_frame)
        self.stop = Event()

    def set_data_source(self, input):
        if self.capture is not None:
            self.capture.release()
        self.stop_update_capture()
        self.name = input['name']
        self.url = input['url']
        self.resource_type = input['type']
        self.release()
        try:
            if self.resource_type == "M3U8":
                command = ["ffmpeg-win/ffmpeg.exe","-y","-i",f"{input['url']}","-ab","128k","-ac","2","-ar","44100","-vb","3072k","-r","25",f"src/export/{'output'}.flv"]
                si = subprocess.STARTUPINFO()
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                self.pipe = subprocess.Popen(command, startupinfo=si)
                self.url = 'src/export/{}.flv'.format('output')
            else:
                if self.typeOld == 'M3U8':
                    command =  'ffmpeg-win/ffmpeg.exe -y -loop 1 -i src/images/splash.jpg -i src/musics/muted.mp3 -filter_complex:0 "scale=-1:720,pad=1280:720:(1280-iw)/2:(720-ih)/2,setsar=1" -filter_complex:1 "volume=0" -r 25 src/export/output.flv'
                    si = subprocess.STARTUPINFO()
                    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    self.pipe = subprocess.Popen(command, startupinfo=si)
                    Clock.schedule_once(lambda x: self.pipe.kill() , 5)
            if self.f_parent is not None:
                if self.resource_type == "M3U8" or self.resource_type == "VIDEO":
                    self.f_parent.refresh_stream()
                elif self.typeOld == "M3U8" or self.typeOld == "VIDEO":
                    self.f_parent.refresh_stream()
            self.typeOld = input['type']

        except Exception as e:
            print("Exception:", e)
            if self.resource_type == "M3U8" or self.resource_type == "VIDEO":
                self.f_parent.refresh_stream()
            elif self.typeOld == "M3U8" or self.typeOld == "VIDEO":
                self.f_parent.refresh_stream()
            self.typeOld = input['type']


        capture = None
        if 'capture' in input and input['capture'] is not None:
            capture = input['capture']
        self.init_capture(capture)

    def init_capture(self, capture=None):
        try:
            if self.resource_type == 'IMG':
                self.show_captured_img(self.url)
            else:
                if capture is not None:
                    self.capture = capture 
                else:
                    if self.resource_type == 'CAMERA':
                        self.capture = cv2.VideoCapture(int(self.url))
                    else:
                        self.capture = cv2.VideoCapture(self.url)

                if self.capture is not None and self.capture.isOpened():
                    print(">>CAPTURE FINED:")
                    # sp.call(self._process())
                    self.event_capture = Clock.schedule_interval(self.update, 1.0 / 30)
                else:
                    print("cv2.error:")
                    if self.capture is not None:
                        self.capture.release()
                    self.show_captured_img(self.default_frame)
        except cv2.error as e:
            print("cv2.error:", e)
        except Exception as e:
            print("Exception:", e)
    
    def _process(self):
        self.event_capture = Clock.schedule_interval(self.update, 1.0 / 30)
    
    def show_captured_img(self, url=None):
        cap = cv2.VideoCapture(url or self.url)
        ret, frame = cap.read()
        if ret:
            self.update_texture_from_frame(frame)
        cap.release()
        del ret, frame, cap

    def stop_update_capture(self):
        if self.event_capture is not None:
            self.event_capture.cancel()

    def update(self, dt):
        try:
            # stoped
            if not self.capture or not self.capture.grab():
                return False
            # playing
            if self.capture.isOpened():
                ret, frame = self.capture.retrieve()
                if ret:
                    self.update_texture_from_frame(frame)

        except IOError:
            print('update interval fail--')

    def update_texture_from_frame(self, frame):
        fshape = frame.shape
        texture = Texture.create(size=(fshape[1], fshape[0]), colorfmt='bgr')
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.texture = texture
        del frame

    def release(self):
        if self.pipe is not None:
            self.pipe.kill()
        if self.capture is not None:
            self.capture.release()