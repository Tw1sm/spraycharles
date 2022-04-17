#!/usr/bin/env python3

# parsing from "NT LAN Manager (NTLM) Authentication Protocol" v20190923, revision  31.0
# https://winprotocoldoc.blob.core.windows.net/productionwindowsarchives/MS-NLMP/%5bMS-NLMP%5d.pdf
# Source: https://github.com/b17zr/ntlm_challenger

import argparse
import base64
import datetime
import sys
from collections import OrderedDict

import click
import requests
from impacket import ntlm, smb, smb3
from impacket.smbconnection import SMBConnection
from urllib3.exceptions import InsecureRequestWarning


def decode_string(byte_string):
    return byte_string.decode("UTF-8").replace("\x00", "")


def decode_int(byte_string):
    return int.from_bytes(byte_string, "little")


def parse_version(version_bytes):

    major_version = version_bytes[0]
    minor_version = version_bytes[1]
    product_build = decode_int(version_bytes[2:4])

    version = "Unknown"

    if major_version == 5 and minor_version == 1:
        version = "Windows XP (SP2)"
    elif major_version == 5 and minor_version == 2:
        version = "Server 2003"
    elif major_version == 6 and minor_version == 0:
        version = "Server 2008 / Windows Vista"
    elif major_version == 6 and minor_version == 1:
        version = "Server 2008 R2 / Windows 7"
    elif major_version == 6 and minor_version == 2:
        version = "Server 2012 / Windows 8"
    elif major_version == 6 and minor_version == 3:
        version = "Server 2012 R2 / Windows 8.1"
    elif major_version == 10 and minor_version == 0:
        version = "Server 2016 or 2019 / Windows 10"

    return "{} (build {})".format(version, product_build)


def parse_negotiate_flags(negotiate_flags_int):

    flags = OrderedDict()

    flags["NTLMSSP_NEGOTIATE_UNICODE"] = 0x00000001
    flags["NTLM_NEGOTIATE_OEM"] = 0x00000002
    flags["NTLMSSP_REQUEST_TARGET"] = 0x00000004
    flags["UNUSED_10"] = 0x00000008
    flags["NTLMSSP_NEGOTIATE_SIGN"] = 0x00000010
    flags["NTLMSSP_NEGOTIATE_SEAL"] = 0x00000020
    flags["NTLMSSP_NEGOTIATE_DATAGRAM"] = 0x00000040
    flags["NTLMSSP_NEGOTIATE_LM_KEY"] = 0x00000080
    flags["UNUSED_9"] = 0x00000100
    flags["NTLMSSP_NEGOTIATE_NTLM"] = 0x00000400
    flags["UNUSED_8"] = 0x00000400
    flags["NTLMSSP_ANONYMOUS"] = 0x00000800
    flags["NTLMSSP_NEGOTIATE_OEM_DOMAIN_SUPPLIED"] = 0x00001000
    flags["NTLMSSP_NEGOTIATE_OEM_WORKSTATION_SUPPLIED"] = 0x00002000
    flags["UNUSED_7"] = 0x00004000
    flags["NTLMSSP_NEGOTIATE_ALWAYS_SIGN"] = 0x00008000
    flags["NTLMSSP_TARGET_TYPE_DOMAIN"] = 0x00010000
    flags["NTLMSSP_TARGET_TYPE_SERVER"] = 0x00020000
    flags["UNUSED_6"] = 0x00040000
    flags["NTLMSSP_NEGOTIATE_EXTENDED_SESSIONSECURITY"] = 0x00080000
    flags["NTLMSSP_NEGOTIATE_IDENTIFY"] = 0x00100000
    flags["UNUSED_5"] = 0x00200000
    flags["NTLMSSP_REQUEST_NON_NT_SESSION_KEY"] = 0x00400000
    flags["NTLMSSP_NEGOTIATE_TARGET_INFO"] = 0x00800000
    flags["UNUSED_4"] = 0x01000000
    flags["NTLMSSP_NEGOTIATE_VERSION"] = 0x02000000
    flags["UNUSED_3"] = 0x10000000
    flags["UNUSED_2"] = 0x08000000
    flags["UNUSED_1"] = 0x04000000
    flags["NTLMSSP_NEGOTIATE_128"] = 0x20000000
    flags["NTLMSSP_NEGOTIATE_KEY_EXCH"] = 0x40000000
    flags["NTLMSSP_NEGOTIATE_56"] = 0x80000000

    negotiate_flags = []

    for name, value in flags.items():
        if negotiate_flags_int & value:
            negotiate_flags.append(name)

    return negotiate_flags


