import requests


class Remoteaccess:

    import requests

    def __init__(self, host, timeout):
        self.timeout = timeout
        self.url = 'https://%s:443/RDWeb/Pages/en-US/login.aspx?ReturnUrl=default.aspx' % (host)

        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0", 
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 
            "Accept-Language": "en-US,en;q=0.5", 
            "Accept-Encoding": "gzip, deflate", 
            "Referer": "https://%s/RDWeb/Pages/en-US/login.aspx?ReturnUrl=default.aspx", 
            "Content-Type": "application/x-www-form-urlencoded", 
            "Connection": "close", 
            "Upgrade-Insecure-Requests": "1"
        }


        self.data = {
            "RDPCertificates": '', 
            "PublicModeTimeout": "20", 
            "PrivateModeTimeout": "240", 
            "isUtf8": "1", 
            "flags": "0", 
            "DomainUserName": "PCBG\\test", 
            "UserPass": "test", 
            "MachineType": "public"
        }

    
        # proxy settings
        self.http_proxy  = "http://127.0.0.1:8080"
        self.https_proxy = "http://127.0.0.1:8080"
        self.ftp_proxy   = "http://127.0.0.1:8080"

        self.proxyDict = { 
              "http"  : self.http_proxy, 
              "https" : self.https_proxy, 
              "ftp"   : self.ftp_proxy
        }
    

    def set_username(self, username):
        self.data['DomainUserName'] = username


    def set_password(self, password):
        self.data['UserPass'] = password


    def login(self, username, password):
        # set data
        self.set_username(username)
        self.set_password(password)
        # post the request
        response = requests.post(self.url, headers=self.headers, data=self.data, timeout=self.timeout, verify=False, proxies=self.proxyDict)
        return response


    #def check_success(self, response):
        #failure_url = 'reason=2'
        #if failure_url in response.url:
            #return False
        #else:
            #return True
