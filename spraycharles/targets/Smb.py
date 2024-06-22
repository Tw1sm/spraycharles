import json
import datetime
from impacket.smb import SMB_DIALECT
from impacket.smbconnection import SessionError, SMBConnection

from spraycharles.lib.logger import logger
from spraycharles.lib.utils import SMBStatus, SprayResult


class SMB:
    NAME = "SMB"
    DESCRIPTION = "Spray SMB services"

    #
    # Port, timeout and fireprox are dead args here. exist only to keep
    # formatting and logic from main spraycharles.py consistent with HTTP modules
    #
    def __init__(self, host, port, timeout, fireprox):
        self.host = host
        self.url = f"smb://{host}"
        self.conn = ""
        self.domain = ""
        self.hostname = ""
        self.os = ""
        self.smbv1 = True
        self.username = ""
        self.password = ""


    def get_conn(self):
        #
        # Try connecting with SMBv1 first
        #
        try:
            logger.debug(f"Attempting SMBv1 connection before SMBv3...")
            self.conn = SMBConnection(self.host, self.host, None, 445, preferredDialect=SMB_DIALECT, timeout=5)
        except Exception as e:
            logger.debug(f"Failed to connect with SMBv1: {str(e)}")
            self.smbv1 = False
            
            #
            # v1 failed, try with v3
            #
            try:
                logger.debug(f"Attempting SMBv3 connection...")
                self.conn = SMBConnection(self.host, self.host, None, 445)
            except Exception as e:
                logger.debug(f"Failed to connect with SMBv3: {str(e)}")
                return False

        #
        # Enumerate host info
        #
        try:
            self.conn.login("", "")
        except SessionError:
            pass

        self.domain = self.conn.getServerDNSDomainName()
        self.hostname = self.conn.getServerName()
        self.os = self.conn.getServerOS()
        return True


    def login(self, username, password):
        self.username = username
        self.password = password

        #
        # Split out domain and username if currently joined
        #
        domain = ""
        if "\\" in username:
            domain = username.split("\\")[0]
            username = username.split("\\")[1]

        #
        # Get new smb connection
        #
        if self.smbv1:
            self.conn = SMBConnection(self.host, self.host, None, 445, preferredDialect=SMB_DIALECT)
        else:
            self.conn = SMBConnection(self.host, self.host, None, 445)

        #
        # Send credentialed login request
        #
        try:
            self.conn.login(username, self.password, domain)
            self.conn.logoff()
            
            return SMBStatus.STATUS_SUCCESS.name
        except SessionError as e:
            
            if SMBStatus.STATUS_LOGON_FAILURE in str(e):
                return SMBStatus.STATUS_LOGON_FAILURE.name
            
            elif SMBStatus.STATUS_ACCOUNT_LOCKED_OUT in str(e):
                return SMBStatus.STATUS_ACCOUNT_LOCKED_OUT.name
            
            elif SMBStatus.STATUS_ACCOUNT_DISABLED in str(e):
                return SMBStatus.STATUS_ACCOUNT_DISABLED.name
            
            elif SMBStatus.STATUS_PASSWORD_EXPIRED in str(e):
                return SMBStatus.STATUS_PASSWORD_EXPIRED.name
            
            elif SMBStatus.STATUS_PASSWORD_MUST_CHANGE in str(e):
                return SMBStatus.STATUS_PASSWORD_MUST_CHANGE.name
            
            else:
                return str(e)


    # 
    # Print custom SMB module headers
    #
    def print_headers(self):
        # print table headers
        print("%-25s %-17s %-23s" % ("Username", "Password", "SMB Login"))
        print("-" * 68)


    # 
    # Print login attempt
    #
    def print_response(self, response, outfile, timeout=False):
        # print result to screen
        print("%-25s %-17s %-23s" % (self.username, self.password, response))
        self.log_attempt(response, outfile)    

    
    #
    # Log attempt as JSON object to file
    #
    def log_attempt(self, response, outfile):
        output = open(outfile, "a")
        output.write(
            json.dumps(
                {
                    SprayResult.TIMESTAMP   : datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M:%S"),
                    SprayResult.MODULE      : self.__class__.__name__,
                    SprayResult.USERNAME    : self.username,
                    SprayResult.PASSWORD    : self.password,
                    SprayResult.SMB_LOGIN   : response,
                }
            )
        )
        output.write("\n")
        output.close()
