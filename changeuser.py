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
from copy import deepcopy
import re
import requests
import settings
import soapclient
from os.path import exists
from zeep.helpers import serialize_object


def main():
    parser = argparse.ArgumentParser(description='Change an OX Cloud user.')
    parser.add_argument("-n", dest="context_name",
                        help="Context name the user to be changed.")
    parser.add_argument(
        "-c", "--cid", help="Context ID the user to be changed.", type=int)
    parser.add_argument(
        "-e", "--email", help="E-Mail address / login name of the user.")
    parser.add_argument(
        "-u", "--userid", type=int,
        help="Numeric user ID. Use -e/--email for an email address or login name.")
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
    parser.add_argument("--mailquota", help="New mailquota in non-unified case.", type=int)
    parser.add_argument("-a", "--access_combination", "--access-combination",
                        help="New access combination name for the user.")
    parser.add_argument("--cos", help="The Class of Service for that mailbox.")
    parser.add_argument("--editpassword",
                        help="Should the user have the ability to change his password", type=parse_bool)
    parser.add_argument("--addinfostore",
                        help="Adds infostore permission", type=parse_bool)
    parser.add_argument(
        "--spamlevel", choices=('low', 'medium', 'high'),
        help="Specify spamlevel to use for the mailbox (no default).")
    parser.add_argument(
        "--config", help="Config file or comma-separated PROPERTY=VALUE pairs; quote values containing commas")
    parser.add_argument(
        "--remove-config", help="Wipe specified property from config")
    status = parser.add_mutually_exclusive_group()
    status.add_argument(
        "--disable", help="Disable the user.", action="store_true")
    status.add_argument("--enable", help="Enable the user.",
                        action="store_true")
    parser.add_argument(
        "--dump", help="Print SOAP XML request/response to stdout (includes credentials).", action="store_true")
    args = parser.parse_args()

    if args.context_name is None and args.cid is None:
        parser.error("Context must be specified by either -n or -c !")

    if args.userid is None and args.email is None:
        parser.error("User must be specified by either -u or -e !")

    # Parse local input before making any remote changes.
    try:
        config_updates = read_config(args.config) if args.config is not None else {}
        if args.remove_config is not None:
            if not re.fullmatch(r'[\w.\-/]+', args.remove_config):
                raise ValueError('--remove-config requires a property name')
            # Keep the existing None deletion convention; the key must be sent.
            config_updates[args.remove_config] = None
    except (OSError, ValueError) as error:
        parser.error(str(error))

    changes = ('password', 'firstname', 'lastname', 'language', 'aliases',
               'newmail', 'timezone', 'quota', 'mailquota', 'access_combination',
               'cos', 'editpassword', 'addinfostore', 'spamlevel', 'remove_config')
    if not (any(getattr(args, name) is not None for name in changes)
            or config_updates or args.enable or args.disable):
        parser.error('No changes specified')

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
    if args.aliases is not None or args.newmail is not None:
        aliases = (args.aliases.split(',') if args.aliases is not None
                   else list(user["aliases"] or []))
        primary = args.newmail if args.newmail is not None else user["primaryEmail"]
        changeuser["aliases"] = list(dict.fromkeys(
            alias.strip() for alias in aliases if alias and alias.strip()
            and not (args.newmail is not None and alias.strip() == user["primaryEmail"])
        ))
        if primary not in changeuser["aliases"]:
            changeuser["aliases"].append(primary)
    if args.newmail is not None:
        changeuser["name"] = args.newmail
        changeuser["primaryEmail"] = args.newmail
        changeuser["email1"] = args.newmail
        if user["defaultSenderAddress"] == user["primaryEmail"]:
            changeuser["defaultSenderAddress"] = args.newmail
    if args.timezone is not None:
        changeuser["timezone"] = args.timezone
    if args.disable:
        changeuser["mailenabled"] = False
    if args.enable:
        changeuser["mailenabled"] = True
    if args.quota is not None or args.mailquota is not None:
        if args.quota is not None:
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
        if args.mailquota is not None:
            dcQuota = args.mailquota
        if args.quota is not None:
            changeuser["maxQuota"] = args.quota

    if args.cos is not None or config_updates:
        try:
            changeuser["userAttributes"] = update_user_attributes(
                user["userAttributes"], config_updates, args.cos)
        except ValueError as error:
            parser.error(str(error))

    # Finish constructing/validating the payload before the first write.
    if args.quota is not None or args.mailquota is not None:
        oxaasService = soapclient.getService("OXaaSService", dump=args.dump)
        oxaasService.setMailQuota(ctx.id, user.id, dcQuota, settings.getCreds())
    if args.access_combination is not None:
        userService.changeByModuleAccessName(
            ctx, user, args.access_combination, settings.getCreds())

    if changeuser:
        changeuser["id"] = user.id
        userService.change(ctx, changeuser, settings.getCreds())

    if args.editpassword is not None:
        user_access = userService.getModuleAccess(
            ctx, user, settings.getCreds())
        user_access.editPassword = args.editpassword
        userService.changeByModuleAccess(
            ctx, user, user_access, settings.getCreds())

    if args.addinfostore is not None:
        user_access = userService.getModuleAccess(
            ctx, user, settings.getCreds())
        user_access.infostore = args.addinfostore
        userService.changeByModuleAccess(
            ctx, user, user_access, settings.getCreds())

    # apply spamlevel
    if args.spamlevel:
        data = {"spamlevel": args.spamlevel}
        r = requests.put(settings.getRestHost()+"oxaas/v1/admin/contexts/"+str(
            ctx.id)+"/users/"+str(user.id)+"/spamlevel", auth=(settings.getRestCreds()), json=data, verify=settings.getVerifyTls(), timeout=30)
        print(r.status_code)
        if r.status_code == 200:
            print("Applied spamlevel ", args.spamlevel,
                  " for ", user.id, "in context", ctx.id)
        else:
            raise RuntimeError('Failed to set requested spamlevel (HTTP {})'.format(r.status_code))

    print("Changed user", user.id, "in context", ctx.id)


