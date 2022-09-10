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

import re
import target


def getHost():
  return re.sub("/$","",target.soapHost)+"/webservices/"

def getAdminRestHost():
  return re.sub("/$","",target.soapHost)+"/"

def getRestHost():
  return re.sub("/$","",target.restHost)+"/"

def getCreds():
  creds={
    "login": target.login,
    "password": target.password
  }
  return creds

def getRestCreds():
  creds=(
    target.login,
    target.password
  )
  return creds

def getProxy():
  if hasattr(target, "proxy"):
    proxy={
      "https": target.proxy
    }
    return proxy
  else:
    return None

def getVerifyTls():
  return getattr(target, "verifyTls", True)