def parse_target_info(target_info_bytes):

    MsvAvEOL = 0x0000
    MsvAvNbComputerName = 0x0001
    MsvAvNbDomainName = 0x0002
    MsvAvDnsComputerName = 0x0003
    MsvAvDnsDomainName = 0x0004
    MsvAvDnsTreeName = 0x0005
    MsvAvFlags = 0x0006
    MsvAvTimestamp = 0x0007
    MsvAvSingleHost = 0x0008
    MsvAvTargetName = 0x0009
    MsvAvChannelBindings = 0x000A

    target_info = OrderedDict()
    info_offset = 0

    while info_offset < len(target_info_bytes):
        av_id = decode_int(target_info_bytes[info_offset : info_offset + 2])
        av_len = decode_int(target_info_bytes[info_offset + 2 : info_offset + 4])
        av_value = target_info_bytes[info_offset + 4 : info_offset + 4 + av_len]

        info_offset = info_offset + 4 + av_len

        if av_id == MsvAvEOL:
            pass
        elif av_id == MsvAvNbComputerName:
            target_info["MsvAvNbComputerName"] = decode_string(av_value)
        elif av_id == MsvAvNbDomainName:
            target_info["MsvAvNbDomainName"] = decode_string(av_value)
        elif av_id == MsvAvDnsComputerName:
            target_info["MsvAvDnsComputerName"] = decode_string(av_value)
        elif av_id == MsvAvDnsDomainName:
            target_info["MsvAvDnsDomainName"] = decode_string(av_value)
        elif av_id == MsvAvDnsTreeName:
            target_info["MsvAvDnsTreeName"] = decode_string(av_value)
        elif av_id == MsvAvFlags:
            pass
        elif av_id == MsvAvTimestamp:
            filetime = decode_int(av_value)
            microseconds = (filetime - 116444736000000000) / 10
            time = datetime.datetime(1970, 1, 1) + datetime.timedelta(
                microseconds=microseconds
            )
            target_info["MsvAvTimestamp"] = time.strftime("%b %d, %Y %H:%M:%S.%f")
        elif av_id == MsvAvSingleHost:
            target_info["MsvAvSingleHost"] = decode_string(av_value)
        elif av_id == MsvAvTargetName:
            target_info["MsvAvTargetName"] = decode_string(av_value)
        elif av_id == MsvAvChannelBindings:
            target_info["MsvAvChannelBindings"] = av_value

    return target_info


def parse_challenge(challenge_message):

    # Signature
    # b'NTLMSSP\x00' --> NTLMSSP
    signature = decode_string(challenge_message[0:7])

    # MessageType
    # b'\x02\x00\x00\x00' --> 2
    message_type = decode_int(challenge_message[8:12])

    # TargetNameFields
    target_name_fields = challenge_message[12:20]
    target_name_len = decode_int(target_name_fields[0:2])
    target_name_max_len = decode_int(target_name_fields[2:4])
    target_name_offset = decode_int(target_name_fields[4:8])

    # NegotiateFlags
    negotiate_flags_int = decode_int(challenge_message[20:24])

    negotiate_flags = parse_negotiate_flags(negotiate_flags_int)

    # ServerChallenge
    server_challenge = challenge_message[24:32]

    # Reserved
    reserved = challenge_message[32:40]

    # TargetInfoFields
    target_info_fields = challenge_message[40:48]
    target_info_len = decode_int(target_info_fields[0:2])
    target_info_max_len = decode_int(target_info_fields[2:4])
    target_info_offset = decode_int(target_info_fields[4:8])

    # Version
    version_bytes = challenge_message[48:56]
    version = parse_version(version_bytes)

    # TargetName
    target_name = challenge_message[
        target_name_offset : target_name_offset + target_name_len
    ]
    target_name = decode_string(target_name)

    # TargetInfo
    target_info_bytes = challenge_message[
        target_info_offset : target_info_offset + target_info_len
    ]

    target_info = parse_target_info(target_info_bytes)

    return {
        "target_name": target_name,
        "version": version,
        "target_info": target_info,
        "negotiate_flags": negotiate_flags,
    }


