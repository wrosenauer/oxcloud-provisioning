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
import settings
import soapclient


def main():
    parser = argparse.ArgumentParser(
        description='List (or checks) contexts of an OX Cloud reseller.')
    parser.add_argument("-s", "--searchpattern", help="The search pattern which is used for listing.")
    parser.add_argument("--exists", help="Check for context existance (use with -c or -n).", action="store_true")
    parser.add_argument("-c", "--cid", help="Context ID.", type=int)
    parser.add_argument("-n", dest="context_name", help="Context name.")
    parser.add_argument("--long", help="Verbose output (incl. settings).", action="store_true")
    args = parser.parse_args()

    client = soapclient.getService("OXResellerContextService")

    if args.exists is True:
        if args.context_name is None and args.cid is None:
            parser.error("Context must be specified by either -n or -c !")

        ctx = {}
        if args.cid is not None:
            ctx["id"] = args.cid
        else:
            ctx["name"] = settings.getCreds()["login"] + "_" + args.context_name

        exists = client.exists(ctx, settings.getCreds())
        # this might throw exceptions which should be handled gracefully (NB: ->exists is currently broken with MWB-1774)
        if exists is True:
            print("The context exists!")
        else:
            print("The context does not exist!")
    else:
        if args.searchpattern is not None:
            search = "*" + args.searchpattern + "*"
        else:
            search = "*"

        contexts = client.list(search, settings.getCreds())

        if not args.long:
            print ("{:<7} {:<40} {:<10}".format('CID', 'Name', 'maxQuota'))
            for context in contexts:
                print ("{:<7} {:<40} {:<10}".format(context.id, context.name, str(context.maxQuota)))
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
