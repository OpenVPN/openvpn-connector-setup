#  OpenVPN Connector Setup
#      - Configure OpenVPN 3 Linux for CloudConnexa™
#
#  SPDX-License-Identifier: AGPL-3.0-only
#
#  Copyright (C) 2020 - 2023  OpenVPN Inc. <sales@openvpn.net>
#  Copyright (C) 2020 - 2023  David Sommerseth <davids@openvpn.net>
#

import os
import dbus
from openvpn3 import ConfigurationManager

class ConfigImport(object):
    def __init__(self, systembus, cfgname, force=False):
        self.__system_bus = systembus
        self.__cfgmgr = ConfigurationManager(self.__system_bus)
        self.__config_name = cfgname.replace(' ', '')
        self._cfgobj = None
        self.__overwrite = []

        if self.__config_name != cfgname:
            print('** INFO **  Spaces stripped from configuration '
                  + 'name. New name: %s' % self.__config_name)

        if self.__duplicate_check(self.__config_name, force) == True:
            if not force:
                raise ValueError('Configuration profile name "%s" already exists' % self.__config_name)


    def GetConfigName(self):
        return self.__config_name


    def Import(self, profile):
        if len(self.__overwrite) > 0:
            print('** Warning **  Removing old configuration profile with same name')
            for cfg in self.__overwrite:
                if 'OPENVPN_CONNECTOR_DEBUG' in os.environ:
                    print('.. Removing %s' % cfg.GetPath())
                cfg.Remove()

        print('Importing VPN configuration profile "%s" ... ' % self.__config_name,
              end='', flush=True)
        self._cfgobj = self.__cfgmgr.Import(self.__config_name,
                                             profile.GetProfile(),
                                             False, True)
        self._cfgobj.SetProperty('locked_down', True)
        self._cfgobj.SetOverride('persist-tun', True)
        self._cfgobj.SetOverride('log-level', '5')
        print('Done')
        if 'OPENVPN_CONNECTOR_DEBUG' in os.environ:
            print('Configuration path: %s' % self._cfgobj.GetPath())


    def EnableDCO(self):
        print('Enabling Data Channel Offload (DCO) ... ', end='', flush=True)
        self._cfgobj.SetProperty('dco', True)
        print('Done')


    def EnableOwnershipTransfer(self):
        print('Granting root user access to profile ... ', end='', flush=True)
        self._cfgobj.SetProperty('transfer_owner_session', True)
        self._cfgobj.AccessGrant(0)
        print('Done')


    def __duplicate_check(self, cfgname, force):
        # NOTE: This will only look up configuration names
        #       for the current user.  If more users have imported
        #       configuration profiles with the same name, this
        #       will not be detected here.  This will require
        #       improved support within the net.openvpn.v3.configuration
        #       D-Bus service.
        ret = False
        for cfg in self.__cfgmgr.FetchAvailableConfigs():
            n = cfg.GetProperty('name')
            if cfgname == n:
                ret = True
                if force:
                    self.__overwrite.insert(0, cfg)
        return ret
