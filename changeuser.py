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
from os.path import exists


def main():
    parser = argparse.ArgumentParser(description='Change an OX Cloud user.')
    parser.add_argument("-n", dest="context_name",
                        help="Context name the user to be changed.")
    parser.add_argument(
        "-c", "--cid", help="Context ID the user to be changed.", type=int)
    parser.add_argument(
        "-e", "--email", help="E-Mail address / login name of the user.", required=True)
    parser.add_argument("--aliases", help="Comma-separated list of aliases.")
    parser.add_argument("--newmail", help="New primary mail address")
    parser.add_argument("-p", "--password", help="New Password for the user.")
    parser.add_argument("-g", "--firstname",
                        help="New first name of the user.")
    parser.add_argument("-s", "--lastname", help="New last name of the user.")
    parser.add_argument("-l", "--language", help="New language of the user.")
    parser.add_argument("-t", "--timezone", help="New timezone of the user.")
    parser.add_argument("-q", "--unifiedquota", help="Unified quota of the user in MiB", type=int)
    parser.add_argument("--mailquota", help="Mail quota of the user in MiB", type=int)
    parser.add_argument("--drivequota", help="Drive quota of the user in MiB", type=int)
    parser.add_argument("--cos", help="The Class of Service for that mailbox.")
    parser.add_argument("--editpassword",
                        help="Should the user have the ability to change his password", type=bool)
    parser.add_argument(
        "--spamlevel", help="Specify spamlevel to use for the mailbox (no default). Options 'low', 'medium', and 'high'.")
    parser.add_argument(
        "--disable", help="Disable the user.", action="store_true")
    parser.add_argument("--enable", help="Enable the user.",
                        action="store_true")
    args = parser.parse_args()

    if args.context_name is None and args.cid is None:
        parser.error("Context must be specified by either -n or -c !")
    
    if args.unifiedquota is not None and args.mailQuota is not None:
        parser.error("Either unified or separate quote is allowed.")
    if args.mailQuota is not None and args.fileQuota is None:
        parser.error("Separate quotas need mail and file quota defined.")

    if args.cid is not None:
        params = {"id":args.cid}
    else:
        params = {"name":settings.getCreds()["login"] + "_" + args.context_name}

    changeuser = {}

    if args.password is not None:
        changeuser["password"] = args.password
    if args.firstname is not None:
        changeuser["givenName"] = args.firstname
    if args.lastname is not None:
        changeuser["surName"] = args.lastname
    if args.language is not None:
        changeuser["language"] = args.language
    if args.aliases is not None:
        changeuser["aliases"] = args.aliases.split(',')
    if args.newmail is not None:
        changeuser["newName"] = args.newmail
        changeuser["mail"] = args.newmail
    if args.timezone is not None:
        changeuser["timezone"] = args.timezone
    if args.cos:
        changeuser["classOfService"] = [args.cos]
        changeuser["accessCombinationName"] = args.cos
    if args.spamlevel:
        changeuser["spamLevel"] = args.spamlevel
    if args.unifiedquota is not None:
        changeuser["unifiedQuota"] = args.unifiedquota
    else:
        if args.mailquota is not None:
            changeuser["mailQuota"] = args.mailquota
            changeuser["fileQuota"] = args.drivequota

    r = restclient.put("users/"+args.email, changeuser, params)
    if r.status_code == 200:
        print("Changed user")
    else:
        if r.status_code == 404:
            print("User not found.")
        else:
            print("Failed to change user. (Code: "+ str(r.status_code) +")")

    # handle permissions
    permissions = {}
    if args.disable:
        permissions["weblogin"] = False
    if args.enable:
        permissions["weblogin"] = True
    if args.editpassword is not None:
        permissions["editPassword"] = args.editpassword

    if bool(permissions) is not False:
        r = restclient.put("users/"+args.email+"/permissions", permissions, params)
        if r.status_code == 200:
            print("Changed user permissions")
        else:
            if r.status_code == 404:
                print("User not found.")
            else:
                print("Failed to change user permissions. (Code: "+ str(r.status_code) +")")


if __name__ == "__main__":
    main()
