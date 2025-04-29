import requests

from .classes.BaseHttpTarget import BaseHttpTarget


class RDG(BaseHttpTarget):
    NAME = "RDG"
    DESCRIPTION = "Spray Microsoft Remote Desktop Gateway"

    def __init__(self, host, port, timeout, fireprox):
        self.timeout = timeout
        self.url = f"https://{host}:{port}/RDWeb/Pages/en-US/login.aspx"

        if fireprox:
            self.url = f"https://{fireprox}/fireprox/RDWeb/Pages/en-US/login.aspx"

        self.headers = {
            "Host": host,
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
            "Origin": f"https://{host}",
            "Content-Length": "0",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        self.data = {}

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
        domain = ""
        if "\\" in username:
            domain = username.split("\\")[0]
            username = username.split("\\")[1]
        body = 'DomainUserName={}%5C{}&UserPass={}'.format(domain, username, password) 
        self.headers['Content-Length'] = str(len(body))
        # post the request
        response = requests.post(
            self.url,
            headers=self.headers,
            data=body,
            timeout=self.timeout,
            verify=False,
        )  # , proxies=self.proxyDict)
        return response
