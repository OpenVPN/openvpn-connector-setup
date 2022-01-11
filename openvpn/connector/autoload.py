#  OpenVPN Connector Setup
#      - Configure OpenVPN 3 Linux for OpenVPN Cloud
#
#  Copyright (C) 2020 - 2022  OpenVPN Inc. <sales@openvpn.net>
#  Copyright (C) 2020 - 2022  David Sommerseth <davids@openvpn.net>
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
import json
from pathlib import Path

class AutoloadConfig(object):
    def __init__(self, profile, rootdir, cfgname_prefix):
        self._profile = profile
        self._rootdir = rootdir

        al_cfgname = '%s.autoload' % cfgname_prefix
        self._autoload_file = os.path.join(rootdir, al_cfgname)

        vpn_cfgname = '%s.conf' % cfgname_prefix
        self._config_file =  os.path.join(rootdir, vpn_cfgname)

        self._properties = {}


    def GetAutoloadFilename(self):
        return self._autoload_file


    def SetName(self, name):
        self._properties["name"] = name


    def SetAutostart(self, auto_start):
        self._properties["autostart"] = (True == auto_start)


    def SetTunnelParams(self, key, value):
        valid_keys = ['ipv6','persist','dns-fallback','dns-setup-disabled']
        if not key in valid_keys:
            raise ValueError('Incorrect key "%s" for "tunnel" section' % key)

        self._check_property_section('tunnel', self._properties)
        self._properties['tunnel'][key] = value


    def Save(self):
        # Ensure proper destination directories exists
        config_dir = os.path.join(self._rootdir, 'etc','openvpn3','autoload')
        Path(config_dir).mkdir(parents=True, exist_ok=True)

        print('Saving VPN configuration profile to "%s" ... ' % self._config_file, end='', flush=True)
        self._profile.Save(self._config_file)
        print('Done')

        print('Saving openvpn3-autoload config to "%s" ... ' % self._autoload_file,  end='', flush=True)
        j = json.dumps(self._properties, indent=4)
        fp = open(self._autoload_file, 'wb')
        fp.write(j.encode('utf-8'))
        fp.close()
        print('Done')


    def _check_property_section(self, key, props):
        if key is None:
            return
        if type(key) is str:
            if not (key in props):
                props[key] = {}

