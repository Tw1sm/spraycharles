import json
import numpy
from enum import Enum
from rich.table import Table

from spraycharles.lib.logger import console, logger
from spraycharles.utils.notify import discord, slack, teams
from spraycharles.utils.smbstatus import SMBStatus


class HookSvc(str, Enum):
    slack   = "Slack"
    teams   = "Teams"
    discord = "Discord"


class Analyzer:
    def __init__(self, resultsfile, notify, webhook, host, hit_count=0):
        self.resultsfile = resultsfile
        self.notify = notify
        self.webhook = webhook
        self.host = host
        self.hit_count = hit_count


    #
    # Run analysis over spray result file
    #
    def analyze(self):
        logger.debug(f"Opening results file: {self.resultsfile}")
        with open(self.resultsfile, "r") as resultsfile:
            print()
            logger.info("Reading JSON spray result objects")
            responses = [json.loads(line) for line in resultsfile]
            
        #
        # Determine the type of service that was sprayed
        #
        match responses[0]["Module"]:
            case "Office365":
                return self.O365_analyze(responses)
            case "SMB":
                return self.smb_analyze(responses)
            case _:
                return self.http_analyze(responses)

    # 
    # Analyzes O365 and Okta results
    #
    def O365_analyze(self, responses):
        results = []
        for line in responses:
            results.append(line.get("Result"))

        if "Success" in results:
            logger.info("Identified potentially successful logins!")
            print()

            success_table = Table(show_footer=False, highlight=True)

            success_table.add_column("Username")
            success_table.add_column("Password")
            success_table.add_column("Message", justify="right")

            count = 0
            for x in responses:
                if x.get("Result") == "Success":
                    count += 1
                    success_table.add_row(
                        f"{x.get('Username')}", f"{x.get('Password')}", f"{x.get('Message')}"
                    )

            console.print(success_table)

            self.send_notification(count)

            # Returning true to indicate a successfully guessed credential
            return count
        else:
            logger.info("No successful logins")
            print()
            return 0


    #
    # Standard HTTP module analysis
    #
    def http_analyze(self, responses):
        len_with_timeouts = len(responses)

        # remove lines with timeouts
        responses = [line for line in responses if line.get("Response Code") != "TIMEOUT"]
        timeouts = len_with_timeouts - len(responses)

        response_lengths = []
        # Get the response length column for analysis
        for indx, line in enumerate(responses):
            response_lengths.append(int(line.get("Response Length")))

        logger.info("Calculating mean and standard deviation of response lengths")

        # find outlying response lengths
        length_elements = numpy.array(response_lengths)
        length_mean = numpy.mean(length_elements, axis=0)
        length_sd = numpy.std(length_elements, axis=0)
        
        logger.info("Checking for outliers")
        
        length_outliers = [
            x
            for x in length_elements
            if (x > length_mean + 2 * length_sd or x < length_mean - 2 * length_sd)
        ]

        length_outliers = list(set(length_outliers))

        # print out logins with outlying response lengths
        if len(length_outliers) > 0:
            logger.info("Identified potentially successful logins!")
            print()

            success_table = Table(show_footer=False, highlight=True)

            success_table.add_column("Username")
            success_table.add_column("Password")
            success_table.add_column("Response Code", justify="right")
            success_table.add_column("Response Length", justify="right")

            count = 0
            for resp in responses:
                if int(resp.get("Response Length")) in length_outliers:
                    count += 1
                    success_table.add_row(
                        str(resp.get('Username')),
                        str(resp.get('Password')),
                        str(resp.get('Response Code')),
                        str(resp.get('Response Length'))
                    )
                
            console.print(success_table)

            self.send_notification(count)

            print()

            # Returning true to indicate a successfully guessed credential
            return count
        else:
            logger.info("No outliers found or not enough data to find statistical significance")
            print()
            return 0


    # 
    # Check for SMB successes against SMB status codes
    #
    def smb_analyze(self, responses):
        successes = []
        positive_statuses = [
            SMBStatus.STATUS_SUCCESS,
            SMBStatus.STATUS_ACCOUNT_DISABLED,
            SMBStatus.STATUS_PASSWORD_EXPIRED,
            SMBStatus.STATUS_PASSWORD_MUST_CHANGE,
        ]

        for result in responses:
            if SMBStatus(result.get("SMB Login")) in positive_statuses:
                successes.append(result)

        if len(successes) > 0:
            logger.info("Identified potentially successful logins!")
            print()

            success_table = Table(show_footer=False, highlight=True)
            success_table.add_column("Username")
            success_table.add_column("Password")
            success_table.add_column("Status")

            for result in successes:
                success_table.add_row(f"{result.get('Username')}", f"{result.get('Password')}", f"{result.get('SMB Login')}")

            console.print(success_table)

            self.send_notification(len(successes))

            print()

            # Returning true to indicate a successfully guessed credential
            return len(successes)
        else:
            logger.info("No successful SMB logins")
            print()
            return 0

    #
    # Send notification to specified webhook
    #
    def send_notification(self, hit_total):
        # we'll only send notifications if NEW successes are found
        if hit_total > self.hit_count:
            # Calling notifications if specified
            if self.notify:
                print()
                console.print(
                    f"[*] Sending notification to {self.notify} webhook", style="info"
                )

            if self.notify == "slack":
                slack(self.webhook, self.host)
            elif self.notify == "teams":
                teams(self.webhook, self.host)
            elif self.notify == "discord":
                discord(self.webhook, self.host)
