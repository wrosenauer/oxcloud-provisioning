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
        description='Removes per maildomain DKIM entries for an OX Cloud maildomain.')
    parser.add_argument("-d", "--domain", required=True,
                        help="Maildomain to remove DKIM entries for.")
    args = parser.parse_args()

    brand = settings.getCreds()["login"]

    r = restclient.delete("mail/dkim/" + brand + "/" + args.domain, None)
    if r.status_code == 200:
        print("Deleted DKIM entries for domain", args.domain)
    elif r.status_code == 404:
        print("No DKIM entries found for domain", args.domain)
    else:
        print("Failed to delete DKIM entries. (Code: " + str(r.status_code) + ")")


if __name__ == "__main__":
    main()
