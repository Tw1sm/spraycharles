from impacket.smbconnection import SMBConnection, SessionError
from impacket.smb import SMB_DIALECT
import csv


class Smb:
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
            return "SUCCESS"
        except SessionError as e:
            if "STATUS_LOGON_FAILURE" in str(e):
                return "STATUS_LOGON_FAILURE"
            else:
                print(e)

    # handle CSV out output headers. Can be customized per module
    def print_headers(self, csvfile):

        # print table headers
        # print("%-25s %-17s %-23s" % ("Username", "Password", "SMB Login"))
        # print("-" * 68)

        smb_table = Table(highlight=True, min_width=61)
        smb_table.add_column("Username")
        smb_table.add_column("Password")
        smb_table.add_column("SMB Login", justify="right")

        # create CSV file
        output = open(csvfile, "w")
        fieldnames = ["Username", "Password", "SMB Login"]
        output_writer = csv.DictWriter(output, delimiter=",", fieldnames=fieldnames)
        output_writer.writeheader()
        output.close()
	
        return smb_table

    # handle target's response evaluation. Can be customized per module
    def print_response(self, response, csvfile, timeout=False):

        # print result to screen
        # print("%-25s %-17s %-23s" % (self.username, self.password, response))

        # print to CSV file
        output = open(csvfile, "a")
        output.write(f"{self.username},{self.password},{response}\n")
        output.close()

        return self.username, self.password, response
