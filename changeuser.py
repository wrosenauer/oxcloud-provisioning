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
import json
import re
import requests
import settings
import soapclient


def main():
    parser = argparse.ArgumentParser(description='Change an OX Cloud user.')
    parser.add_argument("-n", dest="context_name",
                        help="Context name the user to be changed.")
    parser.add_argument(
        "-c", "--cid", help="Context ID the user to be changed.", type=int)
    parser.add_argument(
        "-e", "--email", help="E-Mail address / login name of the user.")
    parser.add_argument(
        "-u", "--userid", help="UID of the user to be changed.")
    parser.add_argument("--aliases", help="Comma-separated list of aliases.")
    parser.add_argument("--newmail", help="New primary mail address")
    parser.add_argument("-p", "--password", help="New Password for the user.")
    parser.add_argument("-g", "--firstname",
                        help="New first name of the user.")
    parser.add_argument("-s", "--lastname", help="New last name of the user.")
    parser.add_argument("-l", "--language", help="New language of the user.")
    parser.add_argument("-t", "--timezone", help="New timezone of the user.")
    parser.add_argument(
        "-q", "--quota", help="New quota of the user in MiB (-1 for unlimited)", type=int)
    parser.add_argument("-a", "--access_combination",
                        help="New access combination name for the user.")
    parser.add_argument("--cos", help="The Class of Service for that mailbox.")
    parser.add_argument("--editpassword",
                        help="Should the user have the ability to change his password", type=bool)
    parser.add_argument(
        "--guard", help="Enable/disable Guard for the user.", type=bool)
    parser.add_argument(
        "--safeunsubscribe", help="Enable/disable the SafeUnsubscribe feature for the user.", type=bool)
    parser.add_argument(
        "--antiphishing", help="Enable/disable the ToC antiphishing feature.", type=bool)
    parser.add_argument(
        "--spamlevel", help="Specify spamlevel to use for the mailbox (no default). Options 'low', 'medium', and 'high'.")
    parser.add_argument(
        "--config", help="Additional config properties including in format PROPERTY=VALUE")
    parser.add_argument(
        "--disable", help="Disable the user.", action="store_true")
    parser.add_argument("--enable", help="Enable the user.",
                        action="store_true")
    parser.add_argument(
        "--dump", help="Dump XML request/response to file.", action="store_true")
    args = parser.parse_args()

    if args.context_name is None and args.cid is None:
        parser.error("Context must be specified by either -n or -c !")

    if args.userid is None and args.email is None:
        parser.error("User must be specified by either -u or -e !")

    ctx = {}
    if args.cid is not None:
        ctx["id"] = args.cid
    else:
        ctx["name"] = settings.getCreds()["login"] + "_" + args.context_name

    contextService = soapclient.getService("OXResellerContextService")
    ctx = contextService.getData(ctx, settings.getCreds())

    user = {}
    if args.email is not None:
        user["name"] = args.email
    if args.userid is not None:
        user["id"] = args.userid

    userService = soapclient.getService(
        "OXResellerUserService", dump=args.dump)
    user = userService.getData(ctx, user, settings.getCreds())

    changeuser = {}
    if args.password is not None:
        changeuser["password"] = args.password
    if args.firstname is not None:
        changeuser["given_name"] = args.firstname
    if args.lastname is not None:
        changeuser["sur_name"] = args.lastname
    if args.language is not None:
        changeuser["language"] = args.language
    if args.aliases is not None:
        changeuser["aliases"] = args.aliases.split(',')
        changeuser["aliases"].append(user["primaryEmail"])
    if args.newmail is not None:
        changeuser["name"] = args.newmail
        changeuser["primaryEmail"] = args.newmail
        changeuser["email1"] = args.newmail
        changeuser["aliases"] = user["aliases"]
        changeuser["aliases"].append(args.newmail)
        changeuser["aliases"].remove(user["primaryEmail"])
        if user["defaultSenderAddress"] == user["primaryEmail"]:
            changeuser["defaultSenderAddress"] = args.newmail
    if args.timezone is not None:
        changeuser["timezone"] = args.timezone
    if args.disable:
        changeuser["mailenabled"] = False
    if args.enable:
        changeuser["mailenabled"] = True
    if args.quota is not None:
        oxaasService = soapclient.getService("OXaaSService", dump=args.dump)
        # unlimited quota is currently an edge case
        # for Drive unlimited means -1
        # for Dovecot unlimited means 0
        # handle this special case
        if args.quota == -1:
            dcQuota = 0
            # TODO set unifiedquota userAttribute to false
        else:
            dcQuota = args.quota
            # TODO remove unifiedquota userAttribute eventually
        oxaasService.setMailQuota(
            ctx.id, user.id, dcQuota, settings.getCreds())
        changeuser["maxQuota"] = args.quota
    if args.access_combination is not None:
        userService.changeByModuleAccessName(
            ctx, user, args.access_combination, settings.getCreds())
    if args.cos:
        userCloud = {}
        cloudIndex = 0
        cloudFound = False
        changeuser["userAttributes"] = user["userAttributes"]
        for index, entry in enumerate(changeuser["userAttributes"].entries):
            if entry.key == 'cloud':
                cloudFound = True
                cloudIndex = index
                for clouditem in entry.value.entries:
                    userCloud[clouditem.key] = clouditem.value

        userCloud = {
            "key": "cloud",
            "value": {"entries": {"key": "service", "value": args.cos}}
        }
        if not cloudFound:
            changeuser["userAttributes"].entries.append(userCloud)
        else:
            changeuser["userAttributes"].entries[cloudIndex] = userCloud

    if args.config or args.guard or args.safeunsubscribe or args.antiphishing:
        changeuser["userAttributes"] = user["userAttributes"]

        # create a python dict out of userAttributes
        userConfig = {}
        configIndex = 0
        configFound = False
        for index, entry in enumerate(changeuser["userAttributes"].entries):
            if entry.key == 'config':
                configFound = True
                configIndex = index
                for configitem in entry.value.entries:
                    userConfig[configitem.key] = configitem.value

        if args.guard:
            userConfig["com.openexchange.capability.guard-mail"] = args.guard
            userConfig["com.openexchange.capability.guard-docs"] = args.guard
            userConfig["com.openexchange.capability.guard-drive"] = args.guard

        if args.safeunsubscribe:
            userConfig["com.openexchange.plugins.unsubscribe.safemode"] = args.safeunsubscribe

        if args.antiphishing:
            userConfig["com.openexchange.plugins.antiphishing.enabled"] = args.antiphishing

        if args.config:
            newconfig = kv_pairs(args.config)
            for configitem in newconfig:
                userConfig[configitem] = newconfig[configitem]

        # write dict back in correct format
        # TODO: handle append case if configFound=False
        if not configFound:
            changeuser["userAttributes"].entries.append(
                {'key': 'config', 'value': {'entries': []}})

        changeuser["userAttributes"].entries[configIndex].value.entries = []
        for configitem in userConfig:
            changeuser["userAttributes"].entries[configIndex].value.entries.append(
                {
                    "key": configitem,
                    "value": userConfig[configitem]
                }
            )

    if changeuser:
        changeuser["id"] = user.id
        userService.change(ctx, changeuser, settings.getCreds())

    if args.editpassword is not None:
        user_access = userService.getModuleAccess(
            ctx, user, settings.getCreds())
        user_access.editPassword = args.editpassword
        userService.changeByModuleAccess(
            ctx, user, user_access, settings.getCreds())

    print("Changed user", user.id, "in context", ctx.id)

    # apply spamlevel
    if args.spamlevel:
        data = json.loads('{"spamlevel": "'+args.spamlevel+'"}')
        r = requests.put(settings.getRestHost()+"oxaas/v1/admin/contexts/"+str(
            ctx.id)+"/users/"+str(user.id)+"/spamlevel", auth=(settings.getRestCreds()), json=data, verify=settings.getVerifyTls())
        print(r.status_code)
        if r.status_code == 200:
            print("Applied spamlevel ", args.spamlevel,
                  " for ", user.id, "in context", ctx.id)
        else:
            print("Failed to set requested spamlevel")


def kv_pairs(text, item_sep=r",", value_sep="="):
    split_regex = r"""
        (?P<key>[\w\.\-/]+)=    # Key consists of only alphanumerics and '-' character
        (?P<quote>["']?)        # Optional quote character.
        (?P<value>[\S\s]*?)     # Value is a non greedy match
        (?P=quote)              # Closing quote equals the first.
        ($|\s)                  # Entry ends with comma or end of string
    """.replace("=", value_sep).replace(r"|\s)", f"|{item_sep})")
    regex = re.compile(split_regex, re.VERBOSE)
    return {match.group("key"): match.group("value") for match in regex.finditer(text)}


if __name__ == "__main__":
    main()
