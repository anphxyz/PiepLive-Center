import src.utils.kivyhelper as kv_helper
from src.utils import helper
from threading import Thread, Event
from kivy.clock import Clock, mainthread
from kivy.graphics import Fbo, ClearColor, ClearBuffers, Scale, Translate
from kivy.uix.relativelayout import RelativeLayout
from src.modules.kvcam.kivycameramain import KivyCameraMain
from src.modules.kvcam.kivycameramini import KivyCameraMini
from src.modules.custom.pieplabel import PiepLabel
from src.modules.custom.piepimage import PiepImage
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from src.models.normal_model import Normal_model
import subprocess
import cv2
import time
import numpy as np
import array

Builder.load_file('src/ui/mainstream.kv')
class MainStream(RelativeLayout):
    camera= ObjectProperty()
    cameraMini= ObjectProperty()
    f_parent= ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MainStream, self).__init__(**kwargs)
        self.f_width = 1280
        self.f_height = 720
        self.capture = None
        self.fps = 25
        self.v_bitrate = "3072k"
        self.urlStream = ''
        self.devAudio = None
        self.deviceVolume = 100
        self.isStream = False
        self.isRecord = False
        self.pipe = None
        self.pipe2 = None
        self.lsSource = []
        self.command = []
        self.event = None
        self.canvas_parent_index = 0
        self.stop = Event()
        self.reconnect = 0
        self.streamType = ''
        self.mgrSchedule = None
        self.is_loop = False
        self.current_schedule = -1
        self.dataCam = {
            "name": "defaul",
            "url": "src/images/splash.jpg",
            "type": "IMG"
        }

    def _load(self):
        try:
            command =  'ffmpeg-win/ffmpeg.exe -y -loop 1 -i src/images/splash.jpg -i ../resource/media/muted.mp3 -filter_complex:0 "scale=-1:720,pad=1280:720:(1280-iw)/2:(720-ih)/2,setsar=1" -filter_complex:1 "volume=0" -r 25 ../resource/media/output.flv ../resource/media/output_hls.flv'
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            self.pipe2 = subprocess.Popen(command, startupinfo=si)
            Clock.schedule_once(lambda x: self.pipe2.kill() , 5)
        except IOError:
            pass

    def show_camera_mini(self):
        self.cameraMini.opacity = 1
        self.cameraMini.set_data_source({
            "name": "camera mini",
            "url": "0",
            "type": "CAMERA"
        })
        # self.cameraMini.set_data_source({
        #     "name": "camera mini",
        #     "url": "rtsp://viewer:FB1D2631C12FE8F7EE8951663A8A108@14.241.131.216:554",
        #     "type": "RTSP"
        # })

    def hide_camera_mini(self):
        self.cameraMini.opacity = 0
        self.cameraMini.release()

    def switch_display(self, _val):
        temp = self.camera.capture
        self.camera.capture = self.cameraMini.capture
        self.cameraMini.capture = temp
        del temp
    
    def _set_capture(self, data_src, data_type, is_from_schedule):
        self.streamType = data_type
        self.dataCam = data_src
        self.camera.f_parent = self
        self.camera.set_data_source(data_src)
        if self.streamType == "SCHEDULE":
            if is_from_schedule == False:
                self.start_schedule(True)
        elif self.mgrSchedule is not None:
            self.mgrSchedule.cancel()

    def refresh_stream(self):
        if self.isStream is True:
            self.pipe.kill()
            self.prepare()

    def _set_source(self,lsSource):
        self.lsSource = lsSource

    def is_streaming(self):
        return self.isStream

    def record(self):
        if self.record:
            self.isRecord = False
        else:
            self.isRecord = True

    def startStream(self):
        try:
            self.fbo = Fbo(size=(self.f_width, self.f_height))
            with self.fbo:
                ClearColor(0, 0, 0, 1)
                ClearBuffers()
                Scale(1, -1, 1)
                Translate(-self.x, -self.y - self.f_height, 0)
            self.fbo.add(self.canvas)

            self.isStream = True
            Thread(target=self._process).start()
        except IOError:
            kv_helper.getApRoot().triggerStop()
        

    def _process(self):
        self.event = Clock.schedule_interval(self.stream, 1/25)

    @mainthread
    def stream(self, fps):
        try:
            if self.isStream:
                if self.parent is not None:
                    self.canvas_parent_index = self.parent.canvas.indexof(self.canvas)
                    if self.canvas_parent_index > -1:
                        self.parent.canvas.remove(self.canvas)
                self.fbo.draw()
                self.pipe.stdin.write(self.fbo.pixels)
                self.fbo.remove(self.canvas)
                if self.parent is not None and self.canvas_parent_index > -1:
                    self.parent.canvas.insert(self.canvas_parent_index, self.canvas)
                self.reconnect = 0
        except IOError as e:
            self.stopStream()
            self.reconnect += 2
            normal = Normal_model()
            key = self.f_parent.bottom_left.stream_key.text.split("?")[0]
            normal.reset_link_stream(key)
            Clock.schedule_once(self.reconnecting,self.reconnect)
            
    def reconnecting(self, dt):
        if self.reconnect > 10:
            kv_helper.getApRoot().triggerStop()
        else:
            if bool(self.prepare()):
                self.startStream()
    
    def stopStream(self):
        self.isStream = False
        if self.event is not None:
            self.event.cancel()
        if self.pipe is not None:
            self.pipe.kill()
        self.fbo.remove(self.canvas)
        if self.stop is not None:
            self.stop.set()
        self.fbo.remove(self.canvas)
        if self.parent is not None and self.canvas_parent_index > -1:
            self.parent.canvas.insert(self.canvas_parent_index, self.canvas)
        print("--- STOP ---")
        
    def set_url_stream(self, urlStream):
        self.urlStream = urlStream

    def set_device_audio(self, devAudio):
        self.devAudio = devAudio

    def draw_element(self):
        numau = 0
        inp = []
        txt = _map = ''

        numau += 1
        inp.extend(['-stream_loop','-1',"-i", '../resource/media/muted.mp3'])
        txt += f"[{numau}:a]volume=0[a{numau}];"
        _map += f'[a{numau}]'

        if self.dataCam['type'] == "VIDEO" or self.dataCam['type'] == "M3U8":
            url = '../resource/media/output.flv'
            if self.dataCam['type'] == "M3U8":
                url = '../resource/media/output_hls.flv'
            numau += 1
            print("========================")
            print("========"+self.camera.duration+"========")
            print("========================")
            if self.camera.duration == "00:00:00":
                inp.extend(["-i", url])
            else:
                inp.extend(["-ss", self.camera.duration,"-i", url])
            
            txt += f"[{numau}:a]volume=1[a{numau}];"
            _map += f'[a{numau}]'

        if len(self.lsSource) > 0:
            for value in self.lsSource:
                if value['active'] == 1:
                    if(value['type'] == 'audio'):
                        inp.extend(['-stream_loop','-1',"-i", value['src']])
                        numau += 1
                        txt += f'[{numau}:a]volume={str(value["volume"]/100)}[a{numau}];'
                        _map += f'[a{numau}]'
        if self.devAudio is not None:
            inp.extend(['-f', 'dshow', '-i', 'audio={}'.format(self.devAudio)])
            numau += 1
            txt += f"[{numau}:a]volume={str(self.deviceVolume/100)}[a{numau}];"
            _map += f'[a{numau}]'

        if numau > 0:
            txt += _map + f'amix={str(numau)}[a]'

        if len(txt) > 0:
            inp.extend(['-filter_complex', txt,'-map','0:v', '-map','[a]'])
            
        return inp

    def prepare(self):
        try:
            self.command = ['ffmpeg-win/ffmpeg.exe','-y', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', '{}x{}'.format(self.f_width, self.f_height), '-i', '-']
            
            self.command.extend(self.draw_element())
            # encode
            self.command.extend(['-vb', str(self.v_bitrate), '-preset', 'veryfast', '-r', '25'])
            # tream
            self.command.extend(['-f', 'flv', self.urlStream])

            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            self.pipe = subprocess.Popen(self.command, stdin=subprocess.PIPE, startupinfo=si)
            return True

        except IOError:
            print("Exception prepare:")
            return False
            
    def prepare_audio(self):
        pass

    def release(self):
        if self.event is not None:
            self.event.cancel()
        if self.pipe is not None:
            self.pipe.kill()
        if self.camera is not None:
            self.camera.release()
        if self.pipe2 is not None:
            self.pipe2.kill()
        if self.mgrSchedule is not None:
            self.mgrSchedule.cancel()

    def on_change_Volume(self, idx, value):
        if idx is not None and value is not None:
            if idx != -1:
                for _s in self.lsSource:
                    if _s['idx'] == idx:
                        _s['volume'] = value
                        helper._write_lsStaticSource(self.lsSource)
                        break
            else:
                self.deviceVolume = value

            if self.isStream is True:
                self.pipe.kill()
                self.prepare()

    def on_change_position(self, idx, pos_x, pos_y, parentName):
        self.f_parent.on_change_position(idx, pos_x, pos_y)
        # for child in self.mainview.children:
        #     if child.idx == idx:
        #         child.x = pos_x
        #         child.top = pos_y
        #         break

    def show_text(self, text, font, size, color, pos_x, pos_y, active, idx, new):
        if new:
            pText = PiepLabel(text='[color=' + str(color) + ']' + text + '[/color]',
                            font_size=size,
                            font_name=font,
                            x=pos_x,
                            y=pos_y,
                            markup=True,
                            opacity=active,
                            idx=idx,
                            parentName='main')
            self.add_widget(pText)
            # pText2 = PiepLabel(text='[color=' + str(color) + ']' + text + '[/color]',
            #                    font_size=size,
            #                    font_name=font,
            #                    x=pos_x,
            #                    y=pos_y,
            #                    markup=True,
            #                    opacity=active,
            #                    idx=idx,
            #                    parentName='canvas')
            # self.mainview.add_widget(pText2)
        else:
            for child in self.children:
                if child.idx != None and child.idx == idx:
                    child.text = '[color=' + str(color) + ']' + text + '[/color]'
                    child.font_size = str(size)
                    child.font_name = font
                    #child.x = pos_x
                    #child.y = pos_y
                    #child.markup = True
                    #child.opacity = active
                    #child.idx = idx
                    break


    def show_image(self, src, pos_x, pos_y, w, h, active, idx, new):
        if new:
            pimage = PiepImage(source=src,
                            size_hint=(None,None),
                            width=w,
                            height=h,
                            x=pos_x,
                            y=pos_y,
                            opacity=active,
                            idx=idx,
                            parentName='main')
            self.add_widget(pimage)
            # pimage2 = PiepImage(source=src,
            #                    size=(w, h),
            #                    x=pos_x,
            #                    y=pos_y,
            #                    opacity=active,
            #                    idx=idx,
            #                    parentName='canvas')
            # self.mainview.add_widget(pimage2)
        else:
            for child in self.children:
                if child.idx != None and child.idx == idx:
                    child.source = src
                    child.size = (w, h)
                    break

    def on_off_source(self, idx, value):
        for child in self.children:
            if child.idx != None and child.idx == idx:
                if value:
                    child.opacity = 1
                else:
                    child.opacity = 0
                break
        
        # for child in self.mainview.children:
        #     if child.idx != None and child.idx == idx:
        #         if value:
        #             child.opacity = 1
        #         else:
        #             child.opacity = 0

    def on_change_audio(self):
        if self.isStream is True:
            self.pipe.kill()
            self.prepare()

    def start_schedule(self, isSchedule):
        if self.mgrSchedule is not None:
            self.mgrSchedule.cancel()
        self.ls_schedule = self.f_parent.right_content.tab_schedule.ls_schedule.get_data()

        if isSchedule:
            index = self.f_parent.right_content.tab_schedule.ls_schedule.getCurrentIndex()
            self.mgrSchedule = Clock.schedule_once(self.process_schedule , self.ls_schedule[index]['duration']+3)
    
    def process_schedule(self, fps):
        if self.mgrSchedule is not None:
            self.mgrSchedule.cancel()
        self.current_schedule = self.f_parent.right_content.tab_schedule.ls_schedule.getCurrentIndex() + 1
        
        if self.current_schedule >= len(self.ls_schedule):
            if self.is_loop:
                self.current_schedule = 0
            else:
                return False
        data_src = self.ls_schedule[self.current_schedule]
        self.f_parent.right_content.tab_schedule.ls_schedule.setPlayed(self.current_schedule)
        self._set_capture(data_src, 'SCHEDULE', True)
        self.mgrSchedule = Clock.schedule_once(self.process_schedule , self.ls_schedule[self.current_schedule]['duration']+3)

    def run_schedule(self):
        self.mgrSchedule = Clock.schedule_once(self.process_schedule , self.ls_schedule[self.current_schedule]['duration'])

    def loop_schedule(self,_val):
        self.is_loop = _val
        