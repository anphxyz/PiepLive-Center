from kivy.uix.recycleview import RecycleView
from src.utils import helper, firebase, store
from kivy.properties import StringProperty
from kivy.clock import Clock
from src.modules.custom.popup import PiepMeConfirmPopup
import datetime
from src.modules.custom.linkaudio import LinkAudio

class ListMedia(RecycleView):

    item_playing = ''
 
    def __init__(self, **kwargs):
        super(ListMedia, self).__init__(**kwargs)

    def set_data(self):
        self.data = list(
            map(
                lambda cam: {'id': cam['id'],'name': cam['name'], 'url': cam['url'], 'type': cam['type'], 
                'duration': cam['duration'] if 'duration' in cam else 0,
                'list':'VIDEO',
                'active': (False,True) [cam['id'] == self.item_playing]},
                helper._load_video()
            )
        )

    def remove(self, index):
        if self.data:
            self.data.pop(index)
            helper._write_video(self.clean_data_to_save_json())

    def clean_data_to_save_json(self):
        return list(
            map(
                lambda cam: {'id': cam['id'],'name': cam['name'], 'url': cam['url'], 'type': cam['type'], 'duration': cam['duration']},
                list(self.data)
            )
        )

    def refresh_list(self):
        self.set_data()
        self.refresh_view()
    
    def remove_selected(self):
        PiepMeConfirmPopup(message='Are you sure to delete the selected source?',
                            callback_ok=self.process_del_selected,
                            callback_cancel=lambda: True)
                            
    def process_del_selected(self):
        temp = 0
        for child in self.children[0].children:
            if child.isCheckItem.active and child.selected == False:
                temp = 1
                if self.data:
                    self.data.pop(child.index)
        if temp == 1:
            helper._write_video(self.clean_data_to_save_json())

    def setPlayed(self,index):
        self.item_playing = self.data[index]['id']
        for obj in self.data:
            obj['active'] = False
        self.data[index]['active'] = True
        for child in self.children[0].children:
            if child.index == index:
                child.active = True
            else:
                child.active = False
    
    def refresh_view(self):
        try:
            for child in self.children[0].children:
                child.refresh_view_attrs(self,child.index, self.data[child.index])
        except:
            pass

class ListImage(RecycleView):
 
    item_playing = ''

    def __init__(self, **kwargs):
        super(ListImage, self).__init__(**kwargs)

    def set_data(self):
        self.data = list(
            map(
                lambda cam: {'id': cam['id'],'name': cam['name'], 'url': cam['url'], 'type': cam['type'], 
                'list':'IMAGE',
                'active': (False,True) [cam['id'] == self.item_playing]},
                helper._load_image()
            )
        )

    def remove(self, index):
        if self.data:
            self.data.pop(index)
            helper._write_image(self.clean_data_to_save_json())

    def clean_data_to_save_json(self):
        return list(
            map(
                lambda cam: {'id': cam['id'],'name': cam['name'], 'url': cam['url'], 'type': cam['type']},
                list(self.data)
            )
        )

    def refresh_list(self):
        self.set_data()
        self.refresh_view()
    
    def remove_selected(self):
        PiepMeConfirmPopup(message='Are you sure to delete the selected source?',
                            callback_ok=self.process_del_selected,
                            callback_cancel=lambda: True)
                            
    def process_del_selected(self):
        temp = 0
        for child in self.children[0].children:
            if child.isCheckItem.active and child.selected == False:
                temp = 1
                if self.data:
                    self.data.pop(child.index)
        if temp == 1:
            helper._write_image(self.clean_data_to_save_json())

    def setPlayed(self,index):
        self.item_playing = self.data[index]['id']
        for obj in self.data:
            obj['active'] = False
        self.data[index]['active'] = True
        for child in self.children[0].children:
            if child.index == index:
                child.active = True
            else:
                child.active = False

    def refresh_view(self):
        try:
            for child in self.children[0].children:
                child.refresh_view_attrs(self,child.index, self.data[child.index])
        except:
            pass

