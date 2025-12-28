<p align="center">
  <p align="center">
    <img height=250 src=.resources/spraycharles.jpeg>
  </p>

  <h1 align="center">Spraycharles</h1>
  
  <p align="center">
    <i>
      hey, yo I'm feeling like spraycharles - Chiddy Bang
    </i>
  </p>
  <span align="center">

    
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![PyPi](https://img.shields.io/pypi/v/spraycharles?style=for-the-badge)
    
  </span>
</p>

Low and slow password spraying tool, designed to spray on an interval over a long period of time. 

Includes spraying plugins for `Office365`, `OWA`, `EWS`, `Okta`, `ADFS`, `Cisco SSL VPN`, `Citrix Netscaler`, `Sonciwall`, `NTLM over HTTP`, and `SMB`.

Associated [blog post](https://www.sprocketsecurity.com/blog/how-to-bypass-mfa-all-day) by [@sprocket_ed](https://twitter.com/sprocket_ed) covering NTLM over HTTP, Exchange Web Services and Spraycharles.

### What is this tool?
Spraycharles is a relatively simple password sprayer, designed at a time when there weren't many publicly available tools enabling password spraying to be a non-manual process over the course of a penetration test. Maybe the best feature of Spraycharles is the ability to setup a long running spray using `-a/--attempts` and `-i/--interval`, and let it run over the couse of several days, while periodically checking on it. If you have a one-off service or something unique to spray, it's also very easy to template a new module and start spraying.

### What is this tool not?
Spraycharles was not initially designed with modern authentication/cloud providers in mind. If you're looking for more advanced features, you may want to check out tools such as [CredMaster](https://github.com/knavesec/CredMaster) or [TeamFiltration](https://github.com/Flangvik/TeamFiltration) Spraycharles was not designed to be _fast_ - it is single threaded and geared towards more of a volume/time approach.

## Install
Spraycharles can be installed with `pip3 install spraycharles` or by cloning this repository and running `pip3 install .`

> [!TIP]
> This will register the `spraycharles`, and `sc` for short, aliases in your path. Log and output files are stored in `~/.spraycharles`. An alternative output location can be specified with a CLI flag.

### Using Docker
Execute the following commands to build the Spraycharles Docker container:

```bash
git clone https://github.com/Tw1sm/spraycharles
cd spraycharles/extras
docker build . -t spraycharles
```

Execute the following command to use the Spraycharles Docker container:

```bash
docker run -it -v ~/.spraycharles:/root/.spraycharles spraycharles -h
```

You may need to specify additional volumes based on where username a password lists are being stored.

### NixOS

For Nix or NixOS users is a package available. Keep in mind that the latest releases might only
be present in the `unstable` channel.

```bash
nix-env -iA nixos.spraycharles
```

## Usage
The `spray` subcommand:
```
 Usage: spraycharles spray [OPTIONS] COMMAND [ARGS]...

 Low and slow password spraying

╭─ Options ─────────────────────────────────────────────────────────────────────────────╮
│ --debug                 Enable debug logging (overrides --quiet)                      │
│ --config          TEXT  Configuration file.                                           │
│ --help    -h            Show this message and exit.                                   │
╰───────────────────────────────────────────────────────────────────────────────────────╯
╭─ User/Pass Config ────────────────────────────────────────────────────────────────────╮
│ *  --usernames  -u      TEXT  Filepath of the usernames list [default: None]          │
│                               [required]                                              │
│ *  --passwords  -p      TEXT  Single password to spray or filepath of the passwords   │
│                               list                                                    │
│                               [default: None]                                         │
│                               [required]                                              │
│    --equal      -e            Does 1 spray for each user where password = username    │
╰───────────────────────────────────────────────────────────────────────────────────────╯
╭─ Spray Target ────────────────────────────────────────────────────────────────────────╮
│    --host      -H      TEXT                           Host to password spray (ip or   │
│                                                       hostname). Can by anything when │
│                                                       using Office365 module - only   │
│                                                       used for logfile name           │
│                                                       [default: None]                 │
│ *  --module    -m      [ADFS|CiscoSSLVPN|Citrix|NTLM  Module corresponding to target  │
│                        |Office365|Okta|OWA|SMB|Sonic  host                            │
│                        wall]                          [default: None]                 │
│                                                       [required]                      │
│    --path              TEXT                           NTLM authentication endpoint    │
│                                                       (i.e., rpc or ews)              │
│                                                       [default: None]                 │
│    --port      -P      INTEGER                        Port to connect to on the       │
│                                                       specified host                  │
│                                                       [default: 443]                  │
│    --fireprox  -f      TEXT                           URL of desired fireprox         │
│                                                       interface                       │
│                                                       [default: None]                 │
│    --domain    -d      TEXT                           HTTP - Prepend DOMAIN\ to       │
│                                                       usernames; SMB - Supply domain  │
│                                                       for smb connection              │
│                                                       [default: None]                 │
│    --no-ssl                                           Use HTTP instead of HTTPS       │
╰───────────────────────────────────────────────────────────────────────────────────────╯
╭─ Output ──────────────────────────────────────────────────────────────────────────────╮
│ --output   -o      TEXT  Name and path of result output file [default: None]          │
│ --quiet                  Will not log each login attempt to the console               │
│ --analyze                Run the results analyzer after each spray interval (Early    │
│                          false positives are more likely)                             │
╰───────────────────────────────────────────────────────────────────────────────────────╯
╭─ Spray Behavior ──────────────────────────────────────────────────────────────────────╮
│ --attempts    -a      INTEGER  Number of logins submissions per interval (for each    │
│                                user)                                                  │
│                                [default: None]                                        │
│ --interval    -i      INTEGER  Minutes inbetween login intervals [default: None]      │
│ --timeout     -t      INTEGER  Web request timeout threshold [default: 5]             │
│ --jitter              INTEGER  Jitter time between requests in seconds                │
│                                [default: None]                                        │
│ --jitter-min          INTEGER  Minimum time between requests in seconds               │
│                                [default: None]                                        │
│ --pause                        Pause the spray between intervals if a new potentially │
│                                successful login was found                             │
╰───────────────────────────────────────────────────────────────────────────────────────╯
╭─ Notifications ───────────────────────────────────────────────────────────────────────╮
│ --notify   -n      [Slack|Teams|Discord]  Enable notifications for Slack, Teams or    │
│                                           Discord                                     │
│                                           [default: None]                             │
│ --webhook  -w      TEXT                   Webhook used for specified notification     │
│                                           module                                      │
│                                           [default: None]                             │
╰───────────────────────────────────────────────────────────────────────────────────────╯
```

### Config File
Due to the amount of CLI flags often used, an alternative is to populate command line parameters from a yaml file using the `--config` flag. Additionally, each time you use Spraycharles, your CLI options will be written to a yaml file (`last-config.yaml`) in the current directory for easy modification and reuse.

### Notifications
Spraycharles has the ability to issue notifications to Discord, Slack and Microsoft Teams following a potentially successful login attempt. This list of notification providers can augmented using the utils/notify.py script. For any of the potential notification agents, you must specify its name and a webhook URL.

You can specify these using the configuration file to keep your command shorter:

```yaml
notify: Slack
webhook: https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX
```

Notifications sent to any of the providers will include the targeted hostname associated with the spraying job. This is expecially useful when spraying multiple targets at once.

### Updating Username/Password Files
You have the ability to make changes to the provided username and password files while the spray is in progress. Additions or removals to the lists will take effect on the next password rotation

> [!NOTE]
> If you insert a new password into the list, it must be _after_ the password being currently sprayed, in order to be sprayed (Spraycharles keeps an internal loop counter used as an index to pull the next password at the corresponding place in the updated list)


## Utilities
Spraycharles is packaged with some additional utilities to assist with spraying efforts. Full list of Spraycharles modules:
```
 Usage: spraycharles [OPTIONS] COMMAND [ARGS]...

╭─ Options ─────────────────────────────────────────────────────────────────────────────╮
│ --help  -h        Show this message and exit.                                         │
╰───────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────────────────╮
│ analyze   Analyze Spraycharles output files for potential spray hits                  │
│ gen       Generate custom password lists from JSON file                               │
│ modules   List spraying modules                                                       │
│ parse     Parse NTLM over HTTP and SMB endpoints to collect domain information        │
│ spray     Low and slow password spraying                                              │
╰───────────────────────────────────────────────────────────────────────────────────────╯
```

### Generating Custom Spray Lists
The Spraycharles "gen" subcommand will generate a password list based off the specifications provided in extras/list_elements.json

```bash
spraycharles gen extras/list_elements.json custom_passwords.txt
```

### Extracting Domain from NTLM over HTTP and SMB
The Spraycharles parse subcommand will extract the internal domain from both NTLM over HTTP and SMB services using a command similar to the one listed below.

```bash
spraycharles parse https://example.com/ews
spraycharles parse smb://host.domain.local
```

### Analyzing Result Files
The `analyze` submodule can read your output JSON objects and determine response lengths that are statistically relevant. With enough data, it should be able to pull successful logins out of your results file. This is not the only way to determine successful logins, depending on your target site, and I would still recommend checking the data yourself to be sure nothing is missed. For SMB, it will simply find entries with NTSTATUS codes that indicate success.

```bash
spraycharles analyze myresults.json
```

## Disclaimer
This tool is designed for use during penetration testing; usage of this tool for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state and federal laws. Developers assume no liability and are not responsible for any misuse of this program.

## Development
Spraycharles uses Poetry to manage dependencies. Install from source and setup for development with:

```bash
pip3 install poetry
git clone https://github.com/Tw1sm/spraycharles
cd spraycharles
poetry install
```

## Credits
- [@sprocket_ed](https://twitter.com/sprocket_ed) for contributing: several spray modules, many of features that make spraycharles great, and the associated blog post
- [@b17zr](https://twitter.com/b17zr) for the `ntlm_challenger.py` script, which is included in the `utils` folder
