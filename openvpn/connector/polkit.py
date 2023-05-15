#  OpenVPN Connector Setup
#      - Configure OpenVPN 3 Linux for CloudConnexa™
#
#  SPDX-License-Identifier: AGPL-3.0-only
#
#  Copyright (C) 2023         OpenVPN Inc. <sales@openvpn.net>
#  Copyright (C) 2023         David Sommerseth <davids@openvpn.net>
#

import dbus
import os

class PolkitAuthCheck(object):
    """Simplified polkit authorization checker"""

    def __init__(self, dbuscon):
        self._dbuscon = dbuscon

        # Retrieve access to the main PolicyKit1 object
        self._service = self._dbuscon.get_object('org.freedesktop.PolicyKit1',
                                                 '/org/freedesktop/PolicyKit1/Authority')

        # Establish a link to the Authority interface in the PolicyKit object
        self._polkitauth = dbus.Interface(self._service,
                                          dbus_interface='org.freedesktop.PolicyKit1.Authority')


    def CheckAuthorization(self, action_id, allow_user_interaction=False):
        """Checks if the current user has access to a specific PolicyKit action ID"""

        subject = dbus.Struct((dbus.String('unix-process'),
                               dbus.Dictionary(
                                   {
                                       dbus.String('pid'): dbus.UInt32(os.getpid()),
                                       dbus.String('start-time'): dbus.UInt64(0),
                                       dbus.String('uid'): os.getuid()
                                   }
                               )))
        user_interact = allow_user_interaction and 1 or 0;
        res = self._polkitauth.CheckAuthorization(subject,
                                                  dbus.String(action_id),
                                                  dbus.Dictionary({}),
                                                  user_interact,
                                                  dbus.String())
        return dbus.Boolean(res[0]) == dbus.Boolean(True)
