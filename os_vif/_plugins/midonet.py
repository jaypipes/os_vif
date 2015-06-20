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
from os_vif import linux_net
from os_vif import vnic_types


class MidonetPlugin(base.PluginBase):
    """A VIF type that plugs into a MidoNet network port."""

    VIF_TYPE = 'midonet'
    SUPPORTED_VNIC_TYPES = (vnic_types.NORMAL,)

    def plug(self, instance, vif):
        """Plug into MidoNet's network port

        Bind the vif to a MidoNet virtual port.
        """
        dev = vif.devname
        port_id = vif.id
        linux_net.create_tap_dev(dev)
        processutils.execute('sudo', 'mm-ctl', '--bind-port', port_id, dev)

    def unplug(self, vif):
        """Unplug from MidoNet network port

        Unbind the vif from a MidoNet virtual port.
        """
        dev = vif.devname
        port_id = vif.id
        processutils.execute('sudo', 'mm-ctl', '--unbind-port', port_id)
        linux_net.delete_net_dev(dev)
