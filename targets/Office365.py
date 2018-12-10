import requests


class Office365:

    def __init__(self, host, timeout):
        self.timeout = timeout
        self.url = "https://outlook.office365.com:/ews/Exchange.asmx"

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

    def login(self, username, password):
        # send get request
        response = requests.get(self.url, auth=(username,password))#, verify=False, proxies=self.proxyDict)
        return response