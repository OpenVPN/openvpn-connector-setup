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

import sys
import os
import argparse
import dbus
from enum import Enum
from openvpn.connector.token import DecodeToken
from openvpn.connector.profile import ProfileFetch, DecryptError, DownloadError
from openvpn.connector.autoload import AutoloadConfig
from openvpn.connector.configmgr import ConfigImport
from openvpn.connector.systemd import SystemdServiceUnit

# Add the traceback module if we're in debugging mode.
# This will allow dumping of tracebacks when exceptions happens
if 'OPENVPN_CLOUD_DEBUG' in os.environ:
    import traceback


class ConfigModes(Enum):
    UNSET = 0
    AUTOLOAD = 1
    UNITFILE = 2

    def to_string(v):
        if ConfigModes.UNSET == v:
            return '[UNSET]'
        elif ConfigModes.AUTOLOAD == v:
            return 'autoload'
        elif ConfigModes.UNITFILE == v:
            return 'systemd-unit'

    def parse(v):
        if 'autoload' == v:
            return ConfigModes.AUTOLOAD
        elif 'systemd-unit' == v:
            return ConfigModes.UNITFILE
        raise ValueError('Incorrect configuration mode: "%s"' % v)


def main():
    run_mode = ConfigModes.UNITFILE
    cli = argparse.ArgumentParser(prog='openvpn-connector-setup',
                                  description='OpenVPN Connector Setup utility',
                                  usage='%s [options]' % os.path.basename(sys.argv[0]))
    cli.add_argument('--mode', metavar='MODE', nargs=1, action='store',
                     help='Defines how configuration profiles are imported and stored (default: %s)' % ConfigModes.to_string(run_mode))
    cli.add_argument('--token', metavar='TOKEN_VALUE', nargs=1,
                     help='This value is provided by the OpenVPN Cloud web portal.')
    cli.add_argument('--name', metavar='NAME', nargs=1, default=['OpenVPN Cloud',],
                     help='Configuration profile name to use. Default: "OpenVPN Cloud"')
    cli.add_argument('--force', action='store_true',
                     help='Overwrite configuration profile if it already exists')
    cli.add_argument('--autoload-file-prefix', metavar='AUTOLOAD_FILE_PREFIX', nargs=1, default=['connector',],
                     help='Configuration filename to use. Default: connector.conf')
    cli.add_argument('--no-start', action='store_true',
                     help='Do not start and configure the profile to start at boot')
    cli.add_argument('--dco', action='store_true',
                     help='Use OpenVPN Data Channel Offload (DCO) by default')

    cliopts = cli.parse_args(sys.argv[1:])

    token = None
    autoload_prefix = cliopts.autoload_file_prefix[0]
    config_name = cliopts.name[0]
    force = cliopts.force and True
    start_config = not cliopts.no_start
    dco = cliopts.dco and True

    if cliopts.mode:
        run_mode = ConfigModes.parse(cliopts.mode[0])

    if 'OPENVPN_CLOUD_DEBUG' in os.environ:
        print('Run mode: %s' % ConfigModes.to_string(run_mode))

    # By default the root installation directory is /
    # but for development and debugging, the root directory
    # can be put into a chroot.  This is done via the
    # OPENVPN_CLOUD_ROOT_DIR environment variable which
    # must be set before this script is run.
    rootdir = '/'
    if 'OPENVPN_CLOUD_ROOT_DIR' in os.environ:
        rootdir = os.environ['OPENVPN_CLOUD_ROOT_DIR']

    if ConfigModes.AUTOLOAD == run_mode and '/' == rootdir and os.geteuid() != 0:
        print('%s must be run as root with "%s" as top level installation directory ' % (
                  os.path.basename(sys.argv[0]), rootdir))
        sys.exit(2)

    if cliopts.token is None:
        print("""OpenVPN Cloud Connector Setup

This utility is used to configure this host as an OpenVPN Cloud Connector.
Before this utility can be run, you must have configured a connector in
the OpenVPN Cloud web portal where an setup token is provided.  This
token is used by this utility to download the proper VPN configuration
profile and complete the configuration.\n""")

        token = input('Enter setup token: ')
        print("")
    else:
        token = cliopts.token[0]

    try:
        # Parse the setup token.  This contains
        # the profile name which needs to be downloaded
        # and a key used to decrypt the downloaded profile
        token = DecodeToken(token)

        systembus = dbus.SystemBus()
        cfgimport = None
        if ConfigModes.UNITFILE == run_mode:
            cfgimport = ConfigImport(systembus, config_name, force)

        # Download the profile from OpenVPN Cloud
        profile = ProfileFetch(token)
        print('Downloading OpenVPN Cloud Connector profile ... ', end='', flush=True)
        profile.Download()
        print('Done')

        if ConfigModes.AUTOLOAD == run_mode:
            # Generate the openvpn3-autoload configuration
            autoload = AutoloadConfig(profile, rootdir, autoload_prefix)
            autoload.SetName(config_name)
            autoload.SetAutostart(True)
            autoload.SetTunnelParams('persist', True)
            autoload.Save()

            if dco:
                print('** WARNING ** The openvpn3-autoload mode does not support enabling DCO')

            if start_config is True and '/' == rootdir and os.geteuid() == 0:
                service = SystemdServiceUnit(systembus, 'openvpn3-autoload.service')
                print('Enabling openvpn3-autoload.service during boot ... ', end='', flush=True)
                service.Enable()
                print('Done')

                print('Starting openvpn3-autoload.service ... ', end='', flush=True)
                service.Start()
                print('Done')

        elif ConfigModes.UNITFILE == run_mode:
            cfgimport.Import(profile)

            if cliopts.dco:
                cfgimport.EnableDCO()

            if os.geteuid() != 0:
                cfgimport.EnableOwnershipTransfer()

                if start_config is True:
                    print('\n** INFO **   You did not run this command as root, so it will not\n'
                          + '             start the connection automatically during boot.  To start\n'
                          + '             at boot time, as root, run this command: \n\n'
                          + '             # systemctl enable --now openvpn3-session@%s.service\n' %
                          cfgimport.GetConfigName())
            elif os.geteuid() == 0 and start_config is True:
                service = SystemdServiceUnit(systembus,
                                             'openvpn3-session@%s.service' % cfgimport.GetConfigName())

                print('Enabling openvpn3-session@%s.service during boot ... ' % cfgimport.GetConfigName(),
                      end='', flush=True)
                service.Enable()
                print('Done')

                print('Starting openvpn3-session@%s.service ... ' % cfgimport.GetConfigName(),
                      end='', flush=True)
                service.Start()
                print('Done')

    except DownloadError as err:
        print('\n** ERROR ** ' + str(err))
        print('URL: ' + err.GetURL())
        sys.exit(5)
    except DecryptError as err:
        print('\n** ERROR ** Failed decrypting the downloaded profile: ' + str(err))
        sys.exit(4)
    except BaseException as err:
        print('\n** ERROR **  ' + str(err))

        if 'OPENVPN_CLOUD_DEBUG' in os.environ:
            print ('\nmain traceback:')
            print (traceback.format_exc())

        sys.exit(3)
