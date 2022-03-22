import csv

import requests
from requests_ntlm import HttpNtlmAuth


class Ntlm:
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

    def set_password(self, password):
        self.data["password"] = password

    def login(self, username, password):
        self.set_username(username)
        self.set_password(password)
        ntlm_auth = HttpNtlmAuth(username, password)

        # post the request
        response = requests.post(
            self.url, headers=self.headers, auth=ntlm_auth, timeout=self.timeout
        )  # , verify=False, proxies=self.proxyDict)
        return response

    # handle CSV out output headers. Can be customized per module
    def print_headers(self, csvfile):
        # print table headers
        print(
            "%-35s %-17s %-13s %-15s"
            % ("Username", "Password", "Response Code", "Response Length")
        )
        print("-" * 83)

        # create CSV file
        output = open(csvfile, "w")
        fieldnames = ["Username", "Password", "Response Code", "Response Length"]
        output_writer = csv.DictWriter(output, delimiter=",", fieldnames=fieldnames)
        output_writer.writeheader()
        output.close()

    # handle target's response evaluation. Can be customized per module
    def print_response(self, response, csvfile, timeout=False):
        if timeout:
            code = "TIMEOUT"
            length = "TIMEOUT"
        else:
            code = response.status_code
            length = str(len(response.content))

        # print result to screen
        print(
            "%-35s %-17s %13s %15s"
            % (self.data["username"], self.data["password"], code, length)
        )

        # print to CSV file
        output = open(csvfile, "a")
        output.write(
            f'{self.data["username"]},{self.data["password"]},{code},{length}\n'
        )
        output.close()
