import requests
from requests_ntlm import HttpNtlmAuth

from .classes.BaseHttpTarget import BaseHttpTarget


class Ntlm(BaseHttpTarget):
    """Password spray NTLM over HTTP endpoints"""

    def __init__(self, host, port, timeout, path, fireprox):
        self.timeout = timeout
        self.url = f"https://{host}:{port}/{path}"

        if fireprox:
            self.url = f"https://{fireprox}/fireprox/{path}"

        self.headers = {
            "User-Agent": "AppleExchangeWebServices/814.80.3 accountsd/113",
            "Content-Type": "text/xml; charset=utf-8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }

        self.data = {"username": "", "password": ""}

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
        self.set_username(username)
        self.set_password(password)
        ntlm_auth = HttpNtlmAuth(username, password)

        # post the request
        response = requests.post(
            self.url, headers=self.headers, auth=ntlm_auth, timeout=self.timeout
        )  # , verify=False, proxies=self.proxyDict)
        return response
