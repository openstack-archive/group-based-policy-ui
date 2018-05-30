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
import re

from django.conf import settings
from django import shortcuts
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from openstack_dashboard import api
from openstack_dashboard.api.rest import utils as rest_utils

from horizon import exceptions

from gbpui import client

from netaddr import IPAddress
from netaddr import IPNetwork

import logging

LOG = logging.getLogger(__name__)


class PolicyTargets(generic.View):
    # todo: This is a direct port from the old form version; it needs to be
    #       tested and revised; It may be dodgy and/or redundant because:
    #       1)  The created regex might be nonsenseical (needs testing)
    #       2)  The proxy_group_ids might be logical duplication of the third
    #           third conditional
    @staticmethod
    def is_proxy_group(policy_target, proxy_group_ids):
        if hasattr(settings, 'GBPUI_HIDE_PTG_NAMES_FROM_MEMBER_CREATE'):
            regex = "(" + ")|(".join(
                settings.GBPUI_HIDE_PTG_NAMES_FROM_MEMBER_CREATE) \
                + ")"

            if re.match(regex, policy_target.get('name')):
                return True

        if policy_target.id in proxy_group_ids:
            return True

        if policy_target.get('proxied_group_id'):
            return True

        return False

    @rest_utils.ajax()
    def get(self, request):
        policy_targets = client.policy_target_list(
            request, tenant_id=request.user.tenant_id
        )

        proxy_group_ids = [pt.get('proxy_group_id') for pt in policy_targets
                           if pt.get('proxy_group_id')]

        try:
            policy_target_objects = []

            for policy_target in policy_targets:
                if not self.is_proxy_group(policy_target, proxy_group_ids):
                    subnet_objects = []

                    for subnet_id in policy_target.subnets:
                        try:
                            subnet = api.neutron.subnet_get(request, subnet_id)
                            allocation_pool_objects = []

                            allocation_pools = subnet['allocation_pools']
                            if allocation_pools:
                                for allocation_pool in allocation_pools:
                                    allocation_pool_object = {
                                        "start": allocation_pool['start'],
                                        "end": allocation_pool['end']
                                    }
                                    allocation_pool_objects.append(
                                        allocation_pool_object)

                            subnet_object = {
                                "cidr": subnet['cidr'],
                                "allocation_pools": allocation_pool_objects
                            }
                            subnet_objects.append(subnet_object)
                        except Exception:
                            LOG.exception("Unable to retrieve subnet.")

                    policy_target_object = {
                        "id": policy_target.id,
                        "name_or_id": policy_target.name_or_id,
                        "subnets": subnet_objects
                    }
                    policy_target_objects.append(policy_target_object)

            return rest_utils.JSONResponse(policy_target_objects)
        except Exception:
            msg = _("Failed to retrieve groups")
            LOG.error(msg)
            exceptions.handle(request, msg, redirect=shortcuts.redirect)


class Members(generic.View):
    optional_arguments = [
        'block_device_mapping',
        'block_device_mapping_v2',
        'availability_zone',
        'admin_pass', 'disk_config',
        'config_drive', "scheduler_hints"
    ]

    @rest_utils.ajax()
    def post(self, request):
        instance_count = request.DATA['instance_count']

        try:
            if instance_count == 1:
                self.create_instance(request)
            elif instance_count > 1:
                for i in range(0, instance_count):
                    self.create_instance(request, "_" + str(i))

        except Exception:
            instance_name = request.DATA['name']

            error = _("Unable to launch member %(count)s with name %(name)s")
            message = error % {
                'count': instance_count,
                'name': instance_name
            }
            LOG.exception(message)

            raise rest_utils.AjaxError(400, message)

        return rest_utils.CreatedResponse('/api/nova/servers/%s')

    def create_instance(self, request, suffix=""):
        # Instances need to be created one by one, because each instance
        # needs to have it's own GBP port
        kw = {
            'instance_count': 1
        }

        # Mandatory creation arguments and port creation
        try:
            instance_name = request.DATA['name'] + suffix

            if "group_policy_targets" in request.DATA and (
                    request.DATA["group_policy_targets"]):
                meta_data, nics = self.create_ports(request, instance_name)

                kw['meta'] = meta_data
                kw['nics'] = nics
            else:
                if 'nics' in request.DATA:
                    kw['nics'] = request.DATA['nics']
                if 'meta' in request.DATA:
                    kw['meta'] = request.DATA['meta']

            args = (
                request,
                instance_name,
                request.DATA['source_id'],
                request.DATA['flavor_id'],
                request.DATA['key_name'],
                request.DATA['user_data'],
                request.DATA['security_groups'],
            )

        except KeyError as e:
            raise rest_utils.AjaxError(400, 'Missing required parameter '
                                            "'%s'" % e.args[0])

        # Optional creation arguments
        for name in self.optional_arguments:
            if name in request.DATA:
                kw[name] = request.DATA[name]

        return api.nova.server_create(*args, **kw)

    # 1) Missing request.DATA entries get propagated to 'create_instance' as
    #    KeyError
    # 2) All other errors are propagated to 'post' as generic failure Exception
    @staticmethod
    def create_ports(request, instance_name):
        nics = []
        pts = []

        for policy_target_id in request.DATA["group_policy_targets"]:
            policy_target = client.policy_target_get(request,
                                                     policy_target_id['id'])

            args = {
                'policy_target_group_id': policy_target.id,
                'name': instance_name[:41] + "_gbpui"
            }

            for subnet_id in policy_target.subnets:
                subnet = api.neutron.subnet_get(request, subnet_id)

                if 'fixed_ip' in policy_target_id and IPAddress(
                        policy_target_id['fixed_ip']) in \
                        IPNetwork(subnet['cidr']):
                    args['fixed_ips'] = [{
                        'subnet_id': subnet['id'],
                        'ip_address': policy_target_id['fixed_ip']
                    }]

            port = client.pt_create(request, **args)

            nics.append({
                'port-id': port.port_id
            })
            pts.append(port.id)

        meta_data = {'pts': ','.join(pts)}

        return meta_data, nics
