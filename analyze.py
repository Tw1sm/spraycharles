#!/usr/bin/env python3

import csv
import numpy
import click
from texttable import Texttable
from utils.notify import slack, teams, discord


# Defining colors for later use
class Color:
    green = "\033[92m"
    yellow = "\033[93m"
    blue = "\033[94m"
    red = "\033[91m"
    grey = "\033[37m"
    end = "\033[0m"

    def color_print(self, string, color, end="\n"):
        print(color + string + self.end, end=end)


class Analyzer:

    def __init__(self, resultsfile, notify, webhook, host):
        self.resultsfile = resultsfile
        self.notify = notify
        self.webhook = webhook
        self.host = host
        self.colors = Color()

    # Performs basic reading a parsing for output csv file
    def analyze(self):
        try:
            with open(self.resultsfile, newline="") as resultsfile:
                print()
                print("[*] Reading spray data from CSV...")
                reader = csv.reader(
                    resultsfile,
                    delimiter=",",
                )
                responses = list(reader)

        except Exception as e:
            self.colors.color_print(
                "[!] Error reading from file: %s" % (self.resultsfile), self.colors.red
            )
            print(e)
            exit()

        # Calling analyze function based on responses content returned above
        if responses[0][1] == "Message":
            success = self.O365_analyze(responses)
            return success

        elif responses[0][2] == "SMB Login":
            success = self.smb_analyze(responses)
            return success

        else:
            success = self.http_analyze(responses)
            return success

        print()

    def O365_analyze(self, responses):
        results = []
        for line in responses:
            results.append(line[0])

        success_indicies = list(
            filter(lambda x: results[x] == "Success", range(len(results)))
        )

        # print out logins with outlying response lengths
        if len(success_indicies) > 0:
            self.colors.color_print(
                "[+] Identified potential sussessful logins!\n", self.colors.green
            )
            table = Texttable(0)
            table.header(["Username", "Password", "Message"])
            for x in success_indicies:
                table.add_row([responses[x][2], responses[x][3], responses[x][1]])

            # Calling notifications if specified
            if self.notify == "slack":
                slack(self.webhook, self.host)
            elif self.notify == "teams":
                teams(self.webhook, self.host)
            elif self.notify == "discord":
                teams(self.webhook, self.host)

            print(table.draw())

            # Returning true to indicate a successfully guessed credential
            return True

        else:
            self.colors.color_print(
                "[-] No successful Office365 logins", self.colors.red
            )

    def http_analyze(self, responses):

        # Remove header row from list
        del responses[0]

        len_with_timeouts = len(responses)

        # remove lines with timeouts
        responses = [line for line in responses if line[2] != "TIMEOUT"]
        timeouts = len_with_timeouts - len(responses)

        response_lengths = []

        # Get the response length column for analysis
        for indx, line in enumerate(responses):
            response_lengths.append(int(line[3]))

        print("[*] Calculating mean and standard deviation of response lengths...")

        # find outlying response lengths
        length_elements = numpy.array(response_lengths)
        length_mean = numpy.mean(length_elements, axis=0)
        length_sd = numpy.std(length_elements, axis=0)
        print("[*] Checking for outliers...")
        length_outliers = [
            x
            for x in length_elements
            if (x > length_mean + 2 * length_sd or x < length_mean - 2 * length_sd)
        ]

        length_outliers = list(set(length_outliers))
        len_indicies = []

        # find username / password combos with matching response lengths
        for hit in length_outliers:
            len_indicies += [i for i, x in enumerate(responses) if x[3] == str(hit)]

        # print out logins with outlying response lengths
        if len(len_indicies) > 0:
            self.colors.color_print(
                "[+] Identified potential sussessful logins!\n", self.colors.green
            )
            table = Texttable(0)
            table.header(["Username", "Password", "Resp Code", "Resp Length"])
            for x in len_indicies:
                table.add_row(
                    [responses[x][0], responses[x][1], responses[x][2], responses[x][3]]
                )

            # Calling notifications if specified
            if self.notify == "slack":
                slack(self.webhook, self.host)
            elif self.notify == "teams":
                teams(self.webhook, self.host)
            elif self.notify == "discord":
                teams(self.webhook, self.host)

            print(table.draw())

            # Returning true to indicate a successfully guessed credential
            return True

        else:
            self.colors.color_print(
                "[-] No outliers found or not enough data to find statistical significance",
                self.colors.red,
            )

    # check for smb success not HTTP
    def smb_analyze(self, responses):
        successes = []
        for line in responses[1:]:
            if line[2] != "STATUS_LOGON_FAILURE":
                successes.append(line)

        if len(successes) > 0:
            self.colors.color_print(
                "[+] Identified sussessful SMB logins!\n", self.colors.green
            )
            table = Texttable(0)
            table.header(["Username", "Password"])
            for x in successes:
                table.add_row([x[0], x[1]])

            # Calling notifications if specified
            if self.notify == "slack":
                slack(self.webhook, self.host)
            elif self.notify == "teams":
                teams(self.webhook, self.host)
            elif self.notify == "discord":
                teams(self.webhook, self.host)

            print(table.draw())

            # Returning true to indicate a successfully guessed credential
            return True

        else:
            self.colors.color_print("[-] No successful SMB logins", self.colors.red)


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
@click.command(no_args_is_help=True, context_settings=CONTEXT_SETTINGS)
@click.argument("file", type=str, required=True)
@click.option(
    "-n",
    "--notify",
    required=False,
    type=click.Choice(["teams", "slack", "discord"]),
    help="Enable notifications for Slack, MS Teams or Discord.",
)

@click.option(
    "-w",
    "--webhook",
    required=False,
    type=str,
    default=False,
    help="Webhook used for specified   notification module",
)

@click.option(
    "-H",
    "--host",
    required=False,
    type=str,
    default=False,
    help="Target host associated with CSV file",
)

def main(file, notify, webhook, host):

    analyzer = Analyzer(file, notify, webhook, host)
    analyzer.analyze()


if __name__ == "__main__":
    main()
