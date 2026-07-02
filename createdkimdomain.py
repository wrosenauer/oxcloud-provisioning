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
import restclient
import settings


def main():
    parser = argparse.ArgumentParser(
        description='Enables per maildomain DKIM signing for an OX Cloud maildomain.')
    parser.add_argument("-d", "--domain", required=True,
                        help="Maildomain to enable DKIM signing for.")
    args = parser.parse_args()

    brand = settings.getCreds()["login"]

    r = restclient.put("mail/dkim/" + brand + "/" + args.domain, None, None)
    if r.status_code == 200:
        entry = r.json()
        print("Created DKIM entry for domain", args.domain)
        print("Selector:   ", entry.get("selector"))
        print("CNAME target:", entry.get("cname"))
        print("\nCreate a CNAME record for", entry.get("selector"),
              "pointing to", entry.get("cname"))
        print("A second selector will be generated automatically to support key rotation.")
    else:
        title = errorTitle(r)
        if r.status_code == 404:
            print("Failed to create DKIM entry:", title or "Domain not found")
            print("At least one user with an email address for this domain must "
                  "exist, or it must be a shared maildomain.")
        elif r.status_code == 409:
            print("Failed to create DKIM entry:", title or "Domain already configured")
        else:
            print("Failed to create DKIM entry. (Code: " + str(r.status_code) + ")")
            if title:
                print(title)


def errorTitle(r):
    try:
        errors = r.json().get("errors")
    except ValueError:
        return None
    if errors:
        return errors[0].get("title")
    return None


if __name__ == "__main__":
    main()