class ListCamera(RecycleView):
    item_playing = ""
    def __init__(self, **kwargs):
        super(ListCamera, self).__init__(**kwargs)

    def set_data(self):
        self.data = list(
            map(
                lambda cam: {'id': cam['id'],'name': cam['name'], 'url': cam['url'], 'type': cam['type'], 
                'list':'CAMERA',
                'active': (False,True) [cam['id'] == self.item_playing]},
                helper._load_lscam()
            )
        )

    def remove(self, index):
        if self.data:
            self.data.pop(index)
            helper._write_lscam(self.clean_data_to_save_json())

    def clean_data_to_save_json(self):
        return list(
            map(
                lambda cam: {'id': cam['id'],'name': cam['name'], 'url': cam['url'], 'type': cam['type']},
                list(self.data)
            )
        )

    def refresh_list(self):
        self.set_data()
        self.refresh_view()
    
    def remove_selected(self):
        PiepMeConfirmPopup(message='Are you sure to delete the selected source?',
                            callback_ok=self.process_del_selected,
                            callback_cancel=lambda: True)
                            
    def process_del_selected(self):
        temp = 0
        for child in self.children[0].children:
            if child.isCheckItem.active and child.selected == False:
                temp = 1
                if self.data:
                    self.data.pop(child.index)
        if temp == 1:
            helper._write_lscam(self.clean_data_to_save_json())

    def setPlayed(self,index):
        self.item_playing = self.data[index]['id']
        for obj in self.data:
            obj['active'] = False
        self.data[index]['active'] = True
        for child in self.children[0].children:
            if child.index == index:
                child.active = True
            else:
                child.active = False

    def refresh_view(self):
        try:
            for child in self.children[0].children:
                child.refresh_view_attrs(self,child.index, self.data[child.index])
        except:
            pass

class ListPresenter(RecycleView):

    item_playing = ''
    listenerStream = None
    listLiving = []

    def __init__(self, **kwargs):
        super(ListPresenter, self).__init__(**kwargs)
        Clock.schedule_once(self.turnOnObserver,1)

    def turnOnObserver(self,dt):
        if bool(store._get('FO100')):
            activedBu = store.getCurrentActiveBusiness()
            if bool(activedBu):
                db = firebase.config()
                if bool(db):
                    self.listenerStream = db.child(f'l500/{activedBu}/LIST').stream(self.firebaseCallback)
    
    def firebaseCallback(self, message):
        data = message['data']
        id = ln510 = 0
        if bool(data):
            if message['path'] == '/': # case init: get multi data
                keys = list(data.keys())
                for k in keys:
                    media = data[k]
                    id = int(media['_id'])
                    ln510 = int(media['LN510'])
                    self.changeStatePresenter(id, ln510)
            else:# </PL500> case change: get single data
                id = int(data['_id'])
                ln510 = int(data['LN510'])
                self.changeStatePresenter(id, ln510)

    def changeStatePresenter(self, _id, ln510):
        if ln510 == 2:
            self.listLiving.append(_id)
        elif _id in self.listLiving:
            self.listLiving.remove(_id)
        for m in self.data:
            if int(m['id']) == _id:
                if ln510 == 2:
                    m['playable'] = True
                else:
                    m['playable'] = False
        self.refresh_view()

    def stopListenerStream(self):
        if bool(self.listenerStream):
            self.listenerStream.close()

    def set_data(self):
        self.data = list(
            map(
                lambda cam: {'id': cam['id'],'name': cam['name'], 'url': cam['url'], 'type': cam['type'], 
                'rtmp': cam['rtmp'] if 'rtmp' in cam else cam['url'],
                'list':'PRESENTER',
                'active': (False,True) [cam['id'] == self.item_playing],
                'playable': False},
                helper._load_ls_presenter()
            )
        )

    def remove(self, index):
        if self.data:
            self.data.pop(index)
            helper._write_lspresenter(self.clean_data_to_save_json())

    def clean_data_to_save_json(self):
        return list(
            map(
                lambda cam: {'id': cam['id'],'name': cam['name'], 'url': cam['url'], 'type': cam['type']},
                list(self.data)
            )
        )

    def refresh_list(self):
        self.set_data()
        for m in self.data:
            if int(m['id']) in self.listLiving:
                m['playable'] = True
            else:
                m['playable'] = False
        self.refresh_view()
        self.stopListenerStream()
        self.turnOnObserver(1)

    def remove_selected(self):
        PiepMeConfirmPopup(message='Are you sure to delete the selected source?',
                            callback_ok=self.process_del_selected,
                            callback_cancel=lambda: True)
                            
    def process_del_selected(self):
        temp = 0
        for child in self.children[0].children:
            if child.isCheckItem.active and child.selected == False:
                temp = 1
                if self.data:
                    self.data.pop(child.index)
        if temp == 1:
            helper._write_lspresenter(self.clean_data_to_save_json())
    
    def setPlayed(self,index):
        self.item_playing = self.data[index]['id']
        for obj in self.data:
            obj['active'] = False
        self.data[index]['active'] = True
        for child in self.children[0].children:
            if child.index == index:
                child.active = True
            else:
                child.active = False
    def refresh_view(self):
        try:
            for child in self.children[0].children:
                child.refresh_view_attrs(self,child.index, self.data[child.index])
        except:
            pass

