passwordpredator
======
## Overview ##
Low and slow password spraying tool, designed to password spray on an interval over a long period of time.

## Install ##
```bash
$ git clone https://github.com/Tw1sm/passwordpredator.git
$ cd passwordpredator
$ pip install -r requirements.txt
$ ./passwordpredator.py -h
```

## Usage ##
usage: passwordpredator.py [-h] [-p PASSLIST] -H HOST -m MODULE -o CSVFILE -u USERLIST 
                           [-a ATTEMPTS] [-i INTERVAL] [-e] [-t TIMEOUT]

```
optional arguments:
  -h, --help            show this help message and exit
  -p PASSLIST, --passwords PASSLIST
                        filepath of the passwords list
  -H HOST, --host HOST  host to password spray (ip or hostname)
  -m MODULE, --module MODULE
                        module corresponding to target host
  -o CSVFILE, --output CSVFILE
                        name and path of output csv where attempts will be
                        logged
  -u USERLIST, --usernames USERLIST
                        filepath of the usernames list
  -a ATTEMPTS, --attempts ATTEMPTS
                        number of logins submissions per interval (for each
                        user)
  -i INTERVAL, --interval INTERVAL
                        minutes inbetween login intervals
  -e, --equal           does 1 spray for each user where password = username
  -t TIMEOUT, --timeout TIMEOUT
                        web request timeout threshold. default is 5 seconds

```
### Examples ###
Basic usage
```
./passwordpredator -u users.txt -H webmail.company.com -p passwords.txt -m owa
```
Attempt 5 logins per user every 20 minutes
```
./passwordpredator -n users.txt -u webmail.company.com -i 20 -a 5 -m owa
```


### Generating Custom Spray Lists ###
make_list.py will generate a password list based off the specifications provided in list_elements.json
```
./make_list.py
```


## Disclaimer ##
This tool is designed for use during penetration testing; usage of this tool for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state and federal laws. Developers assume no liability and are not responsible for any misuse of this program.