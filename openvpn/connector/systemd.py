#  OpenVPN Connector Setup
#      - Configure OpenVPN 3 Linux for CloudConnexa™
#
#  SPDX-License-Identifier: AGPL-3.0-only
#
#  Copyright (C) 2020 - 2023  OpenVPN Inc. <sales@openvpn.net>
#  Copyright (C) 2020 - 2023  David Sommerseth <davids@openvpn.net>
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
