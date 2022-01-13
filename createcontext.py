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

import sys
import string
import random
from zeep import Client
import settings
import argparse

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

    client = Client(settings.getHost()+"OXResellerContextService?wsdl")

    # check if a context with that name already exists
    context = client.service.list(
        settings.getCreds()["login"] + "_" + args.context_name, settings.getCreds())
    if (context):
        for ctx in context:
            print("Context", ctx.name, "already exists:", ctx.id)
        sys.exit(1)

    # create context
    newContext = {
        "name": settings.getCreds()["login"] + "_" + args.context_name,
        "maxQuota": args.quota
    }
    adminUser = {
        "name": "admin@"+args.context_name,
        "password": args.password,
        "display_name": "admin",
        "sur_name": args.context_name,
        "given_name": "admin",
        "primaryEmail": "admin@"+args.context_name,
        "email1": "admin@"+args.context_name
    }

    # we need some userAttributes, e.g. support string and dynamic theme
    # in most cases meanwhile should be set on the reselleradmin
    if args.supportcontact:
        supportAttributes = [
            {
                "key": "com.openexchange.appsuite.servercontact",
                "value": args.supportcontact
            }
        ]

        newContext["userAttributes"] = {"entries": [
            {"key": "config", "value": {"entries": supportAttributes}}]}

    context = client.service.createModuleAccessByName(
        newContext, adminUser, args.access_combination, settings.getCreds())

    print("Created context:", context.id, context.name,
          "with password", args.password, "and quota", args.quota)


if __name__ == "__main__":
    main()
