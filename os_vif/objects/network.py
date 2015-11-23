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

from oslo_versionedobjects import base
from oslo_versionedobjects import fields


class Network(base.VersionedObject):
    """Represents a network."""
    # Version 1.0: Initial version
    VERSION = '1.0'

    fields = {
        'id': fields.UUIDField(),
        'bridge': fields.StringField(),
        'label': fields.StringField(),
        'subnets': fields.ObjectField('SubnetList', nullable=True),
        'multi_host': fields.BooleanField(),
        'should_provide_bridge': fields.BooleanField(),
        'should_provide_vlan': fields.BooleanField(),
        'bridge_interface': fields.StringField(nullable=True),
        'vlan': fields.StringField(nullable=True),
    }

    obj_relationships = {
        'subnets': [
            ('1.0', '1.0'),
        ],
    }

    def __init__(self, **kwargs):
        kwargs.setdefault('subnets', [])
        kwargs.setdefault('multi_host', False)
        kwargs.setdefault('should_provide_bridge', False)
        kwargs.setdefault('should_provide_vlan', False)
        super(Network, self).__init__(**kwargs)
