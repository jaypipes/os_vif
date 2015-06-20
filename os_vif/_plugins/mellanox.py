#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_concurrency import processutils

from os_vif import base
from os_vif import exception
from os_vif import vnic_types

_DEV_PREFIX_ETH = 'eth'


class MellanoxDirectPlugin(base.PluginBase):
    """
    A VIF type that plugs the interface directly into the Mellanox physical
    network fabric.
    """

    VIF_TYPE = 'mlnx_direct'
    SUPPORTED_VNIC_TYPES = (vnic_types.DIRECT,)

    def plug(self, instance, vif):
        vnic_mac = vif.address
        device_id = instance.uuid
        fabric = vif.physical_network
        if not fabric:
            raise exception.NetworkMissingPhysicalNetwork(
                network_uuid=vif.network.id)
        dev_name = vif.devname_with_prefix(_DEV_PREFIX_ETH)
        processutils.execute('sudo', 'ebrctl', 'add-port', vnic_mac,
                             device_id, fabric,
                             MellanoxDirectPlugin.VIF_TYPE, dev_name)

    def unplug(self, vif):
        vnic_mac = vif.address
        fabric = vif.physical_network
        if not fabric:
            raise exception.NetworkMissingPhysicalNetwork(
                network_uuid=vif.network.id)
        processutils.execute('sudo', 'ebrctl', 'del-port',
                             fabric, vnic_mac)
