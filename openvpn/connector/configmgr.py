#  OpenVPN Connector Setup
#      - Configure OpenVPN 3 Linux for OpenVPN Cloud
#
#  Copyright (C) 2022         OpenVPN Inc. <sales@openvpn.net>
#  Copyright (C) 2022         David Sommerseth <davids@openvpn.net>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, version 3 of the
#  License.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import os
import dbus
from openvpn3 import ConfigurationManager

class ConfigImport(object):
    def __init__(self, systembus, cfgname):
        self.__system_bus = systembus
        self.__cfgmgr = ConfigurationManager(self.__system_bus)
        self.__config_name = cfgname.replace(' ', '')
        self._cfgobj = None


    def GetConfigName(self):
        return self.__config_name


    def Import(self, profile):
        print('Importing VPN configuration profile "%s" ... ' % self.__config_name,
              end='', flush=True)
        self._cfgobj = self.__cfgmgr.Import(self.__config_name,
                                             profile.GetProfile(),
                                             False, True)
        self._cfgobj.SetProperty('locked_down', True)
        self._cfgobj.SetOverride('persist-tun', True)
        self._cfgobj.SetOverride('log-level', '5')
        print('Done')
        if 'OPENVPN_CLOUD_DEBUG' in os.environ:
            print('Configuration path: %s' % self._cfgobj.GetPath())


    def EnableOwnershipTransfer(self):
        print('Granting root user access to profile ... ', end='', flush=True)
        self._cfgobj.SetProperty('transfer_owner_session', True)
        self._cfgobj.AccessGrant(0)
        print('Done')

