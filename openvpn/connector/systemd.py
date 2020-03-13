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

import dbus

class SystemdServiceUnit(object):
    """Simple implementation for managing systemd services"""

    def __init__(self, dbuscon, unit_name):
        self._dbuscon = dbuscon
        self._unit_name = unit_name

        # Retrieve access to the main systemd manager object
        self._srvmngr_obj = self._dbuscon.get_object('org.freedesktop.systemd1',
                                                     '/org/freedesktop/systemd1')
        # Establish a link to the manager interface in the manager object
        self._srvmgr = dbus.Interface(self._srvmngr_obj,
                                      dbus_interface='org.freedesktop.systemd1.Manager')

    def Enable(self):
        """Enable a systemd service unit to be started at boot"""

        self._srvmgr.EnableUnitFiles([self._unit_name,], False, True)

    def Start(self):
        """Start a systemd service unit"""

        self._srvmgr.StartUnit(self._unit_name, 'replace')
