import typer
from typer_config import use_yaml_config
from typer_config.decorators import dump_yaml_config
from rich.prompt import Confirm
from pathlib import Path

from spraycharles import ascii
from spraycharles.lib.logger import logger, init_logger, console
from spraycharles.targets import Target, all
from spraycharles.lib.spraycharles import Spraycharles
from spraycharles.analyze import HookSvc

app = typer.Typer()
COMMAND_NAME = 'spray'
HELP =  'Low and slow password spraying'

@app.callback(no_args_is_help=True, invoke_without_command=True)
@use_yaml_config()
@dump_yaml_config('last-config.yaml')
def main(
    usernames:  str    = typer.Option(..., '-u', '--usernames', help="Filepath of the usernames list", rich_help_panel="User/Pass Config"),
    passwords:  str     = typer.Option(..., '-p', '--passwords', help="Single password to spray or filepath of the passwords list", rich_help_panel="User/Pass Config"),
    host:       str     = typer.Option(None, '-H', '--host', help="Host to password spray (ip or hostname). Can by anything when using Office365 module - only used for logfile name", rich_help_panel="Spray Target"),
    module:     Target  = typer.Option(..., '-m', '--module', case_sensitive=False, help="Module corresponding to target host", rich_help_panel="Spray Target"),
    path:       str     = typer.Option(None, help="NTLM authentication endpoint (i.e., rpc or ews)", rich_help_panel="Spray Target"),
    output:     str     = typer.Option("output.csv", '-o', '--output', help="Name and path of output csv where attempts will be logged", rich_help_panel="Output"),
    attempts:   int     = typer.Option(None, '-a', '--attempts', help="Number of logins submissions per interval (for each user)", rich_help_panel="Spray Behavior"),
    interval:   int     = typer.Option(None, '-i', '--interval', help="Minutes inbetween login intervals", rich_help_panel="Spray Behavior"),
    equal:      bool    = typer.Option(False, '-e', '--equal', help="Does 1 spray for each user where password = username", rich_help_panel="User/Pass Config"),
    timeout:    int     = typer.Option(5, '-t', '--timeout', help="Web request timeout threshold", rich_help_panel="Spray Behavior"),
    port:       int     = typer.Option(443, '-P','--port', help="Port to connect to on the specified hos", rich_help_panel="Spray Target"),
    fireprox:   str     = typer.Option(None, '-f', '--fireprox', help="URL of desired fireprox interface", rich_help_panel="Spray Target"),
    domain:     str     = typer.Option(None, '-d', '--domain', help="HTTP - Prepend DOMAIN\\ to usernames; SMB - Supply domain for smb connection", rich_help_panel="Spray Target"),
    analyze:    bool    = typer.Option(False, '--analyze', help="Run the results analyzer after each spray interval (Early false positives are more likely)", rich_help_panel="Output"),
    jitter:     int     = typer.Option(None, help="Jitter time between requests in seconds", rich_help_panel="Spray Behavior"),
    jitter_min: int     = typer.Option(None, help="Minimum time between requests in seconds", rich_help_panel="Spray Behavior"),
    notify:     HookSvc = typer.Option(None, '-n', '--notify', help="Enable notifications for Slack, Teams or Discord", rich_help_panel="Notifications"),
    webhook:    str     = typer.Option(None, '-w', '--webhook', help="Webhook used for specified notification module", rich_help_panel="Notifications"),
    pause:      bool    = typer.Option(False, '--pause', help="Pause the spray following a potentially successful login", rich_help_panel="Spray Behavior"),
    no_ssl:     bool    = typer.Option(False, '--no-ssl', help="Use HTTP instead of HTTPS", rich_help_panel="Spray Target"),
    debug:      bool    = typer.Option(False, '--debug', help="Enable debug logging")):

    init_logger(debug)

    #
    #  Suppress SSL warnings
    #
    try:
        import requests.packages.urllib3

        requests.packages.urllib3.disable_warnings()
        logger.debug("Disabled urllib3 SSL warnings")
    except Exception:
        pass

    #
    # Read username list and password [list]
    #
    try:
        logger.debug(f"Reading usernames from file {usernames}")
        user_list = Path(usernames).read_text().splitlines()
    except:
        logger.error(f"Failed to read usernames from {usernames}")
        exit()
    
    if Path(passwords).exists():
        logger.debug(f"Password list detected, reading passwords from file {passwords}")
        password_list = Path(passwords).read_text().splitlines()
    else:
        logger.debug("Single password detected")
        password_list = [passwords]

    #
    # Host arg is required for all modules except Office365
    #
    if module != Target.office365 and host is None:
        logger.error("Hostname (-H) of target (mail.targetdomain.com) is required for all modules execept Office365")
        exit()
    
    elif module == Target.office365 and host is None:
        #
        # Set host to Office365 for the logfile name
        #
        host = "Office365"  
    
    #
    # Fireprox, port and timeout are ignored when spraying over SMB
    #
    elif module == Target.smb and (timeout != 5 or fireprox is not None or port != 443):
        logger.warning("Fireprox (-f), port (-P) and timeout (-t) are incompatible when spraying over SMB")


    # 
    # Check that interval and attempt args are supplied together
    #
    if (attempts is None) ^ (interval is None):
        logger.error("[!] Number of login attempts per interval (-a) and interval (-i) must be supplied together")
        exit()
    
    #
    # Warn user if interval and attempts are not supplied and password list is provided
    #
    if interval is None and attempts is None and len(password_list) > 1:
        logger.warning("You have not provided spray attempts/interval. This may lead to account lockouts!")
        print()

        Confirm.ask(
            "[yellow]Press enter to continue anyways",
            default=True,
            show_choices=False,
            show_default=False,
        )
        print()

    # 
    # Check that jitter flags aren't supplied independently
    #
    if (jitter is None) ^ (jitter_min is None):
        logger.error("Jitter (--jitter) and jitter minumum (--jitter-min) must be supplied together")
        exit()

    #
    # Validate that jitter is greater than jitter_min
    #
    if jitter is not None and jitter_min is not None and jitter_min >= jitter:
        logger.error("--jitter flag must be greater than --jitter-min flag")
        exit()

    # 
    # Path flag must be set for NTLM authentication module
    #
    if module == Target.ntlm and path is None:
        logger.error("Must set --path to use the NTLM authentication module")
        exit()

    #
    # Notify flag requires a webhook
    #
    if notify is not None and webhook is None:
        logger.error("Must specify a Webhook URL when the notify flag is used.")
        exit()


    #
    # Finally validated, lets spray
    #
    spraycharles = Spraycharles(
        user_list=user_list,
        user_file=Path(usernames),
        password_list=password_list,
        password_file=Path(passwords),
        host=host,
        module=module,
        path=path,
        output=output,
        attempts=attempts,
        interval=interval,
        equal=equal,
        timeout=timeout,
        port=port,
        fireprox=fireprox,
        domain=domain,
        analyze=analyze,
        jitter=jitter,
        jitter_min=jitter_min,
        notify=notify,
        webhook=webhook,
        pause=pause,
        no_ssl=no_ssl,
    )

    spraycharles.initialize_module()
    console.print(ascii())
    spraycharles.pre_spray_info()
    spraycharles.spray()