class ListSchedule(RecycleView):
    item_playing = ""
    total_time = StringProperty("00:00:00")

    def __init__(self, **kwargs):
        super(ListSchedule, self).__init__(**kwargs)

    def set_data(self):
        self.data = list(
            map(
                lambda cam: {'id': cam['id'],'name': cam['name'], 'url': cam['url'], 'type': cam['type'], 'duration': cam['duration'], 
                'timepoint': cam['timepoint'] if 'timepoint' in cam else 0,
                'audio': cam['audio'] if 'audio' in cam else '',
                'list':'SCHEDULE',
                'active': (False,True) [cam['id'] == self.item_playing]},
                helper._load_schedule()
            )
        )
        self.getTotalTime()

    def get_data(self):
        self.set_data()
        return self.data

    def remove(self, index):
        if self.data:
            self.data.pop(index)
            helper._write_schedule(self.clean_data_to_save_json())

    def clean_data_to_save_json(self):
        return list(
            map(
                lambda cam: {'id': cam['id'],'name': cam['name'], 'url': cam['url'], 'type': cam['type'], 'duration': cam['duration'], 'timepoint': cam['timepoint'],'audio': cam['audio']},
                list(self.data)
            )
        )
    
    def refresh_list(self):
        self.set_data()
        self.refresh_view()
        self.makeTimePointChange()
        self.refresh_view()

    def getCurrentIndex(self):
        for child in self.children[0].children:
            if child.active:
                return child.index
        return -1

    def setSelected(self,index):
        for child in self.children[0].children:
            if child.index == index:
                child.selected = True
            else:
                child.selected = False

    def setPlayed(self,index):
        self.item_playing = self.data[index]['id']
        for obj in self.data:
            obj['active'] = False
        self.data[index]['active'] = True
        for child in self.children[0].children:
            if child.index == index:
                child.active = True
            else:
                child.active = False
    
    def up_list(self,index):
        if index == 0:
            return True
        self.data[index-1], self.data[index] = self.data[index], self.data[index-1]
        self.refresh_view()
        self.makeTimePointChange()

    def down_list(self,index):
        if index == len(self.data)-1:
            return True
        self.data[index+1], self.data[index] = self.data[index], self.data[index+1]
        self.refresh_view()
        self.makeTimePointChange()

    def remove_selected(self):
        PiepMeConfirmPopup(message='Are you sure to delete the selected source?',
                            callback_ok=self.process_del_selected,
                            callback_cancel=lambda: True)

    def process_del_selected(self):
        temp = 0
        for child in self.children[0].children:
            if child.isCheckItem.active and child.active == False:
                temp = 1
                if self.data:
                    self.data.pop(child.index)
        if temp == 1:
            helper._write_schedule(self.clean_data_to_save_json())
            self.getTotalTime()
    
    def getTotalTime(self):
        tt = 0
        for item in self.data:
            tt += item['duration']
        self.total_time = helper.convertSecNoToHMS(tt)

    def makeTimePoint(self,index):
        helper.calc_schedule_runtime(index)
        self.set_data()
        self.refresh_view()

    def makeTimePointChange(self):
        idx = self.getCurrentIndex()
        if idx != -1:
            s = self.data[idx]['timepoint']
            for i, obj in enumerate(self.data):
                if i < idx:
                    self.data[i]['timepoint'] = 0
                if i > idx:
                    s += self.data[i-1]['duration']
                    self.data[i]['timepoint'] = s
        else:
            self.data = helper.calc_schedule_runtime(0,self.data)
        helper._write_schedule(self.clean_data_to_save_json())
        self.refresh_view()

    def refresh_view(self):
        try:
            for child in self.children[0].children:
                child.refresh_view_attrs(self,child.index, self.data[child.index])
        except:
            pass
    
    def link_audio(self, _parent, idx, src):
        _audio = LinkAudio(_parent,idx, src, self.link_audio_result)
        _audio.open()

    def link_audio_result(self,src, idx):
        self.data[idx]['audio'] = src
        helper._write_schedule(self.clean_data_to_save_json())
        self.refresh_view()