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

from zeep import Client
import requests
import settings
import argparse
#import code


def main():
    parser = argparse.ArgumentParser(
        description='List users in an OX Cloud context.')
    parser.add_argument("-n", dest="context_name", help="Context name.")
    parser.add_argument("-c", "--cid", help="Context ID.", type=int)
    parser.add_argument(
        "--skip-acn", help="Skip extraction of ACN.", action="store_true")
    parser.add_argument("--skip-cos", help="Skip COS.", action="store_true")
    args = parser.parse_args()

    if args.context_name is None and args.cid is None:
        parser.error("Context must be specified by either -n or -c !")

    ctx = {}
    if args.cid is not None:
        ctx["id"] = args.cid
    else:
        ctx["name"] = settings.getCreds()["login"] + "_" + args.context_name

    contextService = Client(settings.getHost()+"OXResellerContextService?wsdl")
    ctx = contextService.service.getData(ctx, settings.getCreds())

    userService = Client(settings.getHost()+"OXResellerUserService?wsdl")
    users = userService.service.listAll(ctx, settings.getCreds())
    users = userService.service.getMultipleData(
        ctx, users, settings.getCreds())

    #code.interact(local=locals())
    print("{:<3} {:<30} {:<10} {:<30} {:<30}".format(
        'UID', 'Name', 'Quota', 'ACN', 'COS'))

    for user in users:
        cos = '<skipped>'
        acn = "<skipped>"
        # fetching COS via SOAP cannot be trusted therefore use REST below
        # for userAttributes in user.userAttributes.entries:
        #    # find COS in array (currently cloud should only have one entry)
        #    if userAttributes['key'] == 'cloud':
        #        cos = userAttributes['value'].entries[0]['value']

        if user.id != 2:
            if not args.skip_cos:
                cos = 'unset'
                r = requests.get(settings.getRestHost()+"oxaas/v1/admin/contexts/"+str(
                    ctx.id)+"/users/"+str(user.id)+"/classofservice", auth=(settings.getRestCreds()))
                if r.status_code == 200:
                    if r.json()['classofservice'] != '':
                        cos = r.json()['classofservice']

            if not args.skip_acn:
                acn = userService.service.getAccessCombinationName(
                    ctx, user, settings.getCreds())

        print("{:<3} {:<30} {:<10} {:<30} {:<30}".format(
            user.id, user.name, str(user.usedQuota) + "/" + str(user.maxQuota), acn, cos))


if __name__ == "__main__":
    main()
