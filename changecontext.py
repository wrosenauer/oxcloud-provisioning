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
import restclient
import settings
import sys


def main():
    parser = argparse.ArgumentParser(
        description='Changes an OX Cloud context.')
    parser.add_argument("-n", dest="context_name", help="Context name to be changed.")
    parser.add_argument(
        "-c", "--cid", help="Context ID to be changed.", type=int)
    parser.add_argument(
        "-q", "--quota", help="New quota of the context in MiB", type=int)
    args = parser.parse_args()

    if args.context_name is None and args.cid is None:
        parser.error("Context must be specified by either -n or -c !")

    if args.cid is not None:
        ctx = str(args.cid)
    else:
        ctx = settings.getCreds()["login"] + "_" + args.context_name

    if args.quota is None:
        print("No quota given, no change performed")
        sys.exit()

    data = {"maxQuota": args.quota}
    r = restclient.put("contexts/"+ctx, data)
    if r.status_code == 200:
        print("Changed context", ctx)
    else:
        if r.status_code == 404:
            print("Context not found.")
        else:
            print("Failed to change context. (Code: "+ str(r.status_code) +")")

if __name__ == "__main__":
    main()
