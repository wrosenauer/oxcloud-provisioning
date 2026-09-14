#!/usr/bin/env python3

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

VALID_PERMISSIONS = {
    "send": "send",
    "receive": "receive",
    "maillogin": "maillogin",
    "weblogin": "weblogin",
    "editpassword": "editPassword",
}


def parse_user_permissions(value):
    """Turn a comma-separated list of permission names (or 'none') into a full
    Permissions object with every known key explicitly set to True/False."""
    if value.strip().lower() == "none":
        granted = set()
    else:
        names = [v.strip().lower() for v in value.split(",") if v.strip()]
        invalid = sorted(set(names) - VALID_PERMISSIONS.keys())
        if invalid:
            raise ValueError(
                "Invalid permission(s): " + ", ".join(invalid) +
                ". Valid values are: " + ", ".join(sorted(VALID_PERMISSIONS.keys())) +
                ", or 'none'.")
        granted = set(names)
    return {api_key: (name in granted) for name, api_key in VALID_PERMISSIONS.items()}


def main():
    parser = argparse.ArgumentParser(description='Creates an OX Cloud user.')
    parser.add_argument("-n", dest="context_name",
                        help="Context name the user should be created in.")
    parser.add_argument(
        "-c", "--cid", help="Context ID the user should be created in.", type=int)
    parser.add_argument("-e", "--email", required=True,
                        help="E-Mail address / login name of the user.")
    parser.add_argument("-p", "--password", required=True,
                        help="Password for the user.")
    parser.add_argument("-g", "--firstname", required=True,
                        help="First name of the user.")
    parser.add_argument("-s", "--lastname", required=True,
                        help="Last name of the user.")
    parser.add_argument(
        "-l", "--language", help="Initial language of the user. (Default: en_US)", default="en_US")
    parser.add_argument(
        "-t", "--timezone", help="Initial timezone of the user. (Default: Europe/Berlin)", default="Europe/Berlin")
    parser.add_argument("-q", "--unifiedquota", help="Unified quota of the user in MiB", type=int)
    parser.add_argument("--mailquota", help="Mail quota of the user in MiB", type=int)
    parser.add_argument("--filequota", help="Drive quota of the user in MiB", type=int)
    parser.add_argument(
        "--cos", help="The Class of Service for that mailbox. (Default: cloud_pim)", default="cloud_pim")
    parser.add_argument("--editpassword",
                        help="Should the user have the ability to change his password.", action="store_true")
    parser.add_argument(
        "--spamlevel", help="Specify spamlevel to use for the mailbox (no default). Options 'low', 'medium', and 'high'.")
    parser.add_argument(
        "--userpermissions",
        help="Comma-separated list of permissions to grant to the user. Valid values: "
             "send, receive, maillogin, weblogin, editpassword. This always represents the "
             "full set of granted permissions - any permission not listed is explicitly "
             "disabled. Use 'none' to grant no permissions. Cannot be combined with --editpassword.")
    args = parser.parse_args()

    if args.context_name is None and args.cid is None:
        parser.error("Context must be specified by either -n or -c !")

    if args.unifiedquota is not None and args.mailquota is not None:
        parser.error("Either unified or separate quote is allowed.")
    if args.mailquota is not None and args.filequota is None:
        parser.error("Separate quotas need mail and file quota defined.")
    if args.userpermissions is not None and args.editpassword:
        parser.error("--userpermissions cannot be combined with --editpassword; "
                    "include 'editpassword' in the --userpermissions list instead.")

    if args.cid is not None:
        params = {"id":args.cid}
    else:
        params = {"name":settings.getCreds()["login"] + "_" + args.context_name}

    # prepare user
    user = {
        "name": args.email,
        "password": args.password,
        "displayName": args.firstname + " " + args.lastname,
        "surName": args.lastname,
        "givenName": args.firstname,
        "mail": args.email,
        "language": args.language,
        "timezone": args.timezone,
        "classOfService": args.cos.split(",")
    }
    if args.spamlevel:
        user["spamLevel"] = args.spamlevel
    if args.unifiedquota is not None:
        user["unifiedQuota"] = args.unifiedquota
    else:
        if args.mailquota is not None:
            user["mailQuota"] = args.mailquota
            user["fileQuota"] = args.filequota
    if args.userpermissions is not None:
        try:
            user["userPermissions"] = parse_user_permissions(args.userpermissions)
        except ValueError as e:
            parser.error(str(e))
    elif args.editpassword:
        user["userPermissions"] = {"editPassword": True}

    r = restclient.post("users", user, params)
    if r.status_code == 200:
        result = r.json()
        print("Created user:", result["name"], "with password", args.password)
    else:
        print("Failed to create user. (Code: "+ str(r.status_code) +")")
        print(r.json())



if __name__ == "__main__":
    main()
