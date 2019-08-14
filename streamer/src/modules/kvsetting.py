import kivy, cv2
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, NumericProperty, BooleanProperty, StringProperty
from kivy.uix.popup import Popup
from src.modules.custom.filechoose import FileChooser
from src.utils import ftype, helper, scryto
from kivy.uix.recycleview import RecycleView
from src.modules.recyclelayout.recyclegridlayout import SelectableBox
from kivy.uix.recycleview.views import RecycleDataViewBehavior

Builder.load_file('src/ui/kvsetting.kv')

class KVSetting(Popup):
    rcv_stream = ObjectProperty()
    stream_server = ObjectProperty()
    stream_key = ObjectProperty()
    callback = ObjectProperty()

    def __init__(self, parent):
        super(KVSetting, self).__init__()
        self.f_parent = parent
        self.lsStream = []
        self.stream_server.text = parent.streamServer
        self.stream_key.text = parent.streamKey
        self.rcv_stream.set_parent(self)
        self.rcv_stream.set_data()

    def on_ok(self):
        try:
            if len(self.stream_server.text) > 0 and len(self.stream_key.text) > 0:
                self.f_parent.save_setting(self.stream_server.text,self.stream_key.text)
                self.dismiss()
        except:
            pass
            
    def on_remove(self):
        self.dismiss()

    def on_cancel(self):
        self.dismiss()

    def getLink(self,data):
        self.stream_server.text = data['key_a']
        self.stream_key.text = data['key_b']


class ListStream(RecycleView):
    list_source = ObjectProperty()
    item_playing = ''

    def __init__(self, **kwargs):
        super(ListStream, self).__init__(**kwargs)
        self.data = []

    def set_parent(self,_parent):
        self.f_parent = _parent

    def set_data(self):
        self.data = list(
            map(
                lambda item: {'id': item['id'],'label': item['label'], 'key_a': item['key_a'], 'key_b': item['key_b'],
                'active': (False,True) [item['id'] == self.item_playing]},
                helper._load_ls_key()
            )
        )
        
    def set_source(self,sources):
        self.data = sources

    def getIndexOfSeleced(self):
        for child in self.children[0].children:
            if child.active:
                return child.index
        return -1
    
    def set_active(self,index):
        self.item_playing = self.data[index]['id']
        for obj in self.data:
            obj['active'] = False
        self.data[index]['active'] = True
        for child in self.children[0].children:
            if child.index == index:
                child.active = True
            else:
                child.active = False
        if self.f_parent is not None:
            self.f_parent.getLink(self.data[index])
        

class BoxAudio(SelectableBox):
    """ Adds selection and focus behaviour to the view. """
    selected_source = StringProperty()


class RCVStream(RecycleDataViewBehavior, BoxLayout):
    index = NumericProperty(0)
    name = StringProperty()
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    active = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.name = data['label']
        self.active = data['active']
        return super(RCVStream, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if super(RCVStream, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected

    def set_active(self):
        self.parent.parent.set_active(self.index)