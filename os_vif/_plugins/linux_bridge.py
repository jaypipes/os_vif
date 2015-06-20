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

from os_vif import base
from os_vif import linux_net
from os_vif import vnic_types


class LinuxBridgePlugin(base.PluginBase):
    """A VIF type that uses a standard Linux bridge device."""

    VIF_TYPE = 'bridge'
    SUPPORTED_VNIC_TYPES = (vnic_types.NORMAL,)

    def plug(self, instance, vif):
        """Ensure that the bridge exists, and add VIF to it."""
        network = vif.network
        bridge_name = vif.bridge_name
        if not network.multi_host and network.should_create_bridge:
            mtu = self.config.get('network_device_mtu')
            if network.should_create_vlan:
                iface = self.config.get('vlan_interface',
                                        network.bridge_interface)
                linux_net.ensure_vlan_bridge(network.vlan,
                                             bridge_name, iface, mtu=mtu)
            else:
                iface = self.config.get('flat_interface',
                                        network.bridge_interface)
                linux_net.ensure_bridge(bridge_name, iface)

    def unplug(self, vif):
        # Nothing required to unplug a port for a VIF using standard
        # Linux bridge device...
        pass
