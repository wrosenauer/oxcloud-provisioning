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
import re
from zeep import Client
# for request logging
from zeep import Plugin
from lxml import etree
import settings

class MyLoggingPlugin(Plugin):
    def ingress(self, envelope, http_headers, operation):
        print(etree.tostring(envelope, pretty_print=False))
        return envelope, http_headers

    def egress(self, envelope, http_headers, operation, binding_options):
        print(etree.tostring(envelope, pretty_print=False))
        return envelope, http_headers

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
    parser.add_argument("-p", "--password", help="New Password for the user.")
    parser.add_argument("-g", "--firstname",
                        help="New first name of the user.")
    parser.add_argument("-s", "--lastname", help="New last name of the user.")
    parser.add_argument("-l", "--language", help="New language of the user.")
    parser.add_argument("-t", "--timezone", help="New timezone of the user.")
    parser.add_argument(
        "-q", "--quota", help="New quota of the user in MiB", type=int)
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
        "--dumpster", help="Enable/disbable the Dumpster feature for the user.", type=bool)
    parser.add_argument(
        "--antiphishing", help="Enable/disable the ToC antiphishing feature.", type=bool)
    parser.add_argument(
        "--config", help="Additional config properties including in format PROPERTY=VALUE")
    parser.add_argument("--disable", help="Disable the user.", action="store_true")
    parser.add_argument("--enable", help="Enable the user.", action="store_true")
    parser.add_argument("--dump", help="Dump XML request/response to file.", action="store_true")
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

    contextService = Client(settings.getHost()+"OXResellerContextService?wsdl")
    ctx = contextService.service.getData(ctx, settings.getCreds())

    user = {}
    if args.email is not None:
        user["name"] = args.email
    if args.userid is not None:
        user["id"] = args.userid

    if args.dump:
        userService = Client(settings.getHost()+"OXResellerUserService?wsdl", plugins=[MyLoggingPlugin()])
    else:
        userService = Client(settings.getHost()+"OXResellerUserService?wsdl")
    user = userService.service.getData(ctx, user, settings.getCreds())

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
    if args.timezone is not None:
        changeuser["timezone"] = args.timezone
    if args.disable:
        changeuser["mailenabled"] = False
    if args.enable:
        changeuser["mailenabled"] = True
    if args.quota is not None:
        if args.dump:
            oxaasService = Client(settings.getHost()+"OXaaSService?wsdl", plugins=[MyLoggingPlugin()])
        else:
            oxaasService = Client(settings.getHost()+"OXaaSService?wsdl")
        oxaasService.service.setMailQuota(
            ctx.id, user.id, args.quota, settings.getCreds())
        changeuser["maxQuota"] = args.quota
    if args.access_combination is not None:
        userService.service.changeByModuleAccessName(ctx, user, args.access_combination, settings.getCreds())
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
            "value": {"entries": { "key": "service", "value": args.cos }}
        }
        if not cloudFound:
            changeuser["userAttributes"].entries.append(userCloud)
        else:
            changeuser["userAttributes"].entries[cloudIndex] = userCloud


    if args.config or args.guard or args.safeunsubscribe or args.dumpster or args.antiphishing:
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

        if args.dumpster:
            userConfig["com.openexchange.capability.dumpster"] = args.dumpster

        if args.antiphishing:
            userConfig["com.openexchange.plugins.antiphishing.enabled"] = args.antiphishing

        if args.config:
            newconfig = kv_pairs(args.config)
            for configitem in newconfig:
                userConfig[configitem] = newconfig[configitem]

        # write dict back in correct format
        # TODO: handle append case if configFound=False
        if not configFound:
            changeuser["userAttributes"].entries.append( { 'key':'config', 'value':{'entries':[]} })

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
        userService.service.change(ctx, changeuser, settings.getCreds())

    if args.editpassword is not None:
        user_access = userService.service.getModuleAccess(ctx, user, settings.getCreds())
        user_access.editPassword = args.editpassword
        userService.service.changeByModuleAccess(ctx, user, user_access, settings.getCreds())

    print("Changed user", user.id, "in context", ctx.id)


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
