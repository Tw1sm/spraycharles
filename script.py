#!/usr/bin/env python

import time
import argparse
import csv
import datetime
import json
import os
import sys
from targets import *

def args():
    parser = argparse.ArgumentParser(description="Python based script for password spraying with selenium and headless chrome", formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-p", "--passwords", type=str, dest="passlist", help="filepath of the passwords list", default="./passwords.txt", required=False)
    parser.add_argument("-t", "--target-host", type=str, dest="host", help="host to password spray", required=True)
    parser.add_argument("-m", "--module", type=str, dest="module", help="module corresponding to target host", required=True)
    parser.add_argument("-u", "--usernames", type=str, dest="userlist", help="filepath of the usernames list", required=True)
    parser.add_argument("-o", "--output", type=str, dest="csvfile", help="name and path of output csv where hits will be logged", required=False)
    parser.add_argument("-a", "--attempts", type=int, dest="attempts", help="number of logins submissions per interval (for each user)", required=False)
    parser.add_argument("-i", "--interval", type=int, dest="interval", help="minutes inbetween login intervals", required=False)
    parser.add_argument("-e", "--equal", action="store_true", dest="equal", help="does 1 spray for each user where password = username", required=False)

    args = parser.parse_args()
    userlist, passlist, attempts, interval = args.userlist, args.passlist, args.attempts, args.interval

    # get usernames from file
    try:
        with open(userlist, 'r') as f:
            users = f.read().splitlines()
    except Exception:
        print('[!] Error reading usernames from file: ' + userlist)
        exit()

    #  get passwords from file
    try:
        with open(passlist, 'r') as f:
            passwords = f.read().splitlines()
    except Exception:
        print('[!] Error reading passwords from file: ' + passlist)
        exit()


    if interval and not attempts:
        print('[!] Number of login attempts per interval (-a) required with -i')
        exit()
    elif not interval and attempts:
        print('[!] Minutes per interval (-i) required with -a')
        exit()

    return users, passwords, args.host, args.csvfile, attempts, interval, args.equal, args.module


def print_response(res):
    print('HTTP/1.1 {status_code}\n{headers}\n\n{body}'.format(
        status_code=res.status_code,
        headers='\n'.join('{}: {}'.format(k, v) for k, v in res.headers.items()),
        body=res.content,
    ))


def main():
    users, passwords, host, csvfile, attempts, interval, equal, module = args()
    
    # try to instantiate the specified module
    try:
        module = module.title()
        mod_name = getattr(sys.modules[__name__], module)
        class_name = getattr(mod_name, module)
        target = class_name(host)
    except AttributeError:
        print('[!] Error loading %s module. %s is spelled incorrectly or does not exist') % (module, module)
        exit()

    #for password in passwords:

        #for username in users:
            #response =target.login(username, password)
            #print('User: %s Pass: %s Text Length: %d Content Length %d') % (username,password,len(response.text),len(response.content)) 

    r = target.login('target1','pass')
    print_response(r)



class color:
    green = '\033[92m'
    yellow = '\033[93m'
    red = '\033[91m'
    end = '\033[0m'


if __name__ == '__main__':
    main()
