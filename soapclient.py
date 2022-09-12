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

from lxml import etree
from requests import Session
from zeep import Client
from zeep import Plugin
from zeep.transports import Transport
import settings
import warnings

warnings.filterwarnings("ignore")


class MyLoggingPlugin(Plugin):
    def ingress(self, envelope, http_headers, operation):
        print(etree.tostring(envelope, pretty_print=False))
        return envelope, http_headers

    def egress(self, envelope, http_headers, operation, binding_options):
        print(etree.tostring(envelope, pretty_print=False))
        return envelope, http_headers

def getService(servicename, dump=False):

  session = Session()
  session.verify = settings.getVerifyTls()

  transport = Transport(session = session)
  transport.session.proxies = settings.getProxy()

  plugins = [MyLoggingPlugin()] if dump else []

  return Client(settings.getHost()+servicename+"?wsdl", plugins = plugins, transport = transport).service
