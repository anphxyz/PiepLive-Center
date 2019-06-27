import socketio
import platform
import asyncio
from src.utils import helper, store, timeloop
import os
from datetime import datetime
import json


# https://nodeinfo.piepme.com/
SOCKET_SERVER = 'https://nodeinfodev.piepme.com:444/'
"""---------------------------------------------------------------------
                                SOCKET
---------------------------------------------------------------------"""

sio = socketio.AsyncClient(reconnection=True)


class LoginListener(socketio.AsyncClientNamespace):
    fpath = 'src/modules/login/code.png'

    async def on_connect(self):
        token = self.create_login_token(sio.eio.sid)
        print('Connected:', sio.eio.sid, token)
        helper.generate_qr(token, self.fpath)

        # self.after(1000, self.renew_qr)
        timeloop.timeout(self.renew_qr, 1000)

        await sio.emit('webClientJoin', data={"token": token})

        # async def my_background_task(my_argument)
        #     # do some background work here!
        #     pass

        # sio.start_background_task(my_background_task, 123)

    # update with timeout -> UI

    def renew_qr(self):
        pass
        # helper.getApRoot().login_popup.qr_login = self.fpath

    async def on_webClientRecieve(self, json_str):
        data = json.loads(json_str)
        if data['status'] == 'success':
            store._new(data['elements'])
            # rmv qr
            os.remove("src/images/login.png")
            await sio.disconnect()

    async def on_disconnect(self):
        print('Disconnected!')

    def create_login_token(self, socketID):
        token = socketID
        token += '##qb##'
        token += f'{platform.system()} {platform.release()} - PiepLive Center'
        return helper.stringToBase64(token)


#
sio.register_namespace(LoginListener('/'))


#
def open():
    async def start():
        await sio.connect(SOCKET_SERVER)
        await sio.wait()

    asyncio.run(start(), debug=True)
