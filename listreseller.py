#!/usr/bin/env python3

# Copyright (C) 2022  OX Software GmbH
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
import settings
import soapclient


def main():
    parser = argparse.ArgumentParser(
        description='Lists all OX Cloud reseller admins.')
    parser.add_argument("-s", "--searchpattern", help="The search pattern which is used for listing.")
    args = parser.parse_args()

    client = soapclient.getService("OXResellerService")

    if args.searchpattern is not None:
        search = "*" + args.searchpattern + "*"
    else:
        search = "*"

    resellers = client.list(search, settings.getCreds())

    for reseller in resellers:
        print (reseller['name'])


if __name__ == "__main__":
    main()
