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
    parser = argparse.ArgumentParser(description='Creates an OX Cloud user.')
    parser.add_argument("-n", dest="context_name",
                        help="Context name the user should be created in.")
    parser.add_argument(
        "-c", "--cid", help="Context ID the user should be created in.", type=int)
    parser.add_argument("-e", "--email", required=True,
                        help="E-Mail address / login name of the user.")
    parser.add_argument("-p", "--password", required=True,
                        help="Password for the user.")
    parser.add_argument("-g", "--firstname", required=True,
                        help="First name of the user.")
    parser.add_argument("-s", "--lastname", required=True,
                        help="Last name of the user.")
    parser.add_argument(
        "-l", "--language", help="Initial language of the user. (Default: en_US)", default="en_US")
    parser.add_argument(
        "-t", "--timezone", help="Initial timezone of the user. (Default: Europe/Berlin)", default="Europe/Berlin")
    parser.add_argument("-q", "--quota", required=True,
                        help="Quota of the user in MiB (-1 for unlimited)", type=int)
    parser.add_argument("-a", "--access-combination", required=True,
                        help="Access combination name for the user.")
    parser.add_argument("--cos", help="The Class of Service for that mailbox. If left undefined the access-combination name is used.")
    parser.add_argument("--editpassword",
                        help="Should the user have the ability to change his password.", action="store_true")
    parser.add_argument(
        "--guard", help="Should Guard be enabled for the user.", action="store_true")
    parser.add_argument(
        "--safeunsubscribe", help="Should the SafeUnsubscribe feature be enabled for the user.", action="store_true")
    parser.add_argument(
        "--antiphishing", help="Should TimeOfClick Antiphishing be available to the user.", action="store_true")
    parser.add_argument(
        "--spamlevel", help="Specify spamlevel to use for the mailbox (no default). Options 'low', 'medium', and 'high'.")
    parser.add_argument(
        "--config", help="Additional config properties including in format PROPERTY=VALUE")
    args = parser.parse_args()

    if args.context_name is None and args.cid is None:
        parser.error("Context must be specified by either -n or -c !")

    ctx = {}
    if args.cid is not None:
        ctx["id"] = args.cid
    else:
        ctx["name"] = settings.getCreds()["login"] + "_" + args.context_name

    if args.cos is None:
        args.cos = args.access_combination

    contextService = soapclient.getService("OXResellerContextService")
    ctx = contextService.getData(ctx, settings.getCreds())

    userService = soapclient.getService("OXResellerUserService")
    oxaasService = soapclient.getService("OXaaSService")

    # prepare user
    user = {
        "name": args.email,
        "password": args.password,
        "display_name": args.firstname + " " + args.lastname,
        "sur_name": args.lastname,
        "given_name": args.firstname,
        "primaryEmail": args.email,
        "email1": args.email,
        "language": args.language,
        "timezone": args.timezone,
        "maxQuota": args.quota,
        "drive_user_folder_mode": "normal"  # can be default, normal or none
    }

    # add userattributes (guard, safeunsubscribe)
    userConfig = []
    if args.guard:
        guardAttributes = [
            {
                "key": "com.openexchange.capability.guard-mail",
                "value": "true"
            },
            {
                "key": "com.openexchange.capability.guard-docs",
                "value": "true"
            },
            {
                "key": "com.openexchange.capability.guard-drive",
                "value": "true"
            }
        ]
        userConfig.extend(guardAttributes)

    if args.safeunsubscribe:
        unsubscribeAttributes = [
            {
                "key": "com.openexchange.plugins.unsubscribe.safemode",
                "value": "true"
            }
        ]
        userConfig.extend(unsubscribeAttributes)

    if args.antiphishing:
        antiphishingAttributes = [
            {
                "key": "com.openexchange.plugins.antiphishing.enabled",
                "value": "true"
            }
        ]
        userConfig.extend(antiphishingAttributes)

    if args.config:
        config = kv_pairs(args.config)
        configAttributes = []
        for key in config:
            configAttributes.append(
                {
                    "key": key,
                    "value": config[key]
                }
            )
        userConfig.extend(configAttributes)

    # unlimited quota is currently an edge case
    # for Drive unlimited means -1
    # for Dovecot unlimited means 0
    # handle this special case
    if args.quota == -1:
        dcQuota = 0
        user["maxQuota"] = 1 # to force creation of userfilestore
        # also disable unified quota
        userConfig.extend(
            [{
                "key": "com.openexchange.unifiedquota.enabled",
                "value": "false"
            }]
        )
    else:
        dcQuota = args.quota

    userCOS = {
            "key": "cloud",
            "value": {"entries": { "key": "service", "value": args.cos }}
    }

    user["userAttributes"] = {"entries": [ userCOS ]}

    if (userConfig):
        user["userAttributes"]["entries"].append({"key": "config", "value": {"entries": userConfig}})

    user = userService.createByModuleAccessName(
        ctx, user, args.access_combination, settings.getCreds())
    if args.editpassword:
        user_access = userService.getModuleAccess(ctx, user, settings.getCreds())
        user_access.editPassword = args.editpassword
        userService.changeByModuleAccess(ctx, user, user_access, settings.getCreds())
    if args.quota == -1:
        # change maxQuota to -1 finally
        user["maxQuota"] = -1
        userService.change(ctx, user, settings.getCreds())

    oxaasService.setMailQuota(
        ctx.id, user.id, dcQuota, settings.getCreds())

    print("Created user", user.id, "with password", args.password,
          "in context", ctx.id, "and unified quota", args.quota)

    # apply spamlevel
    if args.spamlevel:
        data = json.loads('{"spamlevel": "'+args.spamlevel+'"}')
        r = requests.put(settings.getRestHost()+"oxaas/v1/admin/contexts/"+str(
            ctx.id)+"/users/"+str(user.id)+"/spamlevel", auth=(settings.getRestCreds()), json=data)
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
