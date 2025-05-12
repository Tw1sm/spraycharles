from enum import Enum

from spraycharles.targets.Adfs import ADFS
from spraycharles.targets.Ciscosslvpn import CiscoSSLVPN
from spraycharles.targets.Citrix import Citrix
from spraycharles.targets.Ntlm import NTLM
from spraycharles.targets.Office365 import Office365
from spraycharles.targets.Okta import Okta
from spraycharles.targets.Owa import OWA
from spraycharles.targets.Rdg import RDG
from spraycharles.targets.Smb import SMB
from spraycharles.targets.Sonicwall import Sonicwall


#
# define all target modules
#
all = [
    ADFS,
    CiscoSSLVPN,
    Citrix,
    NTLM,
    Office365,
    Okta,
    OWA,
    RDG,
    SMB,
    Sonicwall
]


#
# enum for typer argument verification
#
class Target(str, Enum):
    adfs        = ADFS.NAME
    ciscosslvpn = CiscoSSLVPN.NAME
    citrix      = Citrix.NAME
    ntlm        = NTLM.NAME
    office365   = Office365.NAME
    okta        = Okta.NAME
    owa         = OWA.NAME
    rdg         = RDG.NAME
    smb         = SMB.NAME
    sonicwall   = Sonicwall.NAME


