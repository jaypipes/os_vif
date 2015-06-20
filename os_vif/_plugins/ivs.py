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


class IvsBridgePlugin(base.PluginBase):
    """An IVS VIF type that uses a standard Linux bridge for integration."""

    VIF_TYPE = 'ivs'
    SUPPORTED_VNIC_TYPES = (vnic_types.NORMAL,)

    def plug(self, instance, vif):
        iface_id = vif.ovs_interfaceid
        dev = vif.devname
        linux_net.create_tap_dev(dev)
        linux_net.create_ivs_vif_port(dev, iface_id, vif.address,
                                      instance.uuid)

    def unplug(self, vif):
        """Unplug the VIF by deleting the port from the bridge."""
        linux_net.delete_ivs_vif_port(vif.devname)
