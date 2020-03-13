#  OpenVPN Connector Setup
#      - Configure OpenVPN 3 Linux for OpenVPN Cloud
#
#  Copyright (C) 2020         OpenVPN Inc. <sales@openvpn.net>
#  Copyright (C) 2020         David Sommerseth <davids@openvpn.net>
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

class AutoloadConfig(object):
    def __init__(self, cfg):
        cfgdir = os.path.dirname(cfg)
        main_cfgname = os.path.basename(cfg)
        al_cfgname = "%s.autoload" % ".".join(main_cfgname.split('.')[:-1])
        self._cfgname = os.path.join(cfgdir, al_cfgname)
        self._properties = {}


    def GetConfigFilename(self):
        return self._cfgname


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
        j = json.dumps(self._properties, indent=4)
        fp = open(self._cfgname, 'wb')
        fp.write(j.encode('utf-8'))
        fp.close()


    def _check_property_section(self, key, props):
        if key is None:
            return
        if type(key) is str:
            if not (key in props):
                props[key] = {}