def print_challenge(challenge):

    if "NTLMSSP_TARGET_TYPE_DOMAIN" in challenge["negotiate_flags"]:
        print("\nTarget (Domain): {}".format(challenge["target_name"]))
    elif "NTLMSSP_TARGET_TYPE_SERVER" in challenge["negotiate_flags"]:
        print("\nTarget (Server): {}".format(challenge["target_name"]))

    print("\nVersion: {}".format(challenge["version"]))

    print("\nTargetInfo:")

    for name, value in challenge["target_info"].items():
        print("  {}: {}".format(name, value))

    print("\nNegotiate Flags:")

    for flag in challenge["negotiate_flags"]:
        print("  {}".format(flag))


def request_http(url):

    # setup request, insecurely
    headers = {"Authorization": "NTLM TlRMTVNTUAABAAAAB4IIAAAAAAAAAAAAAAAAAAAAAAA="}
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

    request = requests.get(url, headers=headers, verify=False)

    if request.status_code not in [401, 302]:
        print(
            "[!] Expecting response code 401 or 302, received: {}".format(
                request.status_code
            )
        )
        return None

    # get auth header
    auth_header = request.headers.get("WWW-Authenticate")

    if not auth_header:
        print("[!] NTLM Challenge response not found (WWW-Authenticate header missing)")
        return None

    if not "NTLM" in auth_header:
        print(
            '[!] NTLM Challenge response not found (WWW-Authenticate does not contain "NTLM")'
        )
        return None

    # get challenge message from header
    challenge_message = base64.b64decode(auth_header.split(" ")[1].replace(",", ""))

    return challenge_message


def request_SMBv23(host, port=445):

    # start client
    smb_client = smb3.SMB3(host, host, sess_port=port)

    # start: modified from login()
    # https://github.com/SecureAuthCorp/impacket/blob/master/impacket/smb3.py

    session_setup = smb3.SMB2SessionSetup()

    if smb_client.RequireMessageSigning is True:
        session_setup["SecurityMode"] = smb3.SMB2_NEGOTIATE_SIGNING_REQUIRED
    else:
        session_setup["SecurityMode"] = smb3.SMB2_NEGOTIATE_SIGNING_ENABLED

    session_setup["Flags"] = 0

    # NTLMSSP
    blob = smb3.SPNEGO_NegTokenInit()
    blob["MechTypes"] = [
        smb3.TypesMech["NTLMSSP - Microsoft NTLM Security Support Provider"]
    ]

    auth = ntlm.getNTLMSSPType1(
        smb_client._Connection["ClientName"],
        "",
        smb_client._Connection["RequireSigning"],
    )
    blob["MechToken"] = auth.getData()

    session_setup["SecurityBufferLength"] = len(blob)
    session_setup["Buffer"] = blob.getData()

    packet = smb_client.SMB_PACKET()
    packet["Command"] = smb3.SMB2_SESSION_SETUP
    packet["Data"] = session_setup

    packet_id = smb_client.sendSMB(packet)

    smb_response = smb_client.recvSMB(packet_id)

    if smb_client._Connection["Dialect"] == smb3.SMB2_DIALECT_311:
        smb_client.__UpdatePreAuthHash(smb_response.rawData)

    # NTLM challenge
    if smb_response.isValidAnswer(smb3.STATUS_MORE_PROCESSING_REQUIRED):
        session_setup_response = smb3.SMB2SessionSetup_Response(smb_response["Data"])
        resp_token = smb3.SPNEGO_NegTokenResp(session_setup_response["Buffer"])

        return resp_token["ResponseToken"]

    else:
        return None


