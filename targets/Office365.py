import requests


class Office365:

    def __init__(self, host, timeout):
        self.timeout = timeout
        self.url = "https://%s:443" % (host)
        self.url += "/adfs/ls/?client-request-id=885ac48b-3289-49f5-a2a5-b02985aa8d02&username=&wa=wsignin1.0&wtrealm=urn%3afederation%3aMicrosoftOnline&wctx=estsredirect%3d2%26estsrequest%3drQIIAY2Rv2_TQACFe3FqaAdAwFoJIRaQnNw5Pp9tqYOdhoZAkqbKj8pLiB07sWv7XOdMkjIjFSFE544VLJkQEhKCBQmmTJ37FwATQkJiJBELY9_w6Y1P37vHoRzS7sB_EYUlBei6SLCdZfsvyfX1ay--mkfPxd8PTt-8vfts9jJzAm7YNEhDKx0FnpX0kmmOJoMZuD1kLB5p-TxNWUDpfo66rmc7BRnnbBrm6biX_wDAGQCzDJELMlFlEcmqrKiqSCQxh1Uiwr4KBRtaqiC5CAuWS2RBJgWRuA5W7T4-z1yt6ykbikvQxDt0fmXWXJqE3ZiO2An3dMtmVpHqg1LJ2E3aHVg0hFqdVUeVKfSresOnrBBNSNBtj-lwEhIa1-HuUJcrpY65v1fxjJ26rxtl0z_AD2tJeeoMpAOzVSxh-mhcbgZpo2uiqtt2mr0oTIXaYeBvIxbJhFW3lBl3IaPvOH5hI6TRnONp7ERe_ywLfmQz8MqfLDhdXfgWP_e_vLr82Hj_ff5a-bSxMl_Nd9RyH1cbUsH248m2tZc2ilajFU_uD9VmbQe7bGTHSgnq5pPWJtHQMQ-Oef4bD37y4OjSyse1C1xzvn5ThEgR0GI9voWwJikaIuZf0"


        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0", 
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 
            "Accept-Language": "en-US,en;q=0.5", 
            "Accept-Encoding": "gzip, deflate", 
            #"Referer": "https://fs.anham.com/adfs/ls/?&mkt=en-US&client-request-id=b8b0eed1-b46a-4889-a645-78ea738ce535&wa=wsignin1.0&wtrealm=urn%3afederation%3aMicrosoftOnline&wctx=estsredirect%3d2%26estsrequest%3drQIIAXVSO2_TYACMkza0FYIKkGDswARy8vmZh1SJNG7apLEdN04dW0KV40fsOH7E_hrHXmEAiaFi7MDQgaETQgwVM1NZCmN3JOiAEBMTIvkBLLfcSXe6u0c5rIBVH5IESamlQQWtqDSBkhUMoCqJ0yhBETSBA0ynABHeWVv_8vPd-ejDy92327Pr6NU36gy5b0EYRNViMY7jgm-atmYUNN8tniPIJYJ8R5DX2buqZaqhf-TYT1TPUt0Ff5JdNjy01z3LRjRBlyoUgeElgIO5M04WFHFssak2Y90e5JkDm0sAYCXFaotDQk5ZKOPCTBEbY1nUKFYUEk6SMXY0JHhxwcmA6wKg7HB2W2oCTupBbqeZyGmTmGsSlnGwq-xtvnYELXwBfminxu_squmH7mHgR_Ak9xXhA8Nr6nXf8wwNFhYyw4O2pkLb9zqhHxghtI1os9uy4dZkyLs4YTQEVKgP3FoIW3ulNg_4MmMq_Vak1SBpNrx6z-jjbJklp1ucZE-pmTPdZY8Oh_YYFzmpS5usOnNILRSlHanL1VIm4iKQ7IsYZLx-B-u0YKA3jDYZ68O6u9UqM2GwzfWtKK6VU9bppKOhqBiDJLX4_fpM3q2No0GrTUym7mQkOXzCvs_l5727vneRuzXP79n6RhD6pj02LpeQ66WbIFddWVlbzzzIbGT-LCGny_O5L398enYh_N17s108_fz8aeZiuRgLkG6AOt2NgxFsJnpZYmX3IGAGU9eX9JFgPZYnvDdwNE7exKvYcR45zud_5ZEXNzIfV_93lqu1e_OTlVEMRwG5gZFVEqtiuPIP0", 
            "Content-Type": "application/x-www-form-urlencoded", 
            "Connection": "close", 
            "Upgrade-Insecure-Requests": "1"
        }

        self.data = {
            "UserName": "", 
            "Password": "", 
            "AuthMethod": "FormsAuthentication"
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
        self.data['UserName'] = username


    def set_password(self, password):
        self.data['Password'] = password


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

"""
burp0_url = "https://fs.anham.com:443/adfs/ls/?&mkt=en-US&client-request-id=b8b0eed1-b46a-4889-a645-78ea738ce535&wa=wsignin1.0&wtrealm=urn%3afederation%3aMicrosoftOnline&wctx=estsredirect%3d2%26estsrequest%3drQIIAXVSO2_TYACMkza0FYIKkGDswARy8vmZh1SJNG7apLEdN04dW0KV40fsOH7E_hrHXmEAiaFi7MDQgaETQgwVM1NZCmN3JOiAEBMTIvkBLLfcSXe6u0c5rIBVH5IESamlQQWtqDSBkhUMoCqJ0yhBETSBA0ynABHeWVv_8vPd-ejDy92327Pr6NU36gy5b0EYRNViMY7jgm-atmYUNN8tniPIJYJ8R5DX2buqZaqhf-TYT1TPUt0Ff5JdNjy01z3LRjRBlyoUgeElgIO5M04WFHFssak2Y90e5JkDm0sAYCXFaotDQk5ZKOPCTBEbY1nUKFYUEk6SMXY0JHhxwcmA6wKg7HB2W2oCTupBbqeZyGmTmGsSlnGwq-xtvnYELXwBfminxu_squmH7mHgR_Ak9xXhA8Nr6nXf8wwNFhYyw4O2pkLb9zqhHxghtI1os9uy4dZkyLs4YTQEVKgP3FoIW3ulNg_4MmMq_Vak1SBpNrx6z-jjbJklp1ucZE-pmTPdZY8Oh_YYFzmpS5usOnNILRSlHanL1VIm4iKQ7IsYZLx-B-u0YKA3jDYZ68O6u9UqM2GwzfWtKK6VU9bppKOhqBiDJLX4_fpM3q2No0GrTUym7mQkOXzCvs_l5727vneRuzXP79n6RhD6pj02LpeQ66WbIFddWVlbzzzIbGT-LCGny_O5L398enYh_N17s108_fz8aeZiuRgLkG6AOt2NgxFsJnpZYmX3IGAGU9eX9JFgPZYnvDdwNE7exKvYcR45zud_5ZEXNzIfV_93lqu1e_OTlVEMRwG5gZFVEqtiuPIP0"
burp0_headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0", 
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 
    "Accept-Language": "en-US,en;q=0.5", 
    "Accept-Encoding": "gzip, deflate", 
    "Referer": "https://fs.anham.com/adfs/ls/?&mkt=en-US&client-request-id=b8b0eed1-b46a-4889-a645-78ea738ce535&wa=wsignin1.0&wtrealm=urn%3afederation%3aMicrosoftOnline&wctx=estsredirect%3d2%26estsrequest%3drQIIAXVSO2_TYACMkza0FYIKkGDswARy8vmZh1SJNG7apLEdN04dW0KV40fsOH7E_hrHXmEAiaFi7MDQgaETQgwVM1NZCmN3JOiAEBMTIvkBLLfcSXe6u0c5rIBVH5IESamlQQWtqDSBkhUMoCqJ0yhBETSBA0ynABHeWVv_8vPd-ejDy92327Pr6NU36gy5b0EYRNViMY7jgm-atmYUNN8tniPIJYJ8R5DX2buqZaqhf-TYT1TPUt0Ff5JdNjy01z3LRjRBlyoUgeElgIO5M04WFHFssak2Y90e5JkDm0sAYCXFaotDQk5ZKOPCTBEbY1nUKFYUEk6SMXY0JHhxwcmA6wKg7HB2W2oCTupBbqeZyGmTmGsSlnGwq-xtvnYELXwBfminxu_squmH7mHgR_Ak9xXhA8Nr6nXf8wwNFhYyw4O2pkLb9zqhHxghtI1os9uy4dZkyLs4YTQEVKgP3FoIW3ulNg_4MmMq_Vak1SBpNrx6z-jjbJklp1ucZE-pmTPdZY8Oh_YYFzmpS5usOnNILRSlHanL1VIm4iKQ7IsYZLx-B-u0YKA3jDYZ68O6u9UqM2GwzfWtKK6VU9bppKOhqBiDJLX4_fpM3q2No0GrTUym7mQkOXzCvs_l5727vneRuzXP79n6RhD6pj02LpeQ66WbIFddWVlbzzzIbGT-LCGny_O5L398enYh_N17s108_fz8aeZiuRgLkG6AOt2NgxFsJnpZYmX3IGAGU9eX9JFgPZYnvDdwNE7exKvYcR45zud_5ZEXNzIfV_93lqu1e_OTlVEMRwG5gZFVEqtiuPIP0", 
    "Content-Type": "application/x-www-form-urlencoded", 
    "Connection": "close", 
    "Upgrade-Insecure-Requests": "1"
}
burp0_data = {
    "UserName": "test@test.com", 
    "Password": "test", 
    "AuthMethod": "FormsAuthentication"
}
requests.post(burp0_url, headers=burp0_headers, data=burp0_data)

import requests
l
burp0_url = "https://adfs.columbuslibrary.org:443/adfs/ls/?client-request-id=885ac48b-3289-49f5-a2a5-b02985aa8d02&username=&wa=wsignin1.0&wtrealm=urn%3afederation%3aMicrosoftOnline&wctx=estsredirect%3d2%26estsrequest%3drQIIAY2Rv2_TQACFe3FqaAdAwFoJIRaQnNw5Pp9tqYOdhoZAkqbKj8pLiB07sWv7XOdMkjIjFSFE544VLJkQEhKCBQmmTJ37FwATQkJiJBELY9_w6Y1P37vHoRzS7sB_EYUlBei6SLCdZfsvyfX1ay--mkfPxd8PTt-8vfts9jJzAm7YNEhDKx0FnpX0kmmOJoMZuD1kLB5p-TxNWUDpfo66rmc7BRnnbBrm6biX_wDAGQCzDJELMlFlEcmqrKiqSCQxh1Uiwr4KBRtaqiC5CAuWS2RBJgWRuA5W7T4-z1yt6ykbikvQxDt0fmXWXJqE3ZiO2An3dMtmVpHqg1LJ2E3aHVg0hFqdVUeVKfSresOnrBBNSNBtj-lwEhIa1-HuUJcrpY65v1fxjJ26rxtl0z_AD2tJeeoMpAOzVSxh-mhcbgZpo2uiqtt2mr0oTIXaYeBvIxbJhFW3lBl3IaPvOH5hI6TRnONp7ERe_ywLfmQz8MqfLDhdXfgWP_e_vLr82Hj_ff5a-bSxMl_Nd9RyH1cbUsH248m2tZc2ilajFU_uD9VmbQe7bGTHSgnq5pPWJtHQMQ-Oef4bD37y4OjSyse1C1xzvn5ThEgR0GI9voWwJikaIuZf0"
burp0_headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0", 
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 
    "Accept-Language": "en-US,en;q=0.5", 
    "Accept-Encoding": "gzip, deflate", 
    "Referer": "https://adfs.columbuslibrary.org/adfs/ls/?client-request-id=885ac48b-3289-49f5-a2a5-b02985aa8d02&username=&wa=wsignin1.0&wtrealm=urn%3afederation%3aMicrosoftOnline&wctx=estsredirect%3d2%26estsrequest%3drQIIAY2Rv2_TQACFe3FqaAdAwFoJIRaQnNw5Pp9tqYOdhoZAkqbKj8pLiB07sWv7XOdMkjIjFSFE544VLJkQEhKCBQmmTJ37FwATQkJiJBELY9_w6Y1P37vHoRzS7sB_EYUlBei6SLCdZfsvyfX1ay--mkfPxd8PTt-8vfts9jJzAm7YNEhDKx0FnpX0kmmOJoMZuD1kLB5p-TxNWUDpfo66rmc7BRnnbBrm6biX_wDAGQCzDJELMlFlEcmqrKiqSCQxh1Uiwr4KBRtaqiC5CAuWS2RBJgWRuA5W7T4-z1yt6ykbikvQxDt0fmXWXJqE3ZiO2An3dMtmVpHqg1LJ2E3aHVg0hFqdVUeVKfSresOnrBBNSNBtj-lwEhIa1-HuUJcrpY65v1fxjJ26rxtl0z_AD2tJeeoMpAOzVSxh-mhcbgZpo2uiqtt2mr0oTIXaYeBvIxbJhFW3lBl3IaPvOH5hI6TRnONp7ERe_ywLfmQz8MqfLDhdXfgWP_e_vLr82Hj_ff5a-bSxMl_Nd9RyH1cbUsH248m2tZc2ilajFU_uD9VmbQe7bGTHSgnq5pPWJtHQMQ-Oef4bD37y4OjSyse1C1xzvn5ThEgR0GI9voWwJikaIuZf0", 
    "Content-Type": "application/x-www-form-urlencoded", 
    "Connection": "close", 
    "Upgrade-Insecure-Requests": "1"
}
burp0_data = {
    "UserName": "test@test.com", 
    "Password": "test", 
    "AuthMethod": "FormsAuthentication"
    }
requests.post(burp0_url, headers=burp0_headers, data=burp0_data)
"""