import json
import datetime
from impacket.smb import SMB_DIALECT
from impacket.smbconnection import SessionError, SMBConnection

from spraycharles.utils.smbstatus import SMBStatus

class SMB:
    NAME = "SMB"
    DESCRIPTION = "Spray SMB services"

    smbv1 = True

    # port, timeout and fireprox are dead args here. exist only to keep
    # formatting and logic from main spraycharles.py consistent with HTTP modules
    def __init__(self, host, port, timeout, fireprox):
        self.host = host
        self.url = f"smb://{host}"
        conn = ""
        domain = ""
        hostname = ""
        os = ""
        # creds
        username = ""
        password = ""

    def get_conn(self):
        # Try connecting with SMBv1 first
        try:
            self.conn = SMBConnection(
                self.host, self.host, None, 445, preferredDialect=SMB_DIALECT
            )
        except Exception as e:
            # print(e)
            self.smbv1 = False
            # v1 failed, try with v3
            try:
                self.conn = SMBConnection(self.host, self.host, None, 445)
            except Exception as e:
                # print(e)
                # failed to get smb connection
                return False

        # enumerate host info
        try:
            self.conn.login("", "")
        except SessionError:
            pass

        self.domain = self.conn.getServerDNSDomainName()
        self.hostname = self.conn.getServerName()
        self.os = self.conn.getServerOS()
        return True

    def login(self, username, password):
        # set class attributes so they can be accessed in print_response()
        self.username = username
        self.password = password

        # split out domain and username if currently joined
        domain = ""
        if "\\" in username:
            domain = username.split("\\")[0]
            username = username.split("\\")[1]

        # get new smb connection
        if self.smbv1:
            self.conn = SMBConnection(
                self.host, self.host, None, 445, preferredDialect=SMB_DIALECT
            )
        else:
            self.conn = SMBConnection(self.host, self.host, None, 445)

        # login
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
                    "UTC Timestamp": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M:%S"),
                    "Module": self.__class__.__name__,
                    "Username": self.username,
                    "Password": self.password,
                    "SMB Login": response,
                }
            )
        )
        output.write("\n")
        output.close()
