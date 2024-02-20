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
import requests
import settings


def main():
    parser = argparse.ArgumentParser(
        description='Close context sessions in OX Cloud.')
    parser.add_argument("-n", dest="context_name", help="Context name.")
    parser.add_argument("-c", "--cid", help="Context ID.", type=int)
    parser.add_argument("-u", "--user", help="User name", required=False)
    args = parser.parse_args()

    if args.context_name is None and args.cid is None:
        parser.error("Context must be specified by either -n or -c !")

    if args.context_name is None:
        params = {"contextId": args.cid}
    else:
        params = {"contextName": args.context_name}

    if args.user is not None:
        params.update = {"userName": args.user}

    r = requests.delete(settings.getRestHost()+"oxaas/v1/admin/sessions/",
                        params=params, auth=(settings.getRestCreds()), verify=settings.getVerifyTls())
    if r.status_code == 200:
        print(r.json())
    else:
        print("Request failed")
        r.raise_for_status()


if __name__ == "__main__":
    main()
