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
import json
import requests
import settings


def main():
    parser = argparse.ArgumentParser(
        description='Manage OX Cloud announcements.')
    subparsers = parser.add_subparsers(title="subcommands",
                                       description="valid subcommands",
                                       required=True,
                                       help="Subcommand help")
    parser_create = subparsers.add_parser(
        "create", help="Create an announcement.")
    parser_create.add_argument(
        "-f", "--file", help="Create announcement from file.", required=True)
    parser_create.set_defaults(func=create)

    parser_delete = subparsers.add_parser(
        "delete", help="Deletes an announcement.")
    parser_delete.add_argument(
        "-i", "--id", help="Announcement ID to be deleted", required=True)
    parser_delete.set_defaults(func=delete)

    parser_list = subparsers.add_parser("list", help="List announcements")
    parser_list.add_argument(
        "-i", "--id", help="Announcement ID to be listed", required=False)
    parser_list.set_defaults(func=list)

    parser_enable = subparsers.add_parser("enable", help="Enable announcement")
    parser_enable.add_argument(
        "-i", "--id", help="Announcement ID to be enabled.", required=True)
    parser_enable.set_defaults(func=enable)

    parser_disable = subparsers.add_parser(
        "disable", help="Disable announcement")
    parser_disable.add_argument(
        "-i", "--id", help="Announcement ID to be disabled.", required=True)
    parser_disable.set_defaults(func=disable)

    args = parser.parse_args()
    args.func(args)


def create(args):
    jsonContent = open(args.file, 'rb').read()
    r = requests.post(settings.getRestHost()+"api/oxaas/v1/admin/announcements",
                      data=jsonContent, auth=(settings.getRestCreds()), verify=settings.getVerifyTls())
    if r.ok:
        print("Created announcement.")
    else:
        print("Failed to create announcement!")
        r.raise_for_status()


def delete(args):
    r = requests.delete(settings.getRestHost()+"api/oxaas/v1/admin/announcements/"+str(args.id),
                        auth=(settings.getRestCreds()), verify=settings.getVerifyTls())
    if r.ok:
        print("Deleted announcement")
    else:
        r.raise_for_status()


def list(args):
    r = requests.get(settings.getRestHost()+"api/oxaas/v1/admin/announcements/*",
                     auth=(settings.getRestCreds()), verify=settings.getVerifyTls())
    if r.ok:
        contentType = r.headers.get('Content-Type')
        if contentType is not None and contentType.startswith('application/json'):
            if args.id is None:
                print(json.dumps(r.json(), indent=4))
            else:
                input_dict = json.loads(r.text)
                output_dict = [
                    x for x in input_dict if x['id'] == int(args.id)]
                print(json.dumps(output_dict, indent=4))
        else:
            print("No announcements found.")
    else:
        r.raise_for_status()


def enable(args):
    r = requests.put(settings.getRestHost()+"api/oxaas/v1/admin/announcements/enable/"+str(args.id),
                     auth=(settings.getRestCreds()), verify=settings.getVerifyTls())
    if r.ok:
        print("Enabled announcement")
    else:
        r.raise_for_status()


def disable(args):
    r = requests.put(settings.getRestHost()+"api/oxaas/v1/admin/announcements/disable/"+str(args.id),
                     auth=(settings.getRestCreds()), verify=settings.getVerifyTls())
    if r.ok:
        print("Disabled announcement")
    else:
        r.raise_for_status()


if __name__ == "__main__":
    main()
