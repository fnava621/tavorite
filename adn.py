""" 
   Python Library that wraps the alpha ADN API. 
   Aims to abstract away all the API endpoints

   I love talking to people. If you have any questions or comments: fnava621@gmail.com or @nava

"""

__author__  = "Fernando Nava <fnava621@gmail.com>"
__version__ = "0.1"


import requests
import json
import re

from adn_endpoints import api_table, base_url


class Adn:
    
    def __init__(self,client_id=None, client_secret=None, redirect_uri=None, access_token=None, scope=['stream', 'email', 'write_post', 'follow', 'messages', 'export']):

        self.client_id         = client_id
        self.client_secret     = client_secret
        self.redirect_uri      = redirect_uri
        self.access_token      = access_token
        self.api_anchor        = 'https://alpha.app.net/%s'
        self.accepted_scope    = ['stream', 'email', 'write_post', 'follow', 'messages', 'export']
        self.scope             = ' '.join([type_scope for type_scope in scope if type_scope in self.accepted_scope])
        self.auth_url          = self.getAuthUrl()
        self.request_token_url = self.api_anchor % 'oauth/access_token'
        self.client            = requests.session()

        def setFunc(key):
            return lambda **kwargs: self._constructFunc(key, **kwargs)
        
        for key in api_table.keys():
            self.__dict__[key] = setFunc(key)



    def _constructFunc(self, api_call, **kwargs):
        # Go through and replace any mustaches that are in our API url.
        fn = api_table[api_call]
        url = re.sub(
            '\{\{(?P<m>[a-zA-Z_]+)\}\}',
            lambda m: "%s" % kwargs.get(m.group(1)),
            base_url + fn['url']
        )

        content = self._request(url, method=fn['method'], params=kwargs)

        return content

    def _request(self, url, method='GET', params=None, files=None, api_call=None):

        method = method.lower()
        if not method in ('get', 'post', 'delete'):
            return "ERROR: NOT CORRECT METHOD"

        params = params or {}

        func = getattr(self.client, method)
        
        url = url + "?access_token=" + self.access_token

        if method == 'get' or method == 'delete':
            response = func(url, params=params)
        else:
            response = func(url, data=params, files=files)
        content = response.content.decode('utf-8')

        # create stash for last function intel
        self._last_call = {
            'api_call': api_call,
            'api_error': None,
            'cookies': response.cookies,
            'error': response.error,
            'headers': response.headers,
            'status_code': response.status_code,
            'url': response.url,
            'content': content,
        }

        content = json.loads(content)

        return content



    def getAuthUrl(self):
        if self.client_id and self.redirect_uri:
            url = self.api_anchor % "/oauth/authenticate?client_id="+\
                   self.client_id + "&response_type=code&redirect_uri=" +\
                   self.redirect_uri + "&scope=" + self.scope
            url_encoded = url.replace(' ', '%20')

            return url_encoded
        else:
           return "ERROR: Need client_id and redirect_uri to generate Authenticate Url"

    def getAccessToken(self, code):
        post_data = {'client_id': self.client_id,
                     'client_secret': self.client_secret,
                     'grant_type': 'authorization_code',
                     'redirect_uri': self.redirect_uri,
                     'code': code}

        get_access_token = requests.post(self.request_token_url, data=post_data)
        
        if get_access_token.ok:
            access_token_info = json.loads(get_access_token.text)
            self.access_token = access_token_info['access_token']
            return self.access_token
        elif self.access_token:
            return self.access_token
        else:
            return "ERROR: Attempt to get AccessToken Failed - Try Again"
        


    def getClientToken(self):
        if self.client_id and self.client_secret:
            url = self.request_token_url + "&scope=" + self.scope
            post_data = {'client_id': self.client_id,
                        'client_secret': self.client_secret,
                        'grant_type': 'client_credentials'}
            r = requests.post(self.request_token_url, data=post_data)
            token = json.loads(r.text)
            return token['access_token']


def bug(code):
    post_data = {'client_id': os.environ.get('CLIENT_ID'),
                     'client_secret': os.environ.get('CLIENT_SECRET'),
                     'grant_type': 'authorization_code',
                     'redirect_uri': os.environ.get('REDIRECT_URL'),
                     'code': code}
    url = 'https://alpha.app.net/oauth/access_token'
    
    r = requests.post(url, data=post_data)
    return r
