from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from src.modules.bottomleft.bottomleft import TextDialog
from src.modules.bottomleft.bottomleft import ImageDialog
from src.modules.bottomleft.bottomleft import AudioDialog
from src.modules.custom.addschedule import AddSchedule
# from src.modules.login import Login
from src.modules.mainstream import MainStream
from src.utils import kivyhelper as kv_helper
from src.utils import helper as helper
from kivy.lang import Builder
import sounddevice as sd

Builder.load_file('src/ui/main.kv')

class MainView(Widget):
    mainStream = ObjectProperty()
    bottom_left = ObjectProperty()
    btn_start = ObjectProperty()
    # btn_record = ObjectProperty()
    # btn_setting = ObjectProperty()
    login_popup = ObjectProperty()
    right_content = ObjectProperty()
    videoBuffer = ObjectProperty()

    def __init__(self, **kwargs):
        super(MainView, self).__init__(**kwargs)
        self.lsAudio = []
        self.lsSource = []
        self.f_width = 1280
        self.f_height = 720
        self.setting = None

    def on_start(self):
        self.mainStream._load()
        self.mainStream.f_parent = self
        self.bottom_left.f_parent = self
        self.right_content.f_parent = self
        self.setting = helper._load_setting()
        if self.setting['ouput_resolution'] is not None:
            self.f_width = self.mainStream.f_width = self.setting['ouput_resolution'][0]
            self.f_height = self.mainStream.f_height = self.setting['ouput_resolution'][1]
        if self.setting['vbitrate'] is not None:
            self.v_bitrate = self.mainStream.v_bitrate = self.setting['vbitrate']
        if self.setting['stream_server'] is not None:
            self.bottom_left.stream_server.text = self.setting['stream_server']
        if self.setting['stream_key'] is not None:
            self.bottom_left.stream_key.text = self.setting['stream_key']

        self.mainStream.urlStream = self.bottom_left.stream_server.text + \
            self.bottom_left.stream_key.text
        self.initAudio()
        self.initSource()
        self.bottom_left.list_mixer.set_source(self.lsAudio)
        self.init_right_content_media()
        self.init_right_content_image()
        self.init_right_content_cam()
        self.init_right_content_presenter()
        self.init_right_content_schedule()

    def init_right_content_media(self):
        self.right_content.tab_media.ls_media.set_data()
        
    def init_right_content_image(self):
        self.right_content.tab_image.ls_image.set_data()

    def init_right_content_cam(self):
        self.right_content.tab_camera.ls_camera.set_data()

    def init_right_content_presenter(self):
        self.right_content.tab_presenter.ls_presenter.set_data()

    def init_right_content_schedule(self):
        self.right_content.tab_schedule.ls_schedule.set_data()

    def initAudio(self):
        try:
            self.audios = sd.query_devices(kind='input')
            if self.audios is not None:
                if 'Realtek High Defini' in self.audios['name']:
                    self.audios['name'] += 'tion Audio)'
                _audio = {
                    'name': self.audios['name'],
                    'value': self.audios['name'],
                    'volume': 100,
                    'idx': -1
                }
                self.lsAudio.append(_audio)
                self.changeAudio(self.audios['name'])
        except Exception as e:
            print("Exception:", e)

    def initSource(self):
        self.lsSource = helper._load_lsStaticSource()
        self.mainStream.lsSource = self.lsSource
        self.bottom_left.list_source.set_source(self.lsSource)
        for idx, _s in enumerate(self.lsSource):
            _s['idx'] = idx
            _s['total'] = len(self.lsSource)
            if _s['type'] == 'text':
                self.mainStream.show_text(_s['label'], _s['font'], _s['size'],
                                        _s['color'], _s['pos_x'], _s['pos_y'], _s['active'], idx, True)
            elif _s['type'] == 'image':
                self.mainStream.show_image(_s['src'], _s['pos_x'], _s['pos_y'],
                                        _s['width'], _s['height'], _s['active'], idx, True)
            elif _s['type'] == 'audio' and _s['active'] == 1:
                _audio = {'name': _s['name'],'value': _s['src'],'volume': _s['volume'],'idx': idx}
                self.lsAudio.append(_audio)


    def changeSrc(self, data_src, data_type):
        if bool(data_src) and self.mainStream is not None:
            self.mainStream._set_capture(data_src, data_type, False)

    def changeAudio(self, value):
        if value is not None and self.mainStream is not None:
            self.mainStream.set_device_audio(value)

    def changeAudioVolume(self, idx, volume):
        if self.mainStream is not None:
            self.mainStream.on_change_Volume(idx, volume)

    def mClick(self, obj):
        if obj == 'start':
            if self.mainStream.isStream is False:
                if len(self.bottom_left.stream_server.text) == 0 or len(self.bottom_left.stream_key.text) == 0:
                    return False
                self.mainStream.set_url_stream(
                    self.bottom_left.stream_server.text+self.bottom_left.stream_key.text)
                if bool(self.mainStream.prepare()):
                    self.mainStream.startStream()
                    self.btn_start.text = "Stop Streaming"
                    self.btn_start.background_color = .29, .41, .15, 0.9
                    if self.setting['stream_server'] is not None:
                        self.setting['stream_server'] = self.bottom_left.stream_server.text
                    if self.setting['stream_key'] is not None:
                        self.setting['stream_key'] = self.bottom_left.stream_key.text
                    helper._write_setting(self.setting)

            elif self.mainStream.isStream is True:
                self.mainStream.stopStream()
                self.btn_start.text = "Start Streaming"
                self.btn_start.background_color = .29, .41, .55, 1
        # elif obj == 'record':
        #     if self.mainStream.isRecord is False:
        #         self.btn_record.text = "Stop Record"
        #         self.btn_record.background_color = .29, .41, .15, 0.9
        #     elif self.mainStream.isStream is True:
        #         self.btn_record.text = "Start Record"
        #         self.btn_record.background_color = .29, .41, .55, 1
        #     self.mainStream.record()

    def triggerStop(self):
        self.mainStream.stopStream()
        self.btn_start.text = "Start Streaming"
        self.btn_start.background_color = .29, .41, .55, 1

    def on_off_source(self, index, value):
        ite = self.lsSource[index]
        if ite['type'] == 'audio':
            if value:
                _audio = {'name':  ite['name'], 'value': ite['name'],
                          'volume': ite['volume'], 'idx': ite['idx']}
                self.bottom_left.list_mixer.add_source(_audio)
            else:
                self.bottom_left.list_mixer.del_source(ite['idx'])
        else:
            self.mainStream.on_off_source(ite['idx'], value)

        self.lsSource[index]["active"] = value
        helper._write_lsStaticSource(self.lsSource)
        self.mainStream._set_source(self.lsSource)
        if ite['type'] == 'audio':
            self.mainStream.on_change_audio()

    def openSetting(self):
        pass

    def add_source(self, type):
        if type == 'IMAGE':
            obj = ImageDialog(self)
            obj.open()
        elif type == 'TEXT':
            obj = TextDialog(self)
            obj.open()
        elif type == 'AUDIO':
            obj = AudioDialog(self)
            obj.open()

    def add_text(self, index, name, label, font, size, color, pos_x, pos_y):
        if index == -1:
            idx = 0
            if len(self.lsSource) > 0:
                idx = self.lsSource[len(self.lsSource)-1]['total']
            text = {
                "type": "text",
                "active": 1,
                "name": name,
                "label": label,
                "pos_x": pos_x,
                "pos_y": pos_y,
                "font": font,
                "size": int(size),
                "color": color,
                "shadow_color": None,
                "shadow_x": 0,
                "shadow_y": 0,
                "box": None,
                "box_color": None,
                "idx": idx,
                'total': idx+1
            }
            self.lsSource.append(text)
            helper._write_lsStaticSource(self.lsSource)
            self.bottom_left.list_source.add_source(text)
            self.mainStream.show_text(label, font, size, color, pos_x, pos_y, 1, idx, True)
        else:
            self.lsSource[index]['name'] = name
            self.lsSource[index]['label'] = label
            self.lsSource[index]['font'] = font
            self.lsSource[index]['size'] = int(size)
            self.lsSource[index]['color'] = color
            helper._write_lsStaticSource(self.lsSource)
            self.bottom_left.list_source.update_source(index,{"name":name, "active": self.lsSource[index]["active"]})
            self.mainStream.show_text(label, font, int(size), color, pos_x, pos_y, self.lsSource[index]["active"], self.lsSource[index]['idx'], False)

    def add_image(self, index, name, src, pos_x, pos_y, width, height):
        if index == -1:
            idx = 0
            if len(self.lsSource) > 0:
                idx = self.lsSource[len(self.lsSource)-1]['total']
            image = {
                "type": "image",
                "active": 1,
                "name": name,
                "src": src,
                "pos_x": pos_x,
                "pos_y": pos_y,
                "width": int(width),
                "height": int(height),
                "timeStart": None,
                "timeEnd": None,
                "idx": idx,
                'total': idx+1
            }
            self.lsSource.append(image)
            helper._write_lsStaticSource(self.lsSource)
            self.bottom_left.list_source.add_source(image)
            self.mainStream.show_image(src, pos_x, pos_y, width, height, 1, idx,True)
        else:
            self.lsSource[index]['name'] = name
            self.lsSource[index]['src'] = src
            self.lsSource[index]['width'] = int(width)
            self.lsSource[index]['height'] = int(height)
            helper._write_lsStaticSource(self.lsSource)
            self.bottom_left.list_source.update_source(index,{"name":name, "active": self.lsSource[index]["active"]})
            self.mainStream.show_image(src, pos_x, pos_y, int(width), int(height), self.lsSource[index]["active"], self.lsSource[index]['idx'], False)

    def add_audio(self, index, name, src, volume):
        if index == -1:
            idx = 0
            if self.lsSource is not None and len(self.lsSource) > 0:
                idx = self.lsSource[len(self.lsSource)-1]['total']
            audio = {
                "type": "audio",
                "active": 1,
                "name": name,
                "src": src,
                "volume": volume,
                "idx": idx,
                'total': idx+1
            }
            self.lsSource.append(audio)
            helper._write_lsStaticSource(self.lsSource)
            self.bottom_left.list_source.add_source(audio)
            self.bottom_left.list_mixer.add_source({'name': name,'value': src,'volume': volume,'idx': idx})
        else:
            self.lsSource[index]['name'] = name
            self.lsSource[index]['src'] = src
            self.lsSource[index]['volume'] = volume
            self.bottom_left.list_source.update_source(index,{"name":name, "active": self.lsSource[index]["active"]})
            self.bottom_left.list_mixer.update_source({'name': name,'value': src,'volume': volume,'idx': self.lsSource[index]['idx']})

    def delete_source(self, index):
        if self.lsSource[index]['type'] == 'audio':
            self.bottom_left.list_mixer.del_source(self.lsSource[index]['idx'])
        del(self.lsSource[index])
        helper._write_lsStaticSource(self.lsSource)

    def openLogin(self):
        self.login_popup = Login(self)
        self.login_popup.open()

    def on_stop(self):
        if self.mainStream is not None:
            self.mainStream.release()

    def on_change_position(self, idx, pos_x, pos_y):
        for _s in self.lsSource:
            if _s['idx'] == idx:
                _s['pos_x'] = pos_x
                _s['pos_y'] = pos_y
                helper._write_lsStaticSource(self.lsSource)
                break

    def on_edit_source(self,index):
        ite = self.lsSource[index]
        if ite['type'] == 'image':
            obj = ImageDialog(self, ite, index)
            obj.open()
        elif ite['type'] == 'text':
            obj = TextDialog(self, ite, index)
            obj.open()
        elif ite['type'] == 'audio':
            obj = AudioDialog(self, ite, index)
            obj.open()
    
    def open_add_schedule(self, data):
        self.add_schedule_pop = AddSchedule(self,data)
        self.add_schedule_pop.open()
