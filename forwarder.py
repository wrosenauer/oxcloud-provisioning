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

import settings
import argparse
import requests


def main():
    parser = argparse.ArgumentParser(
        description='Manage OX Cloud mailforwarders.')
    subparsers = parser.add_subparsers(title="subcommands",
                                       description="valid subcommands",
                                       required=True,
                                       help="Subcommand help")
    parser_create = subparsers.add_parser("create", help="Create a forwarder")
    parser_create.add_argument(
        "-c", "--context", help="Context ID or name the forward should be created in.", required=True)
    parser_create.add_argument(
        "-a", "--alias", help="The alias/forward address to be created.", required=True)
    parser_create.add_argument(
        "-t", "--target", help="The target address(es) (comma separted if multiple)", required=True)
    parser_create.set_defaults(func=create)

    parser_delete = subparsers.add_parser("delete", help="Delete a forwarder")
    parser_delete.add_argument(
        "-c", "--context", help="Context ID or name", required=True)
    parser_delete.add_argument(
        "-a", "--alias", help="The alias/forward address to be deleted.")
    parser_delete.add_argument(
        "--all", help="Deletes all forwarders from context.", default=False, action='store_true')
    parser_delete.set_defaults(func=delete)

    parser_list = subparsers.add_parser("list", help="List forwarders")
    parser_list.add_argument(
        "-c", "--context", help="Context id or name", required=True)
    parser_list.set_defaults(func=list)
    args = parser.parse_args()

    try:
        cid = int(args.context)
        args.context = cid
    except:
        args.context = settings.getCreds()["login"] + "_" + args.context
    args.func(args)


def create(args):
    data = args.target.split(",")
    r = requests.post(settings.getRestHost()+"api/oxaas/v1/admin/forwards/"+str(
        args.context)+"/"+str(args.alias), auth=(settings.getRestCreds()), json=data)
    if r.status_code == 201:
        print("Created forwarder", args.alias,
              "to", args.target, "in context", args.context)
    else:
        if r.status_code == 204:
            print("Forwarder already exists!")
        else:
            print("Failed to create forwarder!")
            r.raise_for_status()


def delete(args):
    if args.alias is not None:
        r = requests.delete(settings.getRestHost()+"api/oxaas/v1/admin/forwards/"+str(args.context)+"/"+str(args.alias),
                            auth=(settings.getRestCreds()))
    else:
        if args.all:
            r = requests.delete(settings.getRestHost()+"api/oxaas/v1/admin/forwards/"+str(args.context),
                                auth=(settings.getRestCreds()))
    if r.ok:
        if args.all:
            print("Deleted all forwarders from context")
        else:
            print("Deleted forwarder", args.alias)
    else:
        r.raise_for_status()

def list(args):
    r = requests.get(settings.getRestHost()+"api/oxaas/v1/admin/forwards/"+str(args.context),
                     auth=(settings.getRestCreds()))
    print(r.json())


if __name__ == "__main__":
    main()
