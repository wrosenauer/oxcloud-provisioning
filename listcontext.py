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

from zeep import Client
import argparse
import settings

def main():
    parser = argparse.ArgumentParser(
        description='List contexts of an OX Cloud reseller.')
    parser.add_argument("-s", "--searchpattern", help="The search pattern which is used for listing.")
    parser.add_argument("--long", help="Verbose output (incl. settings).", action="store_true")
    args = parser.parse_args()

    client = Client(settings.getHost()+"OXResellerContextService?wsdl")

    if args.searchpattern is not None:
        search = "*" + args.searchpattern + "*"
    else:
        search = "*"

    contexts = client.service.list(search, settings.getCreds())

    if not args.long:
        print ("{:<7} {:<40} {:<10}".format('CID', 'Name', 'maxQuota'))
        for context in contexts:
            print ("{:<7} {:<40} {:<10}".format(context.id, context.name, context.maxQuota))
    else:
        print("{:<7} {:<40} {:<10}".format('CID', 'Name', 'Quota'))
        for context in contexts:
            print("{:<7} {:<40} {:<10}".format(
                context.id, context.name, str(context.usedQuota) + "/" + str(context.maxQuota)))
            
            for entries in context.userAttributes.entries:
                if entries.key == 'config':
                    print ("Configuration")
                    for prop in entries.value.entries:
                        print (prop.key, ":", prop.value)
                    print ("\n")


if __name__ == "__main__":
    main()
