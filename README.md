spraycharles
======
## Overview ##
Low and slow password spraying tool, designed to spray on an interval over a long period of time.

## Install ##
```bash
$ git clone https://github.com/Tw1sm/spraycharles.git
$ cd spraycharles
$ pip3 install -r requirements.txt
$ ./spraycharles.py -h
```

## Usage ##
```
usage: spraycharles.py [-h] [-p PASSLIST] [-H HOST] -m MODULE [-o CSVFILE] -u USERLIST [-a ATTEMPTS] [-i INTERVAL] [-e] [-t TIMEOUT] [-b PORT] [-f FIREPROX]

low and slow password spraying tool

optional arguments:
  -h, --help            show this help message and exit
  -p PASSLIST, --passwords PASSLIST
                        filepath of the passwords list
  -H HOST, --host HOST  host to password spray (ip or hostname). Can by anything when using Office365 module - only used for logfile name.
  -m MODULE, --module MODULE
                        module corresponding to target host
  -o CSVFILE, --output CSVFILE
                        name and path of output csv where attempts will be logged
  -u USERLIST, --usernames USERLIST
                        filepath of the usernames list
  -a ATTEMPTS, --attempts ATTEMPTS
                        number of logins submissions per interval (for each user)
  -i INTERVAL, --interval INTERVAL
                        minutes inbetween login intervals
  -e, --equal           does 1 spray for each user where password = username
  -t TIMEOUT, --timeout TIMEOUT
                        web request timeout threshold. default is 5 seconds
  -b PORT, --port PORT  port to connect to on the specified host. Default 443.
  -f FIREPROX, --fireprox FIREPROX
                        the url of the fireprox interface, if you are using fireprox.
```
### Examples ###
Basic usage (Office365)
```
./spraycharles -u users.txt -p passwords.txt -m Office365
```
Basic usage (non-Office365)
```
./spraycharles -u users.txt -H webmail.company.com -p passwords.txt -m owa
```
Attempt 5 logins per user every 20 minutes
```
./spraycharles -n users.txt -H webmail.company.com -p passwords.txt -i 20 -a 5 -m owa
```
Usage with fireprox (Office365)
```
./spraycharles -u users.txt -H webmail.company.com -p passwords.txt -m owa -f abcdefg.execute-api.us-east-1.amazonawms.com
```

### Generating Custom Spray Lists ###
make_list.py will generate a password list based off the specifications provided in list_elements.json
```
./make_list.py
```

### Analyzing the results CSV file ###
`analyze.py` can read your output CSV and determine response lengths that are statistically relevant. With enough data, it should be able to pull successful logins out of your CSV file. This is not the only way to determine successful logins, depending on your target site, and I would still recommend checking the data yourself to be sure nothing is missed.
```
./analyze.py myresults.csv
```


## Disclaimer ##
This tool is designed for use during penetration testing; usage of this tool for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state and federal laws. Developers assume no liability and are not responsible for any misuse of this program.
