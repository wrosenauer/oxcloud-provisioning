#!/usr/bin/env python3

# Copyright (C) 2026  OX Software GmbH
#                     Wolfgang Rosenauer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import json
import restclient
import settings


def main():
    parser = argparse.ArgumentParser(
        description='Lists per maildomain DKIM entries of an OX Cloud brand.')
    parser.add_argument("-d", "--domain",
                        help="Maildomain to list. (lists all domains of the brand if left out)")
    parser.add_argument("--selector",
                        help="Specific selector to retrieve. (requires -d)")
    parser.add_argument("--status", action="store_true",
                        help="Show selector rotation status (DNS/LDAP) for the domain. (requires -d)")
    parser.add_argument("--dump", action="store_true",
                        help="Dump raw JSON response.")
    args = parser.parse_args()

    if args.selector is not None and args.domain is None:
        parser.error("--selector requires -d/--domain to be specified.")
    if args.status and args.domain is None:
        parser.error("--status requires -d/--domain to be specified.")

    brand = settings.getCreds()["login"]

    if args.domain is None:
        r = restclient.get("mail/dkim/" + brand, None)
    elif args.status:
        r = restclient.report("mail/dkim/" + brand + "/" + args.domain, None)
    elif args.selector is not None:
        r = restclient.get("mail/dkim/" + brand + "/" + args.domain + "/" + args.selector, None)
    else:
        r = restclient.get("mail/dkim/" + brand + "/" + args.domain, None)

    if r.status_code != 200:
        try:
            errors = r.json().get("errors")
        except ValueError:
            errors = None
        title = errors[0].get("title") if errors else None
        if r.status_code == 404:
            print(title or "No DKIM entries found")
        else:
            print("Request failed. (Code: " + str(r.status_code) + ")")
            if title:
                print(title)
        return

    result = r.json()

    if args.dump:
        print(json.dumps(result, indent=4))
        return

    if args.domain is None:
        print("{:<40} {:<45} {:<25}".format("Domain", "Selector", "Activated"))
        for domain, entry in result.items():
            print("{:<40} {:<45} {:<25}".format(
                domain, entry.get("selector", ""), entry.get("activated", "")))
    elif args.status:
        print("{:<45} {:<6} {:<7} {:<10} {:<11}".format(
            "Selector", "DNS", "LDAP", "DNS tries", "LDAP tries"))
        for entry in result:
            state = entry.get("state", {})
            print("{:<45} {:<6} {:<7} {:<10} {:<11}".format(
                entry.get("selector", ""), str(state.get("dns")), str(state.get("ldap")),
                str(state.get("dnsAttempts")), str(state.get("ldapAttempts"))))
    else:
        print("Selector:     ", result.get("selector"))
        print("CNAME target: ", result.get("cname"))
        print("RSA thumbprint:", result.get("rsaThumbPrint"))
        print("Activated:    ", result.get("activated"))


if __name__ == "__main__":
    main()
