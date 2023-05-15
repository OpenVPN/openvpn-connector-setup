#  OpenVPN Connector Setup
#      - Configure OpenVPN 3 Linux for CloudConnexa™
#
#  SPDX-License-Identifier: AGPL-3.0-only
#
#  Copyright (C) 2020 - 2023  OpenVPN Inc. <sales@openvpn.net>
#  Copyright (C) 2020 - 2023  David Sommerseth <davids@openvpn.net>
#

from setuptools import setup, find_packages
from os import path
from openvpn.connector.version import ocs_version

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    python_requires = '>=3.5',
    name = 'openvpn-connector-setup',
    version = ocs_version,
    packages=find_packages(),
    install_requires = [ 'dbus-python', 'cryptography' ],
    entry_points = {
        'console_scripts': ['openvpn-connector-setup=openvpn.connector.main:main']
    },

    author='OpenVPN Inc',
    author_email='info@openvpn.net',
    description='CloudConnexa™ connector setup utility',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='cloudconnexa openvpn-cloud openvpn-connector openvpn vpn',
    url='https://myaccount.openvpn.com/',
    project_urls={
        "Source code": "https://codeberg.org/OpenVPN/openvpn-connector-setup",
    },
    classifiers=[
        'License :: OSI Approved :: AGPLv3',
    ]
)
