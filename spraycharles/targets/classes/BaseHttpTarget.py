import json
import datetime

from spraycharles.lib.utils import SprayResult


class BaseHttpTarget:
    """
    Base class to hold output for standard HTTP spray targets
    """

    def __init__(self):
        self.username = ""
        self.password = ""


    # 
    # Print default module headers
    #
    def print_headers(self):
        print(
            "%-35s %-17s %-13s %-15s"
            % ("Username", "Password", "Response Code", "Response Length")
        )
        print("-" * 83)


    #
    # Print login attempt
    #
    def print_response(self, response, outfile, timeout=False):
        if timeout:
            code = "TIMEOUT"
            length = "TIMEOUT"
        else:
            code = response.status_code
            length = str(len(response.content))

        #
        # print result to screen and log to file
        #
        print("%-35s %-17s %13s %15s" % (self.username, self.password, code, length))
        self.log_attempt(code, length, outfile)

    
    #
    # Log attempt as JSON object to file
    #
    def log_attempt(self, code, length, outfile):
        output = open(outfile, "a")
        output.write(
            json.dumps(
                {
                    SprayResult.TIMESTAMP       : datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M:%S"),
                    SprayResult.MODULE          : self.__class__.__name__,
                    SprayResult.USERNAME        : self.username,
                    SprayResult.PASSWORD        : self.password,
                    SprayResult.RESPONSE_CODE   : code,
                    SprayResult.RESPONSE_LENGTH : length,
                }
            )
        )
        output.write("\n")
        output.close()