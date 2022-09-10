#!/usr/bin/python3

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
import random
import settings
import soapclient
import string


def genPasswd(length=10, chars=string.ascii_letters+string.digits):
    return ''.join([random.choice(chars) for i in range(length)])

def main():
    parser = argparse.ArgumentParser(
        description='Creates an OX Cloud reseller admin.')
    parser.add_argument("-u", dest="reseller_name",
                        required=True, help="Reseller name to be created.")
    parser.add_argument("-p", "--password",
                        help="Password for the reseller.", default=genPasswd())
    args = parser.parse_args()

    client = soapclient.getService("OXResellerService")

    # create reseller
    newReseller = {
        "name": args.reseller_name,
        "displayname": args.reseller_name,
        "password": args.password
    }

    reseller = client.create(newReseller, settings.getCreds())

    print("Created reseller:", reseller.id, reseller.name,
          "with password", args.password)


if __name__ == "__main__":
    main()
