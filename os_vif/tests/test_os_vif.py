# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import mock

import os_vif
from os_vif.tests import base


class TestOSVIF(base.TestCase):

    def test_something(self):
        pass

    @mock.patch('stevedore.extension.ExtensionManager')
    def test_initialize(self, mock_EM):
        self.assertEqual(None, os_vif._EXT_MANAGER)
        os_vif.initialize()
        os_vif.initialize()
        mock_EM.assert_called_once_with(
            invoke_args={}, invoke_on_load=True, namespace='os_vif')
        self.assertNotEqual(None, os_vif._EXT_MANAGER)
