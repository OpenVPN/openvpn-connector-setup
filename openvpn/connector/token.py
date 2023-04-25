#  OpenVPN Connector Setup
#      - Configure OpenVPN 3 Linux for CloudConnexa™
#
#  SPDX-License-Identifier: AGPL-3.0-only
#
#  Copyright (C) 2020 - 2023  OpenVPN Inc. <sales@openvpn.net>
#  Copyright (C) 2020 - 2023  David Sommerseth <davids@openvpn.net>
#

from base64 import b64decode, b64encode

class DecodeToken(object):
    """Decode the CloudConnexa setup token"""
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
