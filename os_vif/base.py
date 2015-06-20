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

import abc

import six


@six.add_metaclass(abc.ABCMeta)
class PluginBase(object):
    """Base class for all VIF plugins."""

    VIF_TYPE = 'unknown'
    """
    Should be overridden with a string representing the VIF type the plugin
    supports.
    """

    SUPPORTED_VNIC_TYPES = (None, )
    """
    Should be overridden with one or more constants for VNIC types in
    `os_vif.vnic_types`.
    """

    def __init__(self, **config):
        """
        Sets up the plugin using supplied kwargs representing configuration
        options.
        """
        self.config = config

    @abc.abstractmethod
    def do_plug(self, instance, vif):
        """
        Given a model of a VIF, perform operations to plug the VIF properly.

        :param instance: `nova.objects.Instance` object.
        :param vif: `os_vif.objects.VIF` object.
        :raises `processutils.ProcessExecutionError`. Plugins implementing
                this method should let `processutils.ProcessExecutionError`
                bubble up. The plug() method catches, logs, and raises a
                standardized os_vif library exception.
        """
        raise NotImplementedError('do_plug')

    @abc.abstractmethod
    def do_unplug(self, vif):
        """
        Given a model of a VIF, perform operations to unplug the VIF properly.

        :param vif: `os_vif.objects.VIF` object.
        :raises `processutils.ProcessExecutionError`. Plugins implementing
                this method should let `processutils.ProcessExecutionError`
                bubble up. The plug() method catches, logs, and raises a
                standardized os_vif library exception.
        """
        raise NotImplementedError('do_unplug')
