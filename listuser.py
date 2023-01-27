#!/usr/bin/python3

# Copyright (C) 2023  OX Software GmbH
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
        description='List users in an OX Cloud context.')
    parser.add_argument("-n", dest="context_name", help="Context name.")
    parser.add_argument("-c", "--cid", help="Context ID.", type=int)
    parser.add_argument(
        "-s", "--search", help="Search pattern to limit output.")
    parser.add_argument(
        "--skip-acn", help="Skip extraction of ACN.", action="store_true")
    parser.add_argument("--skip-cos", help="Skip COS.", action="store_true")
    parser.add_argument("--skip-spamlevel",
                        help="Skip spamlevel.", action="store_true")
    parser.add_argument(
        "-d", "--dump", help="Dump raw object.", action="store_true")
    parser.add_argument("--includeguests",
                        help="Include guests.", action="store_true")
    args = parser.parse_args()

    if args.context_name is None and args.cid is None:
        parser.error("Context must be specified by either -n or -c !")

    if args.cid is not None:
        params = {"id":args.cid}
    else:
        params = {"name":settings.getCreds()["login"] + "_" + args.context_name}

    if args.search is not None:
        params["pattern"] = "*"+args.search+"*"

    params["includeguests"] = args.includeguests

    r = restclient.get("users", params)
    users = r.json()

    if not args.dump:
        print("{:<40} {:<30} {:<12} {:<20} {:<15} {:<3}".format(
            'Name', 'Email', 'Unified Quota', 'COS', 'Spamlevel', 'Guest ID'))

    for user in users:
        # skip for context admin
        cos = user["classOfService"] if user.get("classOfService") is not None else "<none>"
        spamlevel = user["spamLevel"] if user.get("spamLevel") is not None else "<none>"
        usedQuota = user["usedQuota"] if user.get("usedQuota") is not None else "BUG"

        if not args.dump:

            if user.get("guest") is not None:
                print("{:<40} {:<30} {:<12} {:<20} {:<15} {:<3}".format(user["name"], "n/a", "n/a", "n/a", "n/a", user["guest"]["id"]))
            else:
                print("{:<40} {:<30} {:<12} {:<20} {:<15} {:<3}".format(
                    user["name"], user["mail"], str(usedQuota) + "/" + str(user["unifiedQuota"]), cos, spamlevel, "-"))

        else:
            print (json.dumps(user, indent=4))


if __name__ == "__main__":
    main()
