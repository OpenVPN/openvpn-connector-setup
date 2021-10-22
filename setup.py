#  OpenVPN Connector Setup
#      - Configure OpenVPN 3 Linux for OpenVPN Cloud
#
#  Copyright (C) 2020 - 2021  OpenVPN Inc. <sales@openvpn.net>
#  Copyright (C) 2020 - 2021  David Sommerseth <davids@openvpn.net>
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

from setuptools import setup, find_packages
from os import path
from version import ocs_version

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
    description='OpenVPN Cloud Connector setup utility',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='openvpn-cloud openvpn-connector openvpn vpn',
    url='https://openvpn.cloud/',
    project_urls={
        "Source code": "https://github.com/OpenVPN/openvpn-connector-setup",
    },
    classifiers=[
        'License :: OSI Approved :: AGPLv3',
    ]
)
