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
import restclient
import string

def genPasswd(length=10, chars=string.ascii_letters+string.digits):
    return ''.join([random.choice(chars) for i in range(length)])

def main():
    parser = argparse.ArgumentParser(
        description='Creates an OX Cloud context.')
    parser.add_argument("-n", dest="context_name",
                        required=True, help="Context name to be created.")
    parser.add_argument("-p", "--password",
                        help="Password for the user.", default=genPasswd())
    parser.add_argument("-q", "--quota", default=1024,
                        help="Quota of the context in MiB", type=int)
    parser.add_argument("-a", "--access-combination",
                        default="cloud_pim", help="Default access-combination")
    parser.add_argument("--supportcontact",
                        help="Contact information for about dialog")
    args = parser.parse_args()

    data = { "name": args.context_name,
             "maxQuota": args.quota,
             "adminPassword": args.password,
             "accessCombinationName": args.access_combination
           }
    if args.supportcontact is not None:
        data["theme"] = { "serverContact": args.supportcontact }

    r = restclient.post("contexts", data)
    if r.status_code == 200:
        result = r.json()
        print("Created context:", result["id"], " (", result["name"], ") ",
              "with password", args.password, "and quota", result["maxQuota"])
    else:
        if r.status_code == 409:
            print("Context with that name already exists.")
        else:
            print("Failed to create context. (Code: "+ str(r.status_code) +")")


if __name__ == "__main__":
    main()
