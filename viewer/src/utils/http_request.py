from urllib.request import Request, urlopen
from urllib import parse
import json
import sys
from src.utils import scryto


class HTTP_REQUEST():
    """-------------------------------------------------------------------------------------------------------------------------
                                                         HTTP MODEL
    -------------------------------------------------------------------------------------------------------------------------"""

    def __init__(self):
        self.PIEPME_HOST = 'https://webservice.piepme.com'

    def _get(self, path, param):
        return self.http_request(path, param, 'GET')

    def _post(self, path, param):
        return self.http_request(path, param, 'POST')

    def _put(self, path, param):
        return self.http_request(path, param, 'PUT')

    def _delete(self, path, param):
        return self.http_request(path, param, 'DELETE')

    def _patch(self, path, param):
        return self.http_request(path, param, 'PATCH')

    def http_request(self, path, param, method):
        """-------------------------------------------------------------------------------------------------------------------------
                                                        HTTP_REQUEST
        -------------------------------------------------------------------------------------------------------------------------"""
        """ ROOT request method """
        #1. calc url from path
        url = self.PIEPME_HOST + path
        #2. add some param
        param['SRC'] = 'WEB'
        #3. add token
        param['token'] = scryto.createTokenV3(param)
        #4. del secret param
        del param['keyToken']
        del param['v']
        #5. buid query string
        if method is 'GET':
            url += '?' + self.querystring(param)
        #6. calc post data
        data = parse.urlencode({} if method is 'GET' else param).encode(
            'utf-8')
        #7. mk request
        req = Request(url, data=data, method=method)
        req.add_header("Accept", "application/json")
        print(f'>>>>>>>>>>REQUEST -> method={method}, url={url}, data={data}')
        #8. receive RESPONSE
        with urlopen(req) as response:
            json_str = response.read().decode("utf-8")
            data_json = json.loads(json_str)
            print(
                f'>>>>>>>>>>RESPONSE -> status={data_json["status"]}, len={len(json_str)}'
            )
            return data_json

    def querystring(self, param):
        """ mk query string for GET method """
        sorted_key = sorted(param)
        maped_ls = map(lambda v: f'{v}={parse.quote(str(param[v]))}',
                       sorted_key)
        return '&'.join(list(maped_ls))
