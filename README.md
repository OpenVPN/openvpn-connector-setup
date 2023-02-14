openvpn-connector-setup
=======================

The `openvpn-connector-setup` tool used to configure the
[OpenVPN 3 Linux client](https://community.openvpn.net/openvpn/wiki/OpenVPN3Linux)
to connect as a connector in an
[OpenVPN Cloud](https://openvpn.net/cloud-docs/installing-connector-for-linux/) managed
environment.

Before this tool can be used, a connector must already be configured in the
[OpenVPN Cloud portal](https://openvpn.cloud/).  As part of this step, the
web portal will provide you with a setup token value.  This token is
mandatory and needed for this tool to configure the host it is being run on.


What does this tool do?
-----------------------
By default this tool will:
* Download a VPN client configuration profile
* Configure this VPN profile to be used by `openvpn3-autoload` at boot time
* Enable and start the `openvpn3-autoload.service` systemd unit.  This will
  connect this host to the OpenVPN Cloud instantly and ensure it connects
  automatically each time the host is rebooted.


How to use it
-------------
First, configure a new connector in the
[OpenVPN Cloud portal](https://cloud.openvpn.com/).  When the portal provides
you with a setup token, run the script:

    [root@host: ~] # openvpn-connector-setup
    OpenVPN Cloud Connector Setup

    This utility is used to configure this host as an OpenVPN Cloud Connector.
    Before this utility can be run, you must have configured a connector in
    the OpenVPN Cloud web portal where an setup token is provided.  This
    token is used by this utility to download the proper VPN configuration
    profile and complete the configuration.
    
    Enter setup token: <PROVIDED_TOKEN_VALUE>
    
    Downloading OpenVPN Cloud Connector profile ... Done
    Importing VPN configuration profile "OpenVPNCloud" ... Done
    Enabling openvpn3-session@OpenVPNCloud.service during boot ... Done
    Starting openvpn3-session@OpenVPNCloud.service ... Done
    [root@host: ~] #

At this point everything should be configured and a VPN connection is
established to the OpenVPN Cloud service.

It is also possible to provide the setup token on the command line:

    [root@host: ~] # openvpn-connector-setup --token <PROVIDED_TOKEN_VALUE>


Options
-------
|                                    |                                                                                                             |
|------------------------------------|-------------------------------------------------------------------------------------------------------------|
|-h, --help                          | show a help message and exit                                                                                |
|--mode `MODE`                       | Valid values: _systemd-unit_ (default), _autoload_ - uses openvpn3-autoload to start the connection at boot |
|--token `TOKEN_VALUE`               | This value is provided by the OpenVPN Cloud we portal.                                                      |
|--name `NAME`                       | Configuration profile name to use. Default: _"OpenVPNCloud"_                                                |
|--force                             | Overwrite existing imported profiles                                                                        |
|--autoload-file-prefix  `PREFIX`    | Configuration filename to use in the `/etc/openvpn3/autoload/` directory. Default: _OpenVPNCloud_           |
|--no-start                          | Do not configure the profile to start at boot                                                               |
|--dco                               | Use the OpenVPN Data Channel Offload (DCO) by default (unavailable with _autoload_ mode)                    |


Manage VPN configurations and sessions
--------------------------------------
To further manage the VPN configuration and session see the
[OpenVPN 3 Linux documentation](https://github.com/OpenVPN/openvpn3-linux/tree/master/docs/man/),
in particular these man pages:

* [`openvpn3-sessions-list`\(1)](https://github.com/OpenVPN/openvpn3-linux/blob/master/docs/man/openvpn3-sessions-list.1.rst)
* [`openvpn3-session-manage`\(1)](https://github.com/OpenVPN/openvpn3-linux/blob/master/docs/man/openvpn3-session-manage.1.rst)
* [`openvpn3-configs-list`\(1)](https://github.com/OpenVPN/openvpn3-linux/blob/master/docs/man/openvpn3-configs-list.1.rst)
* [`openvpn3-config-manage`\(1)](https://github.com/OpenVPN/openvpn3-linux/blob/master/docs/man/openvpn3-config-manage.1.rst)
* [`openvpn3-autoload`\(8)](https://github.com/OpenVPN/openvpn3-linux/blob/master/docs/man/openvpn3-autoload.8.rst)


Project details
---------------

This is an Open Source project and the code is published in three different git repositories

* [MAIN] **Codeberg**: https://codeberg.org/OpenVPN/openvpn-connector-setup/
* [MIRROR] *GitLab*: https://gitlab.com/openvpn/openvpn-connector-setup/
* [MIRROR] *GitHub*: https://github.com/OpenVPN/openvpn-connector-setup/

Report issues using Codeberg.

Copyright
---------
Copyright (C) OpenVPN Inc.  This program is free software: you can
redistribute it and/or modify it under the terms of the
[GNU Affero General Public License](https://www.gnu.org/licenses/agpl-3.0.html)
as published by the Free Software Foundation, version 3 License.
