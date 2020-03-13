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

from base64 import b64decode, b64encode

class DecodeToken(object):
    """Decode the OpenVPN Cloud setup token"""
    def __init__(self, token, split_point=40):
        #
        # Token format:  [ENCRYPTION_KEY][FILEREF]
        #
        # ENCRYPTION_KEY is BASE64 encoded data, used to decrypt the
        #      downloaded connector profile, variable length
        # FILEREF is the reference to the file being downloaded,
        #      always 40 characters
        #
        l = len(token)
        if l < split_point:
            raise RuntimeError("Incorrect token value: %s "
                               + "(length %i, expected at least %i)"
                               % (token, l, split_point))

        self.__key = token[:-split_point]
        self.__fileref = token[-split_point:]

    def GetKey(self):
        """Retrieve the encryption password"""
        return b64decode(self.__key)

    def OverrideKey(self, key):
        """Overrides the encryption key from the token. Used for testing and debugging"""
        self.__key = b64encode(key.encode('utf-8'))

    def GetFileRef(self):
        """Retrieve the file reference needed to download the encrypted configuration profile"""
        return self.__fileref

    def OverrideFileRef(self, fref):
        """Overrides the file reference from the token. Used for testing and debugging"""
        self.__fileref = fref

    def __repr__(self):
        return '<DecodeToken key="%s", fileref="%s">' \
            % (self.__key, self.__fileref)
