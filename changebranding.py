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

import warnings
import argparse
import re
from requests import Session
from zeep import Client
from zeep.transports import Transport
import settings

warnings.filterwarnings("ignore")


def main():
    parser = argparse.ArgumentParser(
        description='Changes global reseller settings.')
    parser.add_argument("--servercontact", help="Modify contact information.")
    parser.add_argument("--configimport",
                        help="Import properties (e.g dynamic theme settings) from file.")
    parser.add_argument(
        "--config", help="Additional config properties including in format PROPERTY=VALUE")
    args = parser.parse_args()

    session = Session()
    session.verify = False
    resellerService = Client(settings.getHost() +
        "OXResellerService?wsdl", transport=Transport(session=session))

    admin = {
        "name": settings.getCreds()["login"]
    }

    config = []

    if args.configimport is not None:
        fileinput = open(args.configimport, 'r')
        lines = fileinput.readlines()
        for line in lines:
            if line.startswith('#') or line.startswith(' '):
                continue
            line = line.strip()
            config.append({"key": line.split('=', 1)[
                          0], "value": line.split('=', 1)[1]})

        fileinput.close()

    if args.servercontact:
        config.append(
            {"key": "com.openexchange.appsuite.servercontact", "value": args.servercontact})

    if args.config:
        for key, value in kv_pairs(args.config).items():
            config.append(
                {
                    "key": key,
                    "value": value
                }
            )

    admin["configurationToAdd"] = {"entries": config}

    resellerService.service.changeSelf(admin, settings.getCreds())
    print("Changed configuration")


def kv_pairs(text, item_sep=r";", value_sep="="):
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