def parse_bool(value):
    if value.lower() in ('true', 'yes', '1'):
        return True
    if value.lower() in ('false', 'no', '0'):
        return False
    raise argparse.ArgumentTypeError('Expected true or false')


def kv_pairs(text):
    """Read comma-separated properties without silently skipping invalid input."""
    result = {}
    remaining = text.strip()
    if not remaining:
        raise ValueError('--config requires PROPERTY=VALUE or a config file')
    while remaining:
        match = re.match(r'([\w.\-/]+)\s*=\s*', remaining)
        if not match:
            raise ValueError('Invalid --config input: expected PROPERTY=VALUE')
        key = match.group(1)
        remaining = remaining[match.end():]
        if remaining.startswith(('"', "'")):
            end = 1
            while end < len(remaining):
                if remaining[end] == '\\':
                    end += 2
                elif remaining[end] == remaining[0]:
                    break
                else:
                    end += 1
            if end >= len(remaining):
                raise ValueError('Unclosed quote in --config input')
            value = remaining[1:end]
            remaining = remaining[end + 1:].lstrip()
            if remaining and not remaining.startswith(','):
                raise ValueError('Expected comma after quoted config value')
        else:
            value, separator, remaining = remaining.partition(',')
            value = value.rstrip()
            # Restore the delimiter for the common handling below.
            if separator:
                remaining = ',' + remaining
        result[key] = value
        if remaining:
            remaining = remaining[1:].strip()
            if not remaining:
                raise ValueError('Trailing comma in --config input')
    return result


def read_config(value):
    if not exists(value):
        return kv_pairs(value)
    result = {}
    with open(value, encoding='utf-8') as config_file:
        for number, line in enumerate(config_file, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            key, separator, setting = line.partition('=')
            key = key.strip()
            if not separator or not re.fullmatch(r'[\w.\-/]+', key):
                raise ValueError('Invalid config property on line {}'.format(number))
            # File values are literal; commas and JSON quoting are preserved.
            result[key] = setting
    return result


def map_entries(value, label):
    """Normalize SOAP map wrappers; refuse malformed data instead of losing it."""
    if value is None:
        return []
    if not isinstance(value, dict) or 'entries' not in value:
        raise ValueError('Malformed {} map'.format(label))
    entries = value['entries']
    if entries is None:
        entries = []
    elif isinstance(entries, dict):
        entries = [entries]
    if not isinstance(entries, list) or any(
            not isinstance(entry, dict) or not isinstance(entry.get('key'), str)
            or not entry['key'] or 'value' not in entry for entry in entries):
        raise ValueError('Malformed {} entries'.format(label))
    value['entries'] = entries
    return entries


def update_user_attributes(attributes, config_updates, cos=None):
    """Copy SOAP attributes and merge only the requested namespaces/properties."""
    attributes = deepcopy(serialize_object(attributes, target_cls=dict))
    if attributes is None:
        attributes = {'entries': []}
    namespaces = map_entries(attributes, 'userAttributes')
    updates = {}
    if cos is not None:
        updates['cloud'] = {'service': cos}
    if config_updates:
        updates['config'] = config_updates
    for name, properties in updates.items():
        matches = [entry for entry in namespaces if entry['key'] == name]
        if len(matches) > 1:
            raise ValueError('Duplicate {} namespaces in userAttributes'.format(name))
        if matches:
            namespace = matches[0]
            if namespace['value'] is None:
                namespace['value'] = {'entries': []}
        else:
            namespace = {'key': name, 'value': {'entries': []}}
            namespaces.append(namespace)
        entries = map_entries(namespace['value'], name)
        by_key = {}
        for entry in entries:
            if entry['key'] in by_key:
                raise ValueError('Duplicate property in {} userAttributes'.format(name))
            by_key[entry['key']] = entry
        for key, value in properties.items():
            if key in by_key:
                by_key[key]['value'] = value
            else:
                entry = {'key': key, 'value': value}
                entries.append(entry)
                by_key[key] = entry
    return attributes


if __name__ == "__main__":
    main()
