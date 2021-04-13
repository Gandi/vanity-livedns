Vanity LiveDNS
===============

## Description

This script is a simple utility tool to print information needed to configure a "vanity" set-up of LiveDNS: using NS records on your own zone instead of the default Gandi ones.

Check out the [Gandi documentation](https://docs.gandi.net/en/domain_names/advanced_users/vanity_nameservers.html) for more details

## Usage

Pretty straightforward:

```bash
python vanity_livedns.py domain-name
```

or, if you want to customize the names for something other than ns1, ns2, ns3 ..

```bash
python vanity_livedns.py domain-name --ns riri,fifi,loulou
```

This should output something like:

```
% python vanity_livedns.py example.com
Retrieving nameservers ns-208-a.gandi.net, ns-69-b.gandi.net, ns-11-c.gandi.net
Retrieving IP addresses 3/3

# Vanity DNS information for example.com
ns1
 173.246.100.209
 2001:4b98:aaaa::d1
ns2
 213.167.230.70
 2001:4b98:aaab::46
ns3
 217.70.187.12
 2604:3400:aaac::c


; Zone file
@ IN NS ns1
@ IN NS ns2
@ IN NS ns3

ns1 IN A 173.246.100.209
ns1 IN AAAA 2001:4b98:aaaa::d1
ns2 IN A 213.167.230.70
ns2 IN AAAA 2001:4b98:aaab::46
ns3 IN A 217.70.187.12
ns3 IN AAAA 2604:3400:aaac::c
```

You don't need any special permission as the script simply uses the public API to hash the name, and your local DNS resolver to retrieve the IP addresses of Gandi's nameservers

## Requirements

The script is a simple wrapper around `curl` and `dig`, so it need those binaries to work.