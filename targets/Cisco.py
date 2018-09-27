import requests


##############################
# ALPHA CODE - NEEDS TESTING #
##############################

class Cisco:

    def __init__(self, host):
        self.host = host
        self.url = 'https://%s/cgi/login' % (host)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'https://%s/vpn/index.html' % (host),
            'Connection': 'close', 'Upgrade-Insecure-Requests': '1',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        self.data = {
            'login': '',
            'passwd': ''
        }        

        #self.http_proxy  = 'http://127.0.0.1:8080'
        #self.https_proxy = 'http://127.0.0.1:8080'
        #self.ftp_proxy   = 'http://127.0.0.1:8080'

        #self.proxyDict = { 
              #'http'  : self.http_proxy, 
              #'https' : self.https_proxy, 
              #'ftp'   : self.ftp_proxy
        #}


    def set_username(self, username):
        self.data['login'] = username


    def set_password(self, password):
        self.data['passwd'] = password


    def login(self, username, password):
        # set data
        self.set_username(username)
        self.set_password(password)
        # post the request
        response = requests.post(self.url, headers=self.headers, data=self.data)
        return response


    def check_success(self, response):
        # if response url equals https://<host>/vpn/index.html still, login was failure
        if response.url == self.headers['Referer']:
            return False
        else:
            return True
