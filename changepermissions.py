#!/usr/bin/env python3

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
    parser = argparse.ArgumentParser(description='Change service permission for an OX Cloud user.')
    parser.add_argument("-n", dest="context_name",
                        help="Context name the user to be changed.")
    parser.add_argument(
        "-c", "--cid", help="Context ID the user to be changed.", type=int)
    parser.add_argument(
        "-e", "--email", help="E-Mail address / login name of the user.")
    parser.add_argument(
        "-u", "--userid", help="UID of the user to be changed.")
    parser.add_argument(
        "--enable", help="Enable permissions (comma separated) for the user.")
    parser.add_argument(
        "--disable", help="Disable permissions (comma separated) for the user.")
    args = parser.parse_args()

    if args.context_name is None and args.cid is None:
        parser.error("Context must be specified by either -n or -c !")

    if args.userid is None and args.email is None:
        parser.error("User must be specified by either -u or -e !")

    ctx = {}
    if args.cid is not None:
        ctx["id"] = args.cid
    else:
        contextService = soapclient.getService("OXResellerContextService")
        ctx["name"] = settings.getCreds()["login"] + "_" + args.context_name
        ctx = contextService.getData(ctx, settings.getCreds())

    user = {}
    if args.email is not None:
        user["name"] = args.email
        userService = soapclient.getService("OXResellerUserService")
        user = userService.getData(ctx, user, settings.getCreds())
    if args.userid is not None:
        user["id"] = args.userid

    oxaasService = soapclient.getService("OXaaSService")
    if args.enable is not None:
        perms = args.enable.split (",")
        oxaasService.enablePermissions(ctx["id"], user["id"], perms, settings.getCreds())

    if args.disable is not None:
        perms = args.disable.split (",")
        oxaasService.disablePermissions(ctx["id"], user["id"], perms, settings.getCreds())

    print("User permissions for", user["id"], "in context", ctx["id"], ":",
        oxaasService.getPermissions(ctx["id"], user["id"],settings.getCreds()))



if __name__ == "__main__":
    main()
