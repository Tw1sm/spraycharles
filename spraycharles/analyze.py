#!/usr/bin/env python3

import csv

import click
import numpy
from rich.console import Console
from rich.table import Table
from rich.theme import Theme

from .utils.notify import discord, slack, teams

# Defining theme
custom_theme = Theme(
    {
        "info": "blue",
        "good": "bold bright_green",
        "warning": "bold yellow",
        "danger": "bold bright_red",
    }
)

console = Console(theme=custom_theme)


class Analyzer:
    def __init__(self, resultsfile, notify, webhook, host, hit_count=0):
        self.resultsfile = resultsfile
        self.notify = notify
        self.webhook = webhook
        self.host = host
        self.hit_count = hit_count

    def analyze(self):
        try:
            with open(self.resultsfile, newline="") as resultsfile:
                print()
                console.print("[*] Reading spray data from CSV", style="info")
                reader = csv.reader(
                    resultsfile,
                    delimiter=",",
                )
                responses = list(reader)
        except Exception as e:
            console.print(
                f"[!] Error reading from file: {self.resultsfile}", style="danger"
            )
            print(e)
            exit()

        if responses[0][1] == "Message":
            return self.O365_analyze(responses)
        elif responses[0][2] == "SMB Login":
            return self.smb_analyze(responses)
        else:
            return self.http_analyze(responses)

    # Analyzes O365 and Okta
    def O365_analyze(self, responses):
        results = []
        for line in responses:
            results.append(line[0])
        success_indicies = list(
            filter(lambda x: results[x] == "Success", range(len(results)))
        )

        if len(success_indicies) > 0:
            console.print(
                "[+] Identified potentially sussessful logins!",
                style="good",
            )
            success_table = Table(show_footer=False, highlight=True)

            success_table.add_column("Username")
            success_table.add_column("Password")
            success_table.add_column("Message", justify="right")
            for x in success_indicies:
                success_table.add_row(
                    f"{responses[x][2]}", f"{responses[x][3]}", f"{responses[x][1]}"
                )

            console.print(success_table)

            self.send_notification(len(success_indicies))

            # Returning true to indicate a successfully guessed credential
            return len(success_indicies)
        else:
            console.print("[!] No successful logins", style="danger")

            return 0

    def http_analyze(self, responses):
        # remove header row from list
        del responses[0]

        len_with_timeouts = len(responses)

        # remove lines with timeouts
        responses = [line for line in responses if line[2] != "TIMEOUT"]
        timeouts = len_with_timeouts - len(responses)

        response_lengths = []
        # Get the response length column for analysis
        for indx, line in enumerate(responses):
            response_lengths.append(int(line[3]))

        console.print(
            "[*] Calculating mean and standard deviation of response lengths.",
            style="info",
        )

        # find outlying response lengths
        length_elements = numpy.array(response_lengths)
        length_mean = numpy.mean(length_elements, axis=0)
        length_sd = numpy.std(length_elements, axis=0)
        console.print("[*] Checking for outliers.", style="info")
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
            console.print(
                "[+] Identified potentially sussessful logins!\n", style="good"
            )

            success_table = Table(show_footer=False, highlight=True)

            success_table.add_column("Username")
            success_table.add_column("Password")
            success_table.add_column("Response Code", justify="right")
            success_table.add_column("Response Length", justify="right")
            for x in len_indicies:
                success_table.add_row(
                    f"{responses[x][0]}",
                    f"{responses[x][1]}",
                    f"{responses[x][2]}",
                    f"{responses[x][3]}",
                )

            console.print(success_table)

            self.send_notification(len(len_indicies))

            print()

            # Returning true to indicate a successfully guessed credential
            return len(len_indicies)
        else:
            console.print(
                "[!] No outliers found or not enough data to find statistical significance.",
                style="danger",
            )
            print()
            return 0

    # check for smb success not HTTP
    def smb_analyze(self, responses):
        successes = []
        positive_statuses = [
            "STATUS_SUCCESS",
            "STATUS_ACCOUNT_DISABLED",
            "STATUS_PASSWORD_EXPIRED",
            "STATUS_PASSWORD_MUST_CHANGE",
        ]
        for line in responses[1:]:
            if line[2] in positive_statuses:
                successes.append(line)

        if len(successes) > 0:
            console.print(
                "[+] Identified potentially sussessful logins!\n", style="good"
            )

            success_table = Table(show_footer=False, highlight=True)

            success_table.add_column("Username")
            success_table.add_column("Password")
            success_table.add_column("Status")
            for x in successes:
                success_table.add_row(f"{x[0]}", f"{x[1]}", f"{x[2]}")

            console.print(success_table)

            self.send_notification(len(successes))

            print()

            # Returning true to indicate a successfully guessed credential
            return len(successes)
        else:
            console.print("[!] No successful SMB logins", style="danger")
            print()
            return 0

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
                teams(self.webhook, self.host)


def main(file, notify, webhook, host):

    analyzer = Analyzer(file, notify, webhook, host)
    analyzer.analyze()


if __name__ == "__main__":
    main()
