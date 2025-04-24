#!/usr/bin/env python3

# Copyright (C) 2022-2025 OX Software GmbH
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
import requests
import settings


def main():
    parser = argparse.ArgumentParser(
        description='Manage OX Cloud mailforwarders.')
    subparsers = parser.add_subparsers(title="subcommands",
                                       description="valid subcommands",
                                       required=True,
                                       help="Subcommand help")
    parser_create = subparsers.add_parser("create", help="Create (or overwrite) a forwarder")
    parser_create.add_argument(
        "-c", "--context", help="Context ID or name for forward", required=True)
    parser_create.add_argument(
        "-a", "--alias", help="The alias/forward address to be created.", required=True)
    parser_create.add_argument(
        "-t", "--target", help="The target address(es) (comma separated if multiple)", required=True)
    parser_create.set_defaults(func=create)

    parser_update = subparsers.add_parser("update", help="Add recipient to a forwarder")
    parser_update.add_argument(
        "-c", "--context", help="Context ID or name the forward should be updated in.", required=True)
    parser_update.add_argument(
        "-a", "--alias", help="The alias/forward address to be extended.", required=True)
    parser_update.add_argument(
        "-t", "--target", help="The to be added target address", required=True)
    parser_update.set_defaults(func=update_target)

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
        args.context = { "id": cid }
    except:
        args.context = { "name": settings.getCreds()["login"] + "_" + args.context }

    args.func(args)


def create(args):
    data = { "address": args.alias,
             "forwardTo": [args.target] }
    r = requests.post(settings.getRestHost()+"cloudapi/v2/mail/forwards/", params=args.context,
                      auth=(settings.getRestCreds()), json=data, verify=settings.getVerifyTls())
    if r.status_code == 200:
        print("Created forwarder", args.alias,
              "to", args.target, "in context", args.context)
    else:
        if r.status_code == 204:
            print("Forwarder already exists!")
        else:
            print("Failed to create forwarder!")
            r.raise_for_status()

def update_target(args):
    data = { "recipient":args.target }
    r = requests.put(settings.getRestHost()+"cloudapi/v2/mail/forwards/"+str( 
        args.context)+"/"+str(args.alias), auth=(settings.getRestCreds()), json=data, verify=settings.getVerifyTls())
    if r.status_code == 201:
        print("Updated forwarder", args.alias,
              "to", args.target, "in context", args.context)
    else:
        print("Failed to update forwarder!")
        r.raise_for_status()

def delete(args):
    if args.alias is not None:
        r = requests.delete(settings.getRestHost()+"cloudapi/v2/mail/forwards/"+str(args.context)+"/"+str(args.alias),
                            auth=(settings.getRestCreds()), verify=settings.getVerifyTls())
    else:
        if args.all:
            r = requests.delete(settings.getRestHost()+"api/oxaas/v1/admin/forwards/"+str(args.context),
                                auth=(settings.getRestCreds()), verify=settings.getVerifyTls())
    if r.ok:
        if args.all:
            print("Deleted all forwarders from context")
        else:
            print("Deleted forwarder", args.alias)
    else:
        r.raise_for_status()


def list(args):
    r = requests.get(settings.getRestHost()+"cloudapi/v2/mail/forwards/", params=args.context,
                     auth=(settings.getRestCreds()), verify=settings.getVerifyTls())
    print(r.json())


if __name__ == "__main__":
    main()
