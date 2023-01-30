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
import restclient
import settings


def main():
    parser = argparse.ArgumentParser(description='Deletes an OX Cloud user.')
    parser.add_argument("-n", dest="context_name",
                        help="Context name of the user to be deleted.")
    parser.add_argument(
        "-c", "--cid", help="Context ID the user to be deleted.", type=int)
    parser.add_argument("-u", "--userid", help="UID of the guest user to be deleted.")
    parser.add_argument("-e", "--email", help="E-Mail address / login name of the user.")
    #parser.add_argument("--reassign", help="Which userid to reassign shared data. Default=none")
    args = parser.parse_args()

    if args.context_name is None and args.cid is None:
        parser.error("Context must be specified by either -n or -c !")

    if args.userid is None and args.email is None:
        parser.error("User must be specified by either -u or -e !")

    if args.cid is not None:
        params = {"id":args.cid}
    else:
        params = {"name":settings.getCreds()["login"] + "_" + args.context_name}

    #if args.reassign is not None:
    #    reassign = args.reassign
    #else:
    #    reassign = 0
    if args.userid is not None:
        user = args.userid
    else:
        user = args.email

    r = restclient.delete("users/"+user, params)
    if r.status_code == 200:
        print("Deleted user", user, ".")
    else:
        print("Failed to delete user. (Code: "+ str(r.status_code) +")")


if __name__ == "__main__":
    main()
