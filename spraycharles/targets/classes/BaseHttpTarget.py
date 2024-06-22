import json
import datetime

from spraycharles.lib.utils import SprayResult
from spraycharles.lib.logger import logger, JSON_FMT


class BaseHttpTarget:
    """
    Base class to hold output for standard HTTP spray targets
    """

    def __init__(self):
        self.username = ""
        self.password = ""


    #
    # Modules default to HTTPS, switch to HTTP if --no-ssl set
    #
    def set_plain_http(self):
        self.url = self.url.replace("https://", "http://", 1)


    # 
    # Print default module headers
    #
    def print_headers(self):
        header = ("%-35s %-25s %-13s %-15s" % (SprayResult.USERNAME, SprayResult.PASSWORD, SprayResult.RESPONSE_CODE, SprayResult.RESPONSE_LENGTH))
        print(header)
        print("-" * len(header))


    #
    # Print login attempt
    #
    def print_response(self, response, outfile, timeout=False, print_to_screen=True):
        if timeout:
            code = "TIMEOUT"
            length = "TIMEOUT"
        else:
            code = response.status_code
            length = str(len(response.content))

        if print_to_screen:
            print("%-35s %-25s %13s %15s" % (self.username, self.password, code, length))
        
        self.log_attempt(code, length, outfile)

    
    #
    # Log attempt as JSON object to file
    #
    def log_attempt(self, code, length, outfile):
        output = open(outfile, "a")
        data = json.dumps(
            {
                SprayResult.TIMESTAMP       : datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M:%S"),
                SprayResult.MODULE          : self.__class__.__name__,
                SprayResult.USERNAME        : self.username,
                SprayResult.PASSWORD        : self.password,
                SprayResult.RESPONSE_CODE   : code,
                SprayResult.RESPONSE_LENGTH : length,
            }
        )
        logger.debug(data, extra=JSON_FMT)
        output.write("\n")
        output.close()