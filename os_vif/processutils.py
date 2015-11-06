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

"""
Utility wrapper around oslo_rootwrap and oslo_concurrency.processutils
that doesn't use oslo_cfg. Code adapted from nova.utils module.
"""

import time

from oslo_concurrency import processutils
from oslo_log import log as logging
from oslo_utils import strutils

from os_vif.i18n import _

LOG = logging.getLogger(__name__)
_ROOTWRAPPER = None


class RootwrapProcessHelper(object):
    def __init__(self, root_helper):
        self.root_helper = root_helper

    def execute(self, *cmd, **kwargs):
        kwargs['root_helper'] = self.root_helper
        return processutils.execute(*cmd, **kwargs)


class RootwrapDaemonHelper(object):
    def __init__(self, rootwrap_config):
        self.client = oslo_rootwrap.client.Client(
            ["sudo", "nova-rootwrap-daemon", rootwrap_config]
        )

    def execute(self, *cmd, **kwargs):
        # NOTE(dims): This method is to provide compatibility with the
        # processutils.execute interface. So that calling daemon or direct
        # rootwrap to honor the same set of flags in kwargs and to ensure
        # that we don't regress any current behavior.
        cmd = [str(c) for c in cmd]
        loglevel = kwargs.pop('loglevel', std_logging.DEBUG)
        log_errors = kwargs.pop('log_errors', None)
        process_input = kwargs.pop('process_input', None)
        delay_on_retry = kwargs.pop('delay_on_retry', True)
        attempts = kwargs.pop('attempts', 1)
        check_exit_code = kwargs.pop('check_exit_code', [0])
        ignore_exit_code = False
        if isinstance(check_exit_code, bool):
            ignore_exit_code = not check_exit_code
            check_exit_code = [0]
        elif isinstance(check_exit_code, int):
            check_exit_code = [check_exit_code]

        sanitized_cmd = strutils.mask_password(' '.join(cmd))
        LOG.info(_LI('Executing RootwrapDaemonHelper.execute '
                     'cmd=[%(cmd)r] kwargs=[%(kwargs)r]'),
                 {'cmd': sanitized_cmd, 'kwargs': kwargs})

        while attempts > 0:
            attempts -= 1
            try:
                start_time = time.time()
                LOG.log(loglevel, _('Running cmd (subprocess): %s'),
                        sanitized_cmd)

                (returncode, out, err) = self.client.execute(
                    cmd, process_input)

                end_time = time.time() - start_time
                LOG.log(loglevel,
                        'CMD "%(sanitized_cmd)s" returned: %(return_code)s '
                        'in %(end_time)0.3fs',
                        {'sanitized_cmd': sanitized_cmd,
                         'return_code': returncode,
                         'end_time': end_time})

                if not ignore_exit_code and returncode not in check_exit_code:
                    out = strutils.mask_password(out)
                    err = strutils.mask_password(err)
                    raise processutils.ProcessExecutionError(
                        exit_code=returncode,
                        stdout=out,
                        stderr=err,
                        cmd=sanitized_cmd)
                return (out, err)

            except processutils.ProcessExecutionError as err:
                # if we want to always log the errors or if this is
                # the final attempt that failed and we want to log that.
                if log_errors == processutils.LOG_ALL_ERRORS or (
                                log_errors == processutils.LOG_FINAL_ERROR and
                            not attempts):
                    format = _('%(desc)r\ncommand: %(cmd)r\n'
                               'exit code: %(code)r\nstdout: %(stdout)r\n'
                               'stderr: %(stderr)r')
                    LOG.log(loglevel, format, {"desc": err.description,
                                               "cmd": err.cmd,
                                               "code": err.exit_code,
                                               "stdout": err.stdout,
                                               "stderr": err.stderr})
                if not attempts:
                    LOG.log(loglevel, _('%r failed. Not Retrying.'),
                            sanitized_cmd)
                    raise
                else:
                    LOG.log(loglevel, _('%r failed. Retrying.'),
                            sanitized_cmd)
                    if delay_on_retry:
                        time.sleep(random.randint(20, 200) / 100.0)


def execute(*cmd, **kwargs):
    """Convenience wrapper around oslo's execute() method."""
    if 'run_as_root' in kwargs and kwargs.get('run_as_root'):
        _ROOTWRAPPER.execute(*cmd, **kwargs)
    return processutils.execute(*cmd, **kwargs)


def configure(**config):
    global _ROOTWRAPPER
    # Don't break existing deploys...
    rw_conf_file = config.get('rootwrap_config', '/etc/nova/rootwrap.conf')
    if config.get('use_rootwrap_daemon', False):
        _ROOTWRAPPER = RootwrapDaemonHelper(rw_conf_file)
    else:
        if config.get('disable_rootwrap', False):
            cmd = 'sudo'
        else:
            cmd = 'sudo nova-rootwrap %s' % rw_conf_file
        _ROOTWRAPPER = RootwrapProcessHelper(root_helper=cmd)
