import json
import numpy
from enum import Enum
from rich.table import Table

from spraycharles.lib.logger import console, logger
from spraycharles.lib.utils import discord, slack, teams, SMBStatus, SprayResult, HookSvc


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
        print()
        logger.debug(f"Opening results file: {self.resultsfile}")

        #
        # Output file isn't technically JSON compliant, but each line is a JSON object
        # So read each line and load into a list of JSON objects
        #
        with open(self.resultsfile, "r") as resultsfile:
            logger.info("Reading JSON spray result objects")
            responses = [json.loads(line) for line in resultsfile]
            
        #
        # Determine the type of service that was sprayed
        #
        match responses[0][SprayResult.MODULE]:
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

            success_table = Table(show_footer=False, highlight=True, title="Spray Hits", title_justify="left", title_style="bold reverse")

            success_table.add_column(SprayResult.USERNAME)
            success_table.add_column(SprayResult.PASSWORD)
            success_table.add_column(SprayResult.MESSAGE, justify="right")

            count = 0
            for resp in responses:
                if resp.get(SprayResult.RESULT) == "Success":
                    count += 1
                    success_table.add_row(
                        str(resp.get(SprayResult.USERNAME)),
                        str(resp.get(SprayResult.PASSWORD)),
                        str(resp.get(SprayResult.MESSAGE))
                    )

            console.print(success_table)

            self.send_notification(count)

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
        responses = [line for line in responses if line.get(SprayResult.RESPONSE_CODE) != "TIMEOUT"]

        response_lengths = []
        # Get the response length column for analysis
        for indx, line in enumerate(responses):
            response_lengths.append(int(line.get(SprayResult.RESPONSE_LENGTH)))

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

            success_table = Table(show_footer=False, highlight=True, title="Spray Hits", title_justify="left", title_style="bold reverse")

            success_table.add_column(SprayResult.USERNAME)
            success_table.add_column(SprayResult.PASSWORD)
            success_table.add_column(SprayResult.RESPONSE_CODE, justify="right")
            success_table.add_column(SprayResult.RESPONSE_LENGTH, justify="right")

            count = 0
            for resp in responses:
                if int(resp.get("Response Length")) in length_outliers:
                    count += 1
                    success_table.add_row(
                        str(resp.get(SprayResult.USERNAME)),
                        str(resp.get(SprayResult.PASSWORD)),
                        str(resp.get(SprayResult.RESPONSE_CODE)),
                        str(resp.get(SprayResult.RESPONSE_LENGTH))
                    )
                
            console.print(success_table)

            self.send_notification(count)

            print()

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
            if SMBStatus(result.get(SprayResult.SMB_LOGIN)) in positive_statuses:
                successes.append(result)

        if len(successes) > 0:
            logger.info("Identified potentially successful logins!")
            print()

            success_table = Table(show_footer=False, highlight=True, title="Spray Hits", title_justify="left", title_style="bold reverse")
            success_table.add_column(SprayResult.USERNAME)
            success_table.add_column(SprayResult.PASSWORD)
            success_table.add_column(SprayResult.SMB_LOGIN)

            for result in successes:
                success_table.add_row(
                    str(result.get(SprayResult.USERNAME)),
                    str(result.get(SprayResult.PASSWORD)),
                    str(result.get(SprayResult.SMB_LOGIN))
                )

            console.print(success_table)

            self.send_notification(len(successes))

            print()

            return len(successes)
        else:
            logger.info("No successful SMB logins")
            print()
            return 0

    #
    # Send notification to specified webhook
    #
    def send_notification(self, hit_total):
        
        # 
        # We'll only send notifications if NEW successes are found
        #
        if hit_total > self.hit_count:
            if self.notify:
                print()
                logger.info(f"Sending notification to {self.notify.value} webhook")

            match self.notify:
                case None:
                    pass
                case HookSvc.SLACK:
                    slack(self.webhook, self.host)
                case HookSvc.TEAMS:
                    teams(self.webhook, self.host)
                case HookSvc.DISCORD:
                    discord(self.webhook, self.host)
                case _:
                    logger.error("Invalid notification service specified")
