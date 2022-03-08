import requests
import csv


class Openvpn:
    def __init__(self, host, port, timeout, fireprox):
        self.timeout = timeout
        self.url = f"https://{host}:{port}/__auth__"

        if fireprox:
            self.url = f"https://{fireprox}/fireprox/__auth__"

        self.cookies = {
            "openvpn_sess_b10a2c812557be001dccfdf23467a807": "5111ef7adc760bcd6455f326bda7cac8"
        }

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Accept": "text/plain, */*; q=0.01",
            "X-Openvpn": "1",
            "X-Requested-With": "XMLHttpRequest",
            "X-Cws-Proto-Ver": "2",
            "Referer": f"https://{host}:{port}/?src=connect",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Connection": "close",
        }
        self.data = {"username": "", "password": ""}

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
        self.data["username"] = username

    def set_password(self, password):
        self.data["password"] = password

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
