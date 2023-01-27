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

import requests
import settings

path = "cloudapi/v1/"

def post(scope, data):
    return requests.post(settings.getRestHost() + path + scope,
                        auth=(settings.getRestCreds()),
                        json=data,
                        verify=settings.getVerifyTls())

def put(scope, data):
    return requests.put(settings.getRestHost() + path + scope,
                        auth=(settings.getRestCreds()),
                        json=data,
                        verify=settings.getVerifyTls())

def get(scope, params):
    return requests.get(settings.getRestHost() + path + scope,
                        params=params,
                        auth=(settings.getRestCreds()),
                        verify=settings.getVerifyTls())

def delete(scope):
    return requests.delete(settings.getRestHost() + path + scope,
                           auth=(settings.getRestCreds()),
                           verify=settings.getVerifyTls())