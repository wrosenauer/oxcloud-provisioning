#!/usr/bin/python3

# Copyright (C) 2023-2025 OX Software GmbH
#                         Wolfgang Rosenauer
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
import sys


def main():
    parser = argparse.ArgumentParser(
        description='List (or checks) contexts of an OX Cloud reseller.')
    parser.add_argument("-s", "--searchpattern",
                        help="The search pattern which is used for listing.")
    parser.add_argument(
        "--exists", help="Check for context existance (use with -c or -n).", action="store_true")
    parser.add_argument("-c", "--cid", help="Context ID (only for exists check).", type=int)
    parser.add_argument("-n", dest="context_name", help="Context name. (only for exists check)")
    parser.add_argument(
        "--long", help="Verbose output (incl. settings).", action="store_true")
    parser.add_argument("-d", "--dump", help="Dump raw JSON response.", action="store_true")
    args = parser.parse_args()

    if args.exists is True:
        if args.context_name is None and args.cid is None:
            parser.error("Context must be specified by either -n or -c !")

        if args.cid is not None:
            ctx = str(args.cid)
        else:
            ctx = settings.getCreds()["login"] + "_" + args.context_name

        exists = restclient.get("contexts/" + ctx, None)
        if exists.status_code == 200:
            print("The context exists!")
        else:
            print("The context does not exist!")
    else:
        if args.searchpattern is not None:
            search = {"pattern": "*" + args.searchpattern + "*"}
        else:
            search = None

        r = restclient.get("contexts", search)
        if r.status_code != 200:
            print("Request failed (Code: " + str(r.status_code) + ")")
            sys.exit(1)

        contexts = r.json()

        if not args.dump:
            print("{:<60} {:<10}".format(
                'Name', 'Quota'))
            for context in contexts:
                print("{:<60} {:<10}".format(context["name"], str(context["usedQuota"]) + "/" + str(
                    context.get("maxQuota", "unlimited"))))
                if not args.long:
                    continue
                if context.get("theme") is not None:
                    print (context["theme"])
        else:
            # fetch data per context
            for context in contexts:
                r = restclient.get("contexts/" + context["name"], "includebrand=true")
                print(r.request.url)
                print(r.json())

if __name__ == "__main__":
    main()
