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

import glob
import os
import re

_VIRTFN_RE = re.compile("virtfn\d+")


def get_ifname_by_pci_address(pci_addr, pf_interface=False):
    """Get the interface name based on a VF's pci address

    The returned interface name is either the parent PF's or that of the VF
    itself based on the argument of pf_interface.
    """
    if pf_interface:
        dev_path = "/sys/bus/pci/devices/%s/physfn/net" % pci_addr
    else:
        dev_path = "/sys/bus/pci/devices/%s/net" % pci_addr
    try:
        dev_info = os.listdir(dev_path)
        return dev_info.pop()
    except Exception:
        return None


def get_vf_num_by_pci_address(pci_addr):
    """Get the VF number based on a VF's pci address

    A VF is associated with an VF number, which ip link command uses to
    configure it. This number can be obtained from the PCI device filesystem.
    """
    virtfns_path = "/sys/bus/pci/devices/%s/physfn/virtfn*" % (pci_addr)
    vf_num = None
    try:
        for vf_path in glob.iglob(virtfns_path):
            if re.search(pci_addr, os.readlink(vf_path)):
                t = _VIRTFN_RE.search(vf_path)
                vf_num = t.group(1)
                break
    except Exception:
        pass
    return vf_num
