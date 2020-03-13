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

import sys
import os
import argparse
import dbus
from pathlib import Path
from openvpn.connector.token import DecodeToken
from openvpn.connector.profile import ProfileFetch, DecryptError, DownloadError
from openvpn.connector.autoload import AutoloadConfig
from openvpn.connector.systemd import SystemdServiceUnit

# Add the traceback module if we're in debugging mode.
# This will allow dumping of tracebacks when exceptions happens
if 'OPENVPN_CLOUD_DEBUG' in os.environ:
    import traceback


def main():
    cli = argparse.ArgumentParser(prog='openvpn-connector-setup',
                                  description='OpenVPN Connector Setup utility',
                                  usage='%s [options]' % os.path.basename(sys.argv[0]))
    cli.add_argument('--token', metavar='TOKEN_VALUE', nargs=1,
                     help='This value is provided by the OpenVPN Cloud web portal.')
    cli.add_argument('--name', metavar='NAME', nargs=1, default=['OpenVPN Cloud',],
                     help='Configuration profile name to use. Default: "OpenVPN Cloud"')
    cli.add_argument('--config-filename', metavar='CONFIG_FILENAME', nargs=1, default=['connector.conf',],
                     help='Configuration filename to use. Default: connector.conf')
    cli.add_argument('--no-systemd', action='store_true',
                     help='Do not start and configure openvpn3-autoload to start at boot')

    cliopts = cli.parse_args(sys.argv[1:])

    token = None
    cfg_filename = cliopts.config_filename[0]
    config_name = cliopts.name[0]
    systemd_config = not cliopts.no_systemd

    # By default the root installation directory is /
    # but for development and debugging, the root directory
    # can be put into a chroot.  This is done via the
    # OPENVPN_CLOUD_ROOT_DIR environment variable which
    # must be set before this script is run.
    rootdir = '/'
    if 'OPENVPN_CLOUD_ROOT_DIR' in os.environ:
        rootdir = os.environ['OPENVPN_CLOUD_ROOT_DIR']

    if '/' == rootdir and os.geteuid() != 0:
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
        # Ensure proper destination directories exists
        config_dir = os.path.join(rootdir, 'etc','openvpn3','autoload')
        Path(config_dir).mkdir(parents=True, exist_ok=True)

        # Parse the setup token.  This contains
        # the profile name which needs to be downloaded
        # and a key used to decrypt the downloaded profile
        token = DecodeToken(token)

        # Download the profile from OpenVPN Cloud
        profile = ProfileFetch(token)
        print('Downloading OpenVPN Cloud Connector profile ... ', end='', flush=True)
        profile.Download()
        print('Done')

        cfg = os.path.join(config_dir, cfg_filename)
        print('Saving profile to "%s" ... ' % cfg, end='', flush=True)
        profile.Save(cfg)
        print('Done')

        # Generate the openvpn3-autoload configuration
        autoload = AutoloadConfig(cfg)
        print('Saving openvpn3-autoload config to "%s" ... ' % autoload.GetConfigFilename(),  end='', flush=True)
        autoload.SetName(config_name)
        autoload.SetAutostart(True)
        autoload.SetTunnelParams('persist', True)
        autoload.Save()
        print('Done')

        if systemd_config is True and '/' == rootdir and os.geteuid() == 0:
            service = SystemdServiceUnit(dbus.SystemBus(), 'openvpn3-autoload.service')
            print('Enabling openvpn3-autoload.service during boot ... ', end='', flush=True)
            service.Enable()
            print('Done')

            print('Starting openvpn3-autoload.service ... ', end='', flush=True)
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