def request_SMBv1(host, port=445):

    # start client
    smb_client = smb.SMB(host, host, sess_port=port)

    # start: modified from login_standard()
    # https://github.com/SecureAuthCorp/impacket/blob/master/impacket/smb.py

    session_setup = smb.SMBCommand(smb.SMB.SMB_COM_SESSION_SETUP_ANDX)
    session_setup["Parameters"] = smb.SMBSessionSetupAndX_Extended_Parameters()
    session_setup["Data"] = smb.SMBSessionSetupAndX_Extended_Data()

    session_setup["Parameters"]["MaxBufferSize"] = 61440
    session_setup["Parameters"]["MaxMpxCount"] = 2
    session_setup["Parameters"]["VcNumber"] = 1
    session_setup["Parameters"]["SessionKey"] = 0
    session_setup["Parameters"]["Capabilities"] = (
        smb.SMB.CAP_EXTENDED_SECURITY
        | smb.SMB.CAP_USE_NT_ERRORS
        | smb.SMB.CAP_UNICODE
        | smb.SMB.CAP_LARGE_READX
        | smb.SMB.CAP_LARGE_WRITEX
    )

    # NTLMSSP
    blob = smb.SPNEGO_NegTokenInit()

    blob["MechTypes"] = [
        smb.TypesMech["NTLMSSP - Microsoft NTLM Security Support Provider"]
    ]

    auth = ntlm.getNTLMSSPType1(
        smb_client.get_client_name(), "", smb_client._SignatureRequired, use_ntlmv2=True
    )
    blob["MechToken"] = auth.getData()

    session_setup["Parameters"]["SecurityBlobLength"] = len(blob)
    session_setup["Parameters"].getData()
    session_setup["Data"]["SecurityBlob"] = blob.getData()
    session_setup["Data"]["NativeOS"] = "Unix"
    session_setup["Data"]["NativeLanMan"] = "Samba"

    smb_packet = smb.NewSMBPacket()

    if smb_client._SignatureRequired:
        smb_packet["Flags2"] |= smb_packet.SMB.FLAGS2_SMB_SECURITY_SIGNATURE

    smb_packet.addCommand(session_setup)

    smb_client.sendSMB(smb_packet)

    smb_response = smb_client.recvSMB()

    # NTLM challenge
    if smb_response.isValidAnswer(smb.SMB.SMB_COM_SESSION_SETUP_ANDX):

        session_response = smb.SMBCommand(smb_response["Data"][0])
        session_parameters = smb.SMBSessionSetupAndX_Extended_Response_Parameters(
            session_response["Parameters"]
        )
        session_data = smb.SMBSessionSetupAndX_Extended_Response_Data(
            flags=smb_response["Flags2"]
        )
        session_data["SecurityBlobLength"] = session_parameters["SecurityBlobLength"]
        session_data.fromString(session_response["Data"])

        resp_token = smb.SPNEGO_NegTokenResp(session_data["SecurityBlob"])

        return resp_token["ResponseToken"]

    else:
        return None


def main(url, smbv1):

    # request challenge
    if url.startswith("smb"):

        # get host/port from SMB
        host_port = url.split("://")[1].split("/")[0].split(":")

        if len(host_port) == 2:
            host, port = host_port
        else:
            host = host_port[0]
            port = 445

        if smbv1:
            challenge = request_SMBv1(host, port)
        else:
            challenge = request_SMBv23(host, port)

    elif url.startswith("http"):
        challenge = request_http(url)

    else:
        print("[!] Invalid URL, expecting http://... or smb://...")
        sys.exit()

    # parse challenge
    parsed_challenge = parse_challenge(challenge)

    # print challenge
    print_challenge(parsed_challenge)


if __name__ == "__main__":
    main()
