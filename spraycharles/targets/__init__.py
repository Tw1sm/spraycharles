from enum import Enum

from spraycharles.targets.Adfs import Adfs
from spraycharles.targets.Ciscosslvpn import Ciscosslvpn
from spraycharles.targets.Citrix import Citrix
from spraycharles.targets.Ntlm import Ntlm
from spraycharles.targets.Office365 import Office365
from spraycharles.targets.Okta import Okta
from spraycharles.targets.Owa import Owa
from spraycharles.targets.Smb import Smb
from spraycharles.targets.Sonicwall import Sonicwall

#
# define all target modules
#
all = [
    Adfs,
    Ciscosslvpn,
    Citrix,
    Ntlm,
    Office365,
    Okta,
    Owa,
    Smb,
    Sonicwall
]


#
# enum for typer argument verification
#
class Target(str, Enum):
    adfs        = Adfs.NAME
    ciscosslvpn = Ciscosslvpn.NAME
    citrix      = Citrix.NAME
    ntlm        = Ntlm.NAME
    office365   = Office365.NAME
    okta        = Okta.NAME
    owa         = Owa.NAME
    smb         = Smb.NAME
    sonicwall   = Sonicwall.NAME


