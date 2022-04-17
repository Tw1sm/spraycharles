spraycharles
======
## Overview ##
Low and slow password spraying tool, designed to spray on an interval over a long period of time.

Associated [blog post](https://www.sprocketsecurity.com/blog/how-to-bypass-mfa-all-day) by [@sprocket_ed](https://twitter.com/sprocket_ed) covering NTLM over HTTP, Exchange Web Services and spraycharles.

## Content ##
- [Install](#install)
  - [Using pipx](#using-pipx)
  - [Using Docker](#using-docker)
- [Usage](#usage)
  - [Config File](#config-file)
  - [Notifications](#notifications)
  - [Examples](#examples)
- [Utilities](#utilities)
  - [Generating Custom Spray Lists](#generating-custom-spray-lists)
  - [Extracting Domain from NTLM over HTTP and SMB](#extracting-domain-from-ntlm-over-http-and-smb)
  - [Analyzing the results CSV file](#analyzing-the-results-csv-file)
- [Disclaimer](#disclaimer)
- [Development](#development)
- [Credits](#credits)

## Install ##

### Using pipx ###

You can use pipx to to install the spraycharles package into an isolated environment. First install pipx:

```
pip3 install pipx
```

Following this, install the package directly from GitHub using the following command:

```
pipx install git+https://github.com/Tw1sm/spraycharles.git
```


The spraycharles package will then be in your path and useable from anywhere. Spraycharles can be executed using the following commands:

```
spraycharles
sc
```

Note that log and output CSV files are stored in a directory created in your users homefolder with the name `.spraycharles`. These log and CSV files are dynamically created on runtime with. These files are in the format:

```
target-host.timestamp.csv
```

See [usage](#usage) for instructions on how to specify an alternative location for your CSV file.

### Using Docker ###
Execute the following commands to build the spraycharles Docker container:

```
git clone https://github.com/Tw1sm/spraycharles
cd spraycharles/extras
docker build . -t spraycharles
```

Execute the following command to use the spraycharles Docker container:

```
docker run -it -v ~/.spraycharles:/root/.spraycharles spraycharles -h
```

You may need to specify additional volumes based on where username a password lists are being stored.


<br/>

## Usage ##
```
Usage: spraycharles [OPTIONS]

  Low and slow password spraying tool...

Options:
  -p, --passwords TEXT            Filepath of the passwords list or a single
                                  password to spray.  [required]
  -u, --usernames TEXT            Filepath of the usernames list.  [required]
  -H, --host TEXT                 Host to password spray (ip or hostname). Can
                                  by anything when using Office365 module -
                                  only used for logfile name.
  -m, --module TEXT               Module corresponding to target host.
                                  [required]
  --path TEXT                     NTLM authentication endpoint. Ex: rpc or ews
  -o, --output TEXT               Name and path of output csv where attempts
                                  will be logged.
  -a, --attempts INTEGER          Number of logins submissions per interval
                                  (for each user).
  -i, --interval INTEGER          Minutes inbetween login intervals.
  -e, --equal INTEGER             Does 1 spray for each user where password =
                                  username.
  -t, --timeout INTEGER           Web request timeout threshold. Default is 5
                                  seconds.
  -P, --port INTEGER              Port to connect to on the specified host.
                                  Default is 443.
  -f, --fireprox TEXT             The url of the fireprox interface, if you
                                  are using fireprox.
  -d, --domain TEXT               HTTP: Prepend DOMAIN\ to usernames. SMB:
                                  Supply domain for smb connection.
  --analyze                       Run the results analyzer after each spray
                                  interval. False positives are more likely
  --pause                         Pause the spray following a potentially
                                  successful login
  -j, --jitter INTEGER            Jitter time between requests in seconds.
  -jm, --jitter-min INTEGER       Minimum time between requests in seconds.
  -n, --notify [teams|slack|discord]
                                  Enable notifications for Slack, MS Teams or
                                  Discord.
  -w, --webhook TEXT              Webhook used for specified notification
                                  module
  --config FILE                   Read configuration from FILE.
  -h, --help                      Show this message and exit.
```

Spraycharles also includes other submodules:

```
Usage: sc [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  analyze  Analyze existing csv files.
  gen      Generate custom password lists from customized JSON files.
  parse    Parse NTLM over HTTP and SMB endpoints to collect domain information.
  spray    Low and slow password spraying tool.
```

See below for further information about these modules.

#### Config File
It is possible to pre-populate command line arguments form a configuration file using the `--config` argument.

An example configuration file is listed below:

```
usernames = '/tmp/users.txt'
passwords = '/tmp/passwords.txt'
output = 'mail.acme.com.csv'
module = 'owa'
host = 'mail.acme.com'
domain = 'ACME'
analyze = 'True'
attempts = '1'
interval = '30'
timeout = '25'
```

<br/>

### Notifications ###
Spraycharles has the ability to issue notifications to Discord, Slack and Microsoft Teams following a potentially successful login attempt. This list of notification providers can augmented using the utils/notify.py script. For any of the potential notification agents, you must specify its name and a webhook URL.

It is best to specify this information using the configuration file to keep your command shorter:

```
notify = 'slack'
webhook = 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX'
```

Notifications sent to any of the providers will include the targeted hostname associated with the spraying job. This is expecially useful when spraying multiple targets at once using spraycharles.

<br/>

### Examples ###
Basic usage (Office365)
```
spraycharles -u users.txt -p passwords.txt -m Office365
```
Basic usage (non-Office365) with a single password, supplied via command line
```
spraycharles -u users.txt -H webmail.company.com -p Password123 -m owa
```
Attempt 5 logins per user every 20 minutes
```
spraycharles -u users.txt -H webmail.company.com -p passwords.txt -i 20 -a 5 -m owa
```
Usage with fireprox (Office365)
```
spraycharles -u users.txt -p passwords.txt -m office365 -f abcdefg.execute-api.us-east-1.amazonawms.com
```
Spray host over SMB with 2 attempts per user every hour
```
spraycharles -u users.txt -p passwords.txt -m Smb -H 10.10.1.5 -a 2 -i 60
```

<br/>

## Utilities ##
Spraycharles is packaged with some additional utilities to assist with spraying efforts.
<br/>

#### Generating Custom Spray Lists
The spraycharles "gen" subcommand will generate a password list based off the specifications provided in extras/list_elements.json

```
spraycharles gen extras/list_elements.json custom_passwords.txt
```

<br/>

#### Extracting Domain from NTLM over HTTP and SMB
The spraycharles parse subcommand will extract the internal domain from both NTLM over HTTP and SMB services using a command similar to the one listed below.


```
spraycharles parse https://example.com/ews
```

<br/>

### Analyzing the results CSV file ###
With the analyze submodule can read your output CSV and determine response lengths that are statistically relevant. With enough data, it should be able to pull successful logins out of your CSV file. This is not the only way to determine successful logins, depending on your target site, and I would still recommend checking the data yourself to be sure nothing is missed. For SMB, it will simply find entries that contain "SUCCESS"

```
spraycharles analyze myresults.csv
```

<br/>

## Disclaimer ##
This tool is designed for use during penetration testing; usage of this tool for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state and federal laws. Developers assume no liability and are not responsible for any misuse of this program.

## Development ##
Git pre-commit is used to maintain code quality and ensure uniform formatting. To begin developing with spraycharles:

```
pip3 install poetry
git clone https://github.com/Tw1sm/spraycharles
cd spraycharles
poetry shell && poetry install
```

Tests for the spraycharles project are written and stored in the tests directory. A more extensive testing harness is coming soon!

## Credits ##
- [@sprocket_ed](https://twitter.com/sprocket_ed) for contributing: several spray modules, many of features that make spraycharles great, and the associated blog post
- [@b17zr](https://twitter.com/b17zr) for the `ntlm_challenger.py` script, which is included in the `utils` folder
