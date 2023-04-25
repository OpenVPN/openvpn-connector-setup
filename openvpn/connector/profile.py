#  OpenVPN Connector Setup
#      - Configure OpenVPN 3 Linux for CloudConnexa™
#
#  SPDX-License-Identifier: AGPL-3.0-only
#
#  Copyright (C) 2020 - 2023  OpenVPN Inc. <sales@openvpn.net>
#  Copyright (C) 2020 - 2023  David Sommerseth <davids@openvpn.net>
#

import os
from base64 import b64decode
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import cryptography.exceptions
from urllib import request
from urllib.parse import urljoin
from openvpn.connector.token import DecodeToken


OPENVPN_CLOUD_BASEURL='https://cloud-backend.openvpn.com/cvpn/api/v1/profiles/'
if 'OPENVPN_CLOUD_BASEURL' in os.environ:
    OPENVPN_CLOUD_BASEURL=os.environ['OPENVPN_CLOUD_BASEURL']

#
#  Various specific exceptions
#
class DecryptError(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class DownloadError(Exception):
    def __init__(self, msg, url):
        super().__init__(msg)
        self._url = url

    def GetURL(self):
        return self._url


class DecryptProfile(object):
    """Decrypt an encrypted CloudConnexa profile"""

    def __init__(self, password, key_len=32, iterations=25000):
        self._password = password
        self._key_len = key_len
        self._salt_len = 32
        self._gcm_iv_len = 12
        self._gcm_tag_len = 16
        self._pbkdf2_iterations = iterations
        self._backend = default_backend()


    def _get_key_pbkdf2(self, password, salt):
        """Derive the encryption key and IV from the password and salt"""

        kdf = PBKDF2HMAC(
            algorithm=SHA256(),
            length=self._key_len + self._gcm_iv_len,
            salt=salt,
            iterations=self._pbkdf2_iterations,
            backend=self._backend)
        key = kdf.derive(password)

        self._decrkey = key[:self._key_len]
        self._iv = key[self._key_len:self._key_len + self._gcm_iv_len]



    def Retrieve(self, profile):
        """Decode and decrypt the profile payload"""

        # BASE64 decode the payload and extract the
        # salt, encrypted data and GCM authentication tag
        payload = None
        try:
            payload = b64decode(profile)
        except BaseException as err:
            raise DecryptError("Could not decode profile (" + str(err) + ")")

        salt = payload[0:self._salt_len]
        data = payload[self._salt_len:-self._gcm_tag_len]
        gcmtag = payload[-self._gcm_tag_len:]

        # Derive the needed keys and IV.  Those are stored
        # internally in this object
        try:
            self._get_key_pbkdf2(self._password, salt)
        except BaseException as err:
            raise DecryptError("PBKDF2 key derivation failed (" + str(err) + ")")

        # Decrypt the data part of the payload
        # The payload is AES-GCM encrypted and the decrypted
        # data will be authenticated as part of the decryption.
        try:
            ciphdecr = Cipher(algorithms.AES(self._decrkey),
                              modes.GCM(self._iv, gcmtag),
                              backend=self._backend).decryptor()
            return (ciphdecr.update(data)
                    + ciphdecr.finalize())
        except cryptography.exceptions.InvalidTag as err:
              raise DecryptError("Invalid AES-GCM authentication tag")
        except BaseException as err:
              raise DecryptError("Error while decrypting data: " + str(err))



class ProfileFetch(object):
    """Download an encrypted CloudConnexa configuration profile"""

    def __init__(self, token, baseurl=OPENVPN_CLOUD_BASEURL):
        if not isinstance(token, DecodeToken):
            raise ValueError('token argument is not an DecodeToken object')
        self.__baseurl = baseurl
        self.__token = token


    def Download(self):
        """Downloads an encrypted CloudConnexa client profile and decrypt it"""
        res = None
        try:
            dl_url = urljoin(self.__baseurl, self.__token.GetFileRef())
            req = request.Request(dl_url)
            req.add_header('User-agent', 'openvpn-connector-setup')
            res = request.urlopen(req)
        except BaseException as err:
              raise DownloadError("Failed to download profile: " + str(err),
                                  dl_url)

        b64prf = res.read().decode('utf-8')
        decrypt = DecryptProfile(self.__token.GetKey())
        self.__profile = decrypt.Retrieve(b64prf)


    def Save(self, dest):
        """Save the downloaded and decrypted profile to disk"""
        fp = open(dest, 'wb')
        fp.write(self.__profile)
        fp.close()


    def GetProfile(self):
        """Retrieve the downloaded and decrypted profile as a string"""
        return self.__profile.decode('utf-8')
