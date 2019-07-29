import cv2, subprocess
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.properties import ObjectProperty, BooleanProperty, StringProperty, NumericProperty
from kivy.graphics.texture import Texture
from kivy.uix.behaviors import DragBehavior
from kivy.graphics import Rectangle, Color
from src.modules.rightcontentview.itemcamera import ItemCamera
from threading import Thread, Event
from kivy.lang import Builder
from functools import partial
from src.utils import helper

_CAM_NUMS_FRAME = '-2562047788015215'

kv = '''
<KivyCameraMini>:
    drag_rectangle: self.x, self.y, self.width, self.height
    drag_timeout: 10000000
    drag_distance: 0
    keep_ratio: True
'''

Builder.load_string(kv)

class KivyCameraMini(DragBehavior, Image):
    capture = ObjectProperty(None)
    url = StringProperty('')
    resource_type = StringProperty('')
    buffer_rate = NumericProperty(0)
    duration_total = NumericProperty(0)
    duration_total_n = NumericProperty(1)
    duration_current = NumericProperty(0)
    duration_fps = NumericProperty(25)
    reconnect = NumericProperty(0)

    event_capture = None
    default_frame = helper._IMAGES_PATH + 'splash.jpg'
    pipe = None
    pipe2 = None
    f_parent = None
    typeOld = StringProperty('')
    category = StringProperty('')
    data_src = None

    def __init__(self, **kwargs):
        super(KivyCameraMini, self).__init__(**kwargs)
        self.f_height = 720
        self.show_captured_img(self.default_frame)
        self.stop = Event()
        self.data_src = {
            "id": "8c31e461881ac85d932bb461b132f32f",
            "name": "image",
            "url": self.default_frame,
            "type": "IMG"
        }

    def on_touch_up(self, touch):
        if self._get_uid('svavoid') in touch.ud:
            return super(DragBehavior, self).on_touch_up(touch)

        if self._drag_touch and self in [x() for x in touch.grab_list]:
            touch.ungrab(self)
            self._drag_touch = None
            ud = touch.ud[self._get_uid()]
            if ud['mode'] == 'unknown':
                super(DragBehavior, self).on_touch_down(touch)
                Clock.schedule_once(partial(self._do_touch_up, touch), .1)
        else:
            if self._drag_touch is not touch:
                super(DragBehavior, self).on_touch_up(touch)
        return self._get_uid() in touch.ud

    def set_data_source(self, input, category):
        self.data_src = input
        self.url = input['url']
        self.resource_type = input['type']
        self.category = category
        self.buffer_rate = 0
        self.duration_total = 0
        self.duration_current = 0
        self.duration_total_n = 1
        self.duration_fps = 25
        
        if self.pipe is not None:
            self.pipe.kill()
        if self.pipe2 is not None:
            self.pipe2.kill()
        if self.capture is not None:
            self.capture.release()
        self.stop_update_capture()
        fps = 25
        dura = 0
        try:
            if self.resource_type == "M3U8" or self.resource_type == "VIDEO":
                try:
                    _cap = cv2.VideoCapture(self.url)
                    if _cap.isOpened():
                        fps = _cap.get(cv2.CAP_PROP_FPS)
                        if self.resource_type == 'VIDEO':
                            if fps >= 25:
                                self.duration_total_n = _cap.get(cv2.CAP_PROP_FRAME_COUNT)/_cap.get(cv2.CAP_PROP_FPS)*25
                                self.duration_total = _cap.get(cv2.CAP_PROP_FRAME_COUNT)/_cap.get(cv2.CAP_PROP_FPS)
                                dura = int(_cap.get(cv2.CAP_PROP_FRAME_COUNT)/_cap.get(cv2.CAP_PROP_FPS))
                            else:
                                self.duration_total_n = _cap.get(cv2.CAP_PROP_FRAME_COUNT)
                                self.duration_total = _cap.get(cv2.CAP_PROP_FRAME_COUNT)/25
                                dura = int(_cap.get(cv2.CAP_PROP_FRAME_COUNT)/25)
                    del _cap
                except Exception as e:
                    print("Exception:", e)
                        
                output = self.f_parent.mini_url_flv
                timeout = 1
                command = ["ffmpeg/ffmpeg.exe","-y","-nostats","-i",self.url,'-stream_loop','-1',"-i", "../resource/media/muted2.mp3","-ar","44100","-ab", "160k","-vb",self.f_parent.v_bitrate, "-preset", "veryfast","-r","25",'-g','60','-threads', '2',output]
                
                if self.category == "PRESENTER":
                    self.url = self.data_src['rtmp']
                    output = self.f_parent.mini_url_flv_hls
                    timeout=2
                    command = ["ffmpeg/ffmpeg.exe","-y","-nostats","-i", self.url,"-pix_fmt", "yuv420p", "-vsync", "1","-flags","+global_header", "-preset", "veryfast","-ar","44100", "-ab", "160k","-af", "aresample=async=1:min_hard_comp=0.100000:first_pts=0","-vb",self.f_parent.v_bitrate,"-r","25",'-g','25','-threads', '2',output]
                elif self.resource_type == "M3U8":
                    output = self.f_parent.mini_url_flv_hls
                    timeout=1
                    command = ["ffmpeg/ffmpeg.exe","-y","-nostats","-f", "hls","-i", self.url,"-pix_fmt", "yuv420p", "-vsync", "1","-flags","+global_header", "-preset", "veryfast","-ar","44100", "-ab", "160k","-af", "aresample=async=1:min_hard_comp=0.100000:first_pts=0","-vb",self.f_parent.v_bitrate,"-r","25",'-g','25','-threads', '2',output]
                elif self.resource_type == "RTSP":
                    timeout=1
                    command = ["ffmpeg/ffmpeg.exe","-y","-i", self.url,"-acodec", "copy", "-vcodec", "copy","-r","25",'-threads', '2',output]
                else:
                    if fps < 25:
                        command = ["ffmpeg/ffmpeg.exe","-y","-nostats","-i",self.url,'-stream_loop','-1',"-i", "../resource/media/muted2.mp3","-ab", "160k","-af", f"atempo={25/fps}","-vf", f"setpts={fps/25}*PTS","-vb",self.f_parent.v_bitrate,"-r","25",'-threads', '2',output]
                    if self.typeOld == 'M3U8':
                        command2 =  f'ffmpeg/ffmpeg.exe -y "-nostats -loop 1 -i {self.default_frame} -i ../resource/media/muted.mp3 -filter_complex:0 "scale=-1:720,pad=1280:720:(1280-iw)/2:(720-ih)/2,setsar=1" -filter_complex:1 "volume=0" -r 25 -threads 2 {self.f_parent.mini_url_flv_hls}'
                        si = subprocess.STARTUPINFO()
                        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        self.pipe2 = subprocess.Popen(command2, startupinfo=si)
                        Clock.schedule_once(lambda x: self.pipe2.kill() , 5)
                
                si = subprocess.STARTUPINFO()
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                self.pipe = subprocess.Popen(command, startupinfo=si)
                self.url = output
                Clock.schedule_once(self.process_set_data ,timeout)
            else:
                if self.typeOld == 'M3U8' or self.typeOld == 'VIDEO':
                    command =  f'ffmpeg/ffmpeg.exe -y -loop 1 -i {self.default_frame} -i ../resource/media/muted.mp3 -filter_complex:0 "scale=-1:720,pad=1280:720:(1280-iw)/2:(720-ih)/2,setsar=1" -filter_complex:1 "volume=0" -r 25 -threads 2 {self.f_parent.mini_url_flv} {self.f_parent.mini_url_flv_hls}'
                    si = subprocess.STARTUPINFO()
                    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    self.pipe = subprocess.Popen(command, startupinfo=si)
                    Clock.schedule_once(lambda x: self.pipe.kill() , 5)
                Clock.schedule_once(self.process_set_data , 0)
        except :
            print("Exception:")
            Clock.schedule_once(self.process_set_data , 0)
        
    def process_set_data(self, second):
        try:
            self.stop.set()
            th = Thread(target=self.init_capture())
            th.start()
            # self.init_capture()
        except Exception:
            pass

    def init_capture(self):
        try:
            if self.capture is not None:
                self.capture.release()
            self.stop_update_capture()
            
            if self.resource_type == 'IMG' and '.gif' in self.url:
                self.resource_type = 'GIF'
            if self.resource_type == 'CAMERA':
                self.capture = cv2.VideoCapture(int(self.url))
            else:
                self.capture = cv2.VideoCapture(self.url)

            if self.capture is not None and self.capture.isOpened():
                self.reconnect = 0
                if self.resource_type != 'VIDEO' and self.resource_type != "M3U8":
                    self.duration_fps = self.capture.get(cv2.CAP_PROP_FPS)
                self.event_capture = Clock.schedule_interval(self.update, 1.0 / self.duration_fps)
                if self.f_parent is not None:
                    if self.resource_type == "M3U8" or self.resource_type == "VIDEO":
                        self.f_parent.refresh_stream()
                    elif self.typeOld == "M3U8" or self.typeOld == "VIDEO":
                        self.f_parent.refresh_stream()
                self.typeOld = self.resource_type
            else:
                if self.reconnect >= 3:
                    if self.capture is not None:
                        self.capture.release()
                    self.show_captured_img(self.default_frame)
                else:
                    self.reconnect += 1
                    self.init_capture()
                
        except Exception as e:
            print("Exception init_capture:", e)
    
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
            if self.capture.isOpened():
                if not self.capture.grab():
                    pass
                else:
                    ret, frame = self.capture.retrieve()
                    if ret:
                        if self.resource_type == 'VIDEO' or self.resource_type == 'M3U8':
                            if self.resource_type == 'VIDEO':
                                self.buffer_rate = self.capture.get(cv2.CAP_PROP_POS_FRAMES) / self.duration_total_n
                            self.duration_current = self.capture.get(cv2.CAP_PROP_POS_FRAMES)/self.capture.get(cv2.CAP_PROP_FPS)
                        self.update_texture_from_frame(frame)
        except IOError:
            print("Exception update:")

    def update_texture_from_frame(self, frame):
        try:
            frame = self.resizeFrame(frame)
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            buf = cv2.flip(frame, 0).tostring()
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.texture = texture
            del frame
        except IOError:
            print("Exception update_texture_from_frame:")

    def release(self):
        if self.pipe is not None:
            self.pipe.kill()
        if self.pipe2 is not None:
            self.pipe2.kill()
        if self.capture is not None:
            self.capture.release()

    def resizeFrame(self, frame):
        if frame is None:
            return frame
        h, w, c = frame.shape
        r = w / h
        nH = self.f_height
        nW = int(nH * r)
        return cv2.resize(frame, (nW, nH), interpolation=cv2.INTER_AREA)