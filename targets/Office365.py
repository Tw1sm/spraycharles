import requests


class Office365:

    def __init__(self, port, host, timeout, fireprox):
        self.fireprox = fireprox
        self.timeout = timeout
        self.url = "https://login.microsoft.com"
        if(len(fireprox)!=0):
            self.url = "https://%s/fireprox" % (fireprox)
        self.url += "/common/oauth2/token"

        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Windows NT; Windows NT 10.0; en-US) WindowsPowerShell/5.1.17763.1007",
            "Expect": "100-continue",
            "Connection": "close"
        }

        self.data = {
            "resource": "https://graph.windows.net",
            "client_id": "1b730954-1685-4b74-9bfd-dac224a7b894",
            "client_info": "1",
            "grant_type": "password",
            "username": "",
            "password": "",
            "scope": "openid"
        }


    def set_username(self, username):
        self.data['username'] = username


    def set_password(self, password):
        self.data['password'] = password


    def login(self, username, password):
        # set data
        self.set_username(username)
        self.set_password(password)
        # post the request
        response = requests.post(self.url, headers=self.headers, data=self.data, timeout=self.timeout)#, verify=False, proxies=self.proxyDict)
        return response

    """
    def check_success(self, response):
        failure_url = 'reason=2'
        if failure_url in response.url:
            return False
        else:
            return True
    """

