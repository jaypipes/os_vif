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

from os_vif.i18n import _


class ExceptionBase(Exception):
    """Base Exception

    To correctly use this class, inherit from it and define
    a 'msg_fmt' property. That msg_fmt will get printf'd
    with the keyword arguments provided to the constructor.

    """
    msg_fmt = _("An unknown exception occurred.")

    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs

        if not message:
            try:
                message = self.msg_fmt % kwargs
            except Exception:
                # at least get the core message out if something happened
                message = self.msg_fmt

        self.message = message
        super(ExceptionBase, self).__init__(message)

    def format_message(self):
        # NOTE(mrodden): use the first argument to the python Exception object
        # which should be our full NovaException message, (see __init__)
        return self.args[0]


class LibraryNotInitialized(ExceptionBase):
    msg_fmt = _("Before using the os_vif library, you need to call "
                "os_vif.initialize()")


class NoMatchingPlugin(ExceptionBase):
    msg_fmt = _("No VIF plugin was found with the name %(plugin_name)s")


class PlugException(ExceptionBase):
    msg_fmt = _("Failed to plug VIF %(vif)s. Got error: %(err)s")


class UnplugException(ExceptionBase):
    msg_fmt = _("Failed to unplug VIF %(vif)s. Got error: %(err)s")


class NetworkMissingPhysicalNetwork(ExceptionBase):
    msg_fmt = _("Physical network is missing for network %(network_uuid)s")
