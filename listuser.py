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
import requests
import settings
import soapclient


def main():
    parser = argparse.ArgumentParser(
        description='List users in an OX Cloud context.')
    parser.add_argument("-n", dest="context_name", help="Context name.")
    parser.add_argument("-c", "--cid", help="Context ID.", type=int)
    parser.add_argument(
        "-s", "--search", help="Search pattern to limit output.")
    parser.add_argument(
        "--skip-acn", help="Skip extraction of ACN.", action="store_true")
    parser.add_argument("--skip-cos", help="Skip COS.", action="store_true")
    parser.add_argument("--skip-spamlevel",
                        help="Skip spamlevel.", action="store_true")
    parser.add_argument(
        "-d", "--dump", help="Dump raw object.", action="store_true")
    parser.add_argument("--includeguests",
                        help="Include guests.", action="store_true")
    args = parser.parse_args()

    if args.context_name is None and args.cid is None:
        parser.error("Context must be specified by either -n or -c !")

    ctx = {}
    if args.cid is not None:
        ctx["id"] = args.cid
    else:
        ctx["name"] = settings.getCreds()["login"] + "_" + args.context_name

    contextService = soapclient.getService("OXResellerContextService")
    ctx = contextService.getData(ctx, settings.getCreds())

    oxaasService = soapclient.getService("OXaaSService")

    userService = soapclient.getService("OXResellerUserService")
    if args.search is not None:
        users = userService.listCaseInsensitive(
            ctx, "*"+args.search+"*", settings.getCreds())
    else:
        users = userService.listAll(
            ctx, settings.getCreds(), args.includeguests)

    users = userService.getMultipleData(
        ctx, users, settings.getCreds())

    # code.interact(local=locals())
    print("{:<3} {:<40} {:<30} {:<12} {:<12} {:<15} {:<20} {:<15}".format(
        'UID', 'Name', 'Primary email', 'File Quota', 'Mail Quota', 'ACN', 'COS', 'Spamlevel'))

    for user in users:
        cos = '<skipped>'
        acn = "<skipped>"
        spamlevel = '<skipped>'
        # fetching COS via SOAP cannot be trusted therefore use REST below
        # for userAttributes in user.userAttributes.entries:
        #    # find COS in array (currently cloud should only have one entry)
        #    if userAttributes['key'] == 'cloud':
        #        cos = userAttributes['value'].entries[0]['value']

        if not args.dump:

            if user.id != 2:
                if not args.skip_cos:
                    cos = "unset"
                    r = requests.get(settings.getRestHost()+"oxaas/v1/admin/contexts/"+str(
                        ctx.id)+"/users/"+str(user.id)+"/classofservice", auth=(settings.getRestCreds()), verify=settings.getVerifyTls())
                    if r.status_code == 200:
                        if r.json()['classofservice'] != '':
                            cos = r.json()['classofservice']

                if not args.skip_acn:
                    acn = userService.getAccessCombinationName(
                        ctx, user, settings.getCreds())

                if not args.skip_spamlevel:
                    r = requests.get(settings.getRestHost()+"oxaas/v1/admin/contexts/"+str(
                        ctx.id)+"/users/"+str(user.id)+"/spamlevel", auth=(settings.getRestCreds()), verify=settings.getVerifyTls())
                    if r.status_code == 200:
                        if r.json()['spamlevel'] != '':
                            spamlevel = r.json()['spamlevel']
                try:
                    # fails for Guest users w/o LDAP entry
                    mailquota = oxaasService.getMailQuota(
                        ctx.id, user.id, settings.getCreds())
                    # can error if Dovecot has no mailbox/quotausage yet OPS-13238
                    mailquotaUsage = oxaasService.getQuotaUsagePerUser(
                        ctx.id, user.id, settings.getCreds())
                    mailquotaUsage = str(round(mailquotaUsage.storage/1024))
                except:
                    mailquota = "-"
                    mailquotaUsage = "-"
                print("{:<3} {:<40} {:<30} {:<12} {:<12} {:<15} {:<20} {:<15}".format(
                    user.id, user.name, user.primaryEmail, str(user.usedQuota) + "/" + str(user.maxQuota), mailquotaUsage + "/" + str(mailquota), str(acn), ','.join(cos), spamlevel))
            else:
                print("{:<3} {:<40} {:<30} {:<12} {:<12} {:<15} {:<20} {:<15}".format(
                    user.id, user.name, user.primaryEmail, str(user.usedQuota) + "/" + str(user.maxQuota), str(acn), "n/a", "n/a", "n/a"))

        else:
            print(user)


if __name__ == "__main__":
    main()
