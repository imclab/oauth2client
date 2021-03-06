# Copyright 2014 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import mock
import os
import sys
import unittest

try:
  reload
except NameError:
  # For Python3 (though importlib should be used, silly 3.3).
  from imp import reload

from oauth2client.client import HAS_OPENSSL
from oauth2client.client import SignedJwtAssertionCredentials
from oauth2client import crypt


def datafile(filename):
  f = open(os.path.join(os.path.dirname(__file__), 'data', filename), 'rb')
  data = f.read()
  f.close()
  return data


class Test_pkcs12_key_as_pem(unittest.TestCase):

  def _make_signed_jwt_creds(self, private_key_file='privatekey.p12',
                             private_key=None):
    private_key = private_key or datafile(private_key_file)
    return SignedJwtAssertionCredentials(
        'some_account@example.com',
        private_key,
        scope='read+write',
        sub='joe@example.org')

  def test_succeeds(self):
    self.assertEqual(True, HAS_OPENSSL)

    credentials = self._make_signed_jwt_creds()
    pem_contents = crypt.pkcs12_key_as_pem(credentials.private_key,
                                           credentials.private_key_password)
    pkcs12_key_as_pem = datafile('pem_from_pkcs12.pem')
    pkcs12_key_as_pem = crypt._parse_pem_key(pkcs12_key_as_pem)
    self.assertEqual(pem_contents, pkcs12_key_as_pem)

  def test_without_openssl(self):
    openssl_mod = sys.modules['OpenSSL']
    try:
      sys.modules['OpenSSL'] = None
      reload(crypt)
      self.assertRaises(NotImplementedError, crypt.pkcs12_key_as_pem,
                        'FOO', 'BAR')
    finally:
      sys.modules['OpenSSL'] = openssl_mod
      reload(crypt)

  def test_with_nonsense_key(self):
    credentials = self._make_signed_jwt_creds(private_key=b'NOT_A_KEY')
    self.assertRaises(crypt.crypto.Error, crypt.pkcs12_key_as_pem,
                      credentials.private_key, credentials.private_key_password)
