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
import settings
import soapclient


def main():
    parser = argparse.ArgumentParser(
        description='Changes an OX Cloud context.')
    parser.add_argument("-n", dest="context_name", help="Context name to be changed.")
    parser.add_argument(
        "-c", "--cid", help="Context ID to be changed.", type=int)
    parser.add_argument(
        "-q", "--quota", help="New quota of the context in MiB", type=int)
    args = parser.parse_args()

    if args.context_name is None and args.cid is None:
        parser.error("Context must be specified by either -n or -c !")

    contextService = soapclient.getService("OXResellerContextService")

    ctx = {}
    if args.cid is not None:
        ctx["id"] = args.cid
    else:
        ctx["name"] = settings.getCreds()["login"] + "_" + args.context_name

    ctx = contextService.getData(ctx, settings.getCreds())

    if args.quota is not None:
        ctx.maxQuota = args.quota

    contextService.change(ctx, settings.getCreds())
    print("Changed context", ctx.id)


if __name__ == "__main__":
    main()
