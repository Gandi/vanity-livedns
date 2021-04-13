#!/usr/bin/env python3
"""
This script is used to retrieve and print information about how to setup
"vanity" nameservers setup on Gandi LiveDNS system.

It only uses curl and dig to print out some information.

See
https://docs.gandi.net/en/domain_names/advanced_users/vanity_nameservers.html
for additional information on how to set this up

"""
from __future__ import print_function

import os
import json
import sys
import fcntl
import argparse
import subprocess


DEFAULT_NAMES = ['ns%d' % i for i in range(1, 10)]
LIVEDNS_URL = 'https://api.gandi.net/v5/livedns/nameservers/{fqdn}'


def which(program):
    """
    Which witch?

    Check if program is present / executable

    """
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def require_executable(program):
    """exit with error unless program is an accessible executable"""
    if not which(program):
        print('%r command not found, cannot continue' % program,
              file=sys.stderr)
        sys.exit(127)


def unbuffered_io(buffers=(sys.stdout, )):
    """Allows printing to stdout unbuffered"""

    for buffer in buffers:
        flag = fcntl.fcntl(buffer.fileno(), fcntl.F_GETFL)
        flag |= os.O_SYNC
        fcntl.fcntl(buffer.fileno(), fcntl.F_SETFL, flag)


def livedns_ns(fqdn):
    """Returns the "default" list of LiveDNS servers for a given name"""
    url = LIVEDNS_URL.format(fqdn=fqdn.encode('idna').decode())

    args = ['curl', '-f', '-s', '-H', 'Authorization: Apikey unused', url]

    data = subprocess.check_output(args).decode()

    return json.loads(data)


def resolve_name(name):
    """Return the v4/v6 IP addresses for a given name, using local resolver"""

    args = ['dig', '+short', name, 'A',  name, 'AAAA']

    return subprocess.check_output(args).decode().splitlines()


def get_nameservers(fqdn):
    """
    For a given fqdn returns a dict of nameserver -> [ip, ip]

    prints progression for humans

    """

    print('Retrieving nameservers ...', end='')
    ret = {name: [] for name in livedns_ns(fqdn)}

    print('\b\b\b' + ', '.join(ret))

    fmt = '\rRetrieving IP addresses %%d/%d' % len(ret)
    print(fmt % 0, end='')

    for i, name in enumerate(ret, 1):
        ret[name] = resolve_name(name)
        print(fmt % i, end='')

    print('\n')

    return ret


def one_domain(fqdn, ns_names=DEFAULT_NAMES):
    """
    Print Vanity NS information for a domain name

    - nameservers and their IPS
    - records needed in the zone file

    """
    nameservers = get_nameservers(fqdn)

    ns_data = [(name, ips)
               for name, (_, ips) in zip(ns_names, nameservers.items())]

    print('# Vanity DNS information for %s' % fqdn)
    for name, ips in ns_data:
        print('%s' % name)
        for ip in ips:
            print(' %s' % ip)

    print('\n')
    print("; Zone file")

    for name, ips in ns_data:
        print('@ IN NS %s' % name)
    print()

    for name, ips in ns_data:
        for ip in ips:
            rdtype = 'AAAA' if ':' in ip else 'A'
            print('%s IN %s %s' % (name, rdtype, ip))


def type_ns_list(value):
    res = value.split(',')
    if len(res) < 2:
        raise ValueError('at least 2 nameservers are needed')
    return res


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('fqdns', nargs='+', help='Domain name(s) to process')
    parser.add_argument('-n', '--ns', type=type_ns_list,
                        default=DEFAULT_NAMES,
                        help='comma-separated list of local names to use')

    return parser.parse_args()


def main():
    args = parse_args()

    require_executable('dig')
    require_executable('curl')

    for fqdn in args.fqdns:
        one_domain(fqdn, args.ns)


if __name__ == '__main__':
    unbuffered_io()
    main()
