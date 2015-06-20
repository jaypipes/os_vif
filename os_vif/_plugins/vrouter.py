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


class VrouterPlugin(base.PluginBase):
    """A VIF type that plugs into a Contrail network port."""

    VIF_TYPE = 'vrouter'
    SUPPORTED_VNIC_TYPES = (vnic_types.NORMAL,)

    def plug(self, instance, vif):
        """Plug into Contrail's network port

        Bind the vif to a Contrail virtual port.
        """
        dev = vif.devname
        ip_addr = '0.0.0.0'
        ip6_addr = None
        subnets = vif.network.subnets
        for subnet in subnets:
            if not subnet.ips:
                continue
            ips = subnet.ips[0]
            if not ips.address:
                continue
            if ips.version == 4:
                if ips.address is not None:
                    ip_addr = ips.address
            if ips.version == 6:
                if ips.address is not None:
                    ip6_addr = ips.address

        ptype = 'NovaVMPort'
        if self.config.get('libvirt_virt_type') == 'lxc':
            ptype = 'NameSpacePort'

        cmd_args = ("--oper=add --uuid=%s --instance_uuid=%s --vn_uuid=%s "
                    "--vm_project_uuid=%s --ip_address=%s --ipv6_address=%s"
                    " --vm_name=%s --mac=%s --tap_name=%s --port_type=%s "
                    "--tx_vlan_id=%d --rx_vlan_id=%d" % (vif.id,
                    instance.uuid, vif.network.id,
                    instance.project_id, ip_addr, ip6_addr,
                    instance.display_name, vif.address,
                    dev, ptype, -1, -1))
        linux_net.create_tap_dev(dev)
        processutils.execute('sudo', 'vrouter-port-control', cmd_args)

    def unplug(self, vif):
        """Unplug Contrail's network port

        Unbind the vif from a Contrail virtual port.
        """
        dev = vif.devname
        cmd_args = "--oper=delete --uuid=%s" % vif.id
        processutils.execute('sudo', 'vrouter-port-control', cmd_args)
        linux_net.delete_net_dev(dev)
