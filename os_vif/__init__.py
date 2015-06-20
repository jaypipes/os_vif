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
from oslo_log import log as logging
from stevedore import extension

import os_vif.exception
import os_vif.iptables
import os_vif.i18n
import os_vif.objects
import os_vif.linux_net

_LE = os_vif.i18n._LE
_LI = os_vif.i18n._LI

_EXT_MANAGER = None
LOG = logging.getLogger('os_vif')


def initialize(reset=False, **config):
    """
    Loads all os_vif plugins and initializes them with a dictionary of
    configuration options.
    """
    global _EXT_MANAGER
    if reset or (_EXT_MANAGER is not None):
        _EXT_MANAGER = extension.ExtensionManager(namespace='os_vif',
                                                  invoke_on_load=True,
                                                  invoke_args=config)

        ipm_options = {
            'use_ipv6': config.get('use_ipv6', False),
            'iptables_top_regex': config.get('iptables_top_regex', ''),
            'iptables_bottom_regex': config.get('iptables_bottom_regex', ''),
            'iptables_drop_action': config.get('iptables_drop_action', 'DROP'),
            'forward_bridge_interface':
                config.get('forward_bridge_interface', ['all']),
        }
        ipm = os_vif.iptables.IptablesManager(**ipm_options)
        os_vif.linux_net.iptables_manager = ipm
        os_vif.objects.register_all()


def plug(vif, instance):
    """
    Given a model of a VIF, perform operations to plug the VIF properly.

    :param vif: `os_vif.objects.VIF` object.
    :param instance: `nova.objects.Instance` object.
    :raises `exception.LibraryNotInitialized` if the user of the library
            did not call os_vif.initialize(**config) before trying to
            plug a VIF.
    :raises `exception.NoMatchingPlugin` if there is no plugin for the
            type of VIF supplied.
    :raises `exception.PlugException` if anything fails during unplug
            operations.
    """
    if _EXT_MANAGER is None:
        raise os_vif.exception.LibraryNotInitialized()

    vif_type = vif.type
    try:
        plugin = _EXT_MANAGER[vif_type]
    except KeyError:
        raise os_vif.exception.NoMatchingPlugin(vif_type=vif_type)

    try:
        LOG.debug("Plugging vif %s", vif)
        plugin.plug(vif, instance)
        LOG.info(_LI("Successfully plugged vif %s"), vif)
    except processutils.ProcessExecutionError as err:
        LOG.error(_LE("Failed to plug vif %s. Got error: %s"), vif, err)
        raise exception.PlugException(vif=vif, err=err)


def unplug(vif):
    """
    Given a model of a VIF, perform operations to unplug the VIF properly.

    :param vif: `os_vif.objects.VIF` object.
    :raises `exception.LibraryNotInitialized` if the user of the library
            did not call os_vif.initialize(**config) before trying to
            plug a VIF.
    :raises `exception.NoMatchingPlugin` if there is no plugin for the
            type of VIF supplied.
    :raises `exception.UnplugException` if anything fails during unplug
            operations.
    """
    if _EXT_MANAGER is None:
        raise os_vif.exception.LibraryNotInitialized()

    vif_type = vif.type
    try:
        plugin = _EXT_MANAGER[vif_type]
    except KeyError:
        raise os_vif.exception.NoMatchingPlugin(vif_type=vif_type)

    try:
        LOG.debug("Unplugging vif %s", vif)
        plugin.unplug(vif)
        LOG.info(_LI("Successfully unplugged vif %s"), vif)
    except processutils.ProcessExecutionError as err:
        LOG.error(_LE("Failed to unplug vif %s. Got error: %s"), vif, err)
        raise exception.UnplugException(vif=vif, err=err)
