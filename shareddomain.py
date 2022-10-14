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
import requests
import settings


def main():
    parser = argparse.ArgumentParser(
        description='Manage OX Cloud shared domains.')
    subparsers = parser.add_subparsers(title="subcommands",
                                       description="valid subcommands",
                                       required=True,
                                       help="Subcommand help")
    parser_create = subparsers.add_parser(
        "create", help="Create a shared domain.")
    parser_create.add_argument(
        "-d", "--domain", help="Domain to be created as shared.", required=True)
    parser_create.set_defaults(func=create)

    parser_delete = subparsers.add_parser(
        "delete", help="Deletes a shared domain.")
    parser_delete.add_argument(
        "-d", "--domain", help="Domain to be deleted", required=True)
    parser_delete.set_defaults(func=delete)

    parser_list = subparsers.add_parser("list", help="List shared domains")
    parser_list.set_defaults(func=list)
    args = parser.parse_args()

    args.func(args)


def create(args):
    r = requests.post(settings.getRestHost()+"api/oxaas/v1/admin/sharedmaildomains/"+str(
        args.domain), auth=(settings.getRestCreds()), verify=settings.getVerifyTls())
    print(r.status_code)
    if r.status_code == 200:
        print("Created shared domain", args.domain)
    else:
        print("Failed to create shared domain!")
        r.raise_for_status()


def delete(args):
    r = requests.delete(settings.getRestHost()+"api/oxaas/v1/admin/sharedmaildomains/"+str(args.domain),
                        auth=(settings.getRestCreds()), verify=settings.getVerifyTls())
    if r.ok:
        print("Deleted shared domain")
    else:
        r.raise_for_status()


def list(args):
    r = requests.get(settings.getRestHost()+"api/oxaas/v1/admin/sharedmaildomains/*",
                     auth=(settings.getRestCreds()), verify=settings.getVerifyTls())
    print(r.json())


if __name__ == "__main__":
    main()
