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

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs

from gbpui import client
from gbpui import column_filters as gfilters

import tables


class L3PolicyDetailsTab(tabs.Tab):
    name = _("L3 Policy Details")
    slug = "l3_policy_details"
    template_name = "project/endpoint_groups/_l3_policy_details.html"
    failure_url = reverse_lazy('horizon:project:network_policy:index')

    def get_context_data(self, request):
        l3policy_id = self.tab_group.kwargs['l3policy_id']
        try:
            l3policy = client.l3policy_get(request, l3policy_id)
        except Exception:
            exceptions.handle(
                request, _('Unable to retrieve l3 policy details.'),
                redirect=self.failure_url)
        return {'l3policy': l3policy}


class L3PolicyTab(tabs.TableTab):
    table_classes = (tables.L3PolicyTable,)
    name = _("L3 Policy")
    slug = "l3policy"
    template_name = "horizon/common/_detail_table.html"

    def get_l3policy_table_data(self):
        policies = []
        try:
            policies = client.l3policy_list(self.request,
                tenant_id=self.request.user.tenant_id)
            update = lambda x: gfilters.update_l3_policy_attributes(
                self.request, x)
            policies = [update(item) for item in policies]
        except Exception:
            policies = []
            exceptions.handle(self.tab_group.request,
                              _('Unable to retrieve l3 policy list.'))
        return policies


class L2PolicyTab(tabs.TableTab):
    table_classes = (tables.L2PolicyTable,)
    name = _("L2 Policies")
    slug = "l2policy"
    template_name = "horizon/common/_detail_table.html"

    def get_l2policy_table_data(self):
        policies = []
        try:
            policies = client.l2policy_list(self.request,
                tenant_id=self.request.user.tenant_id)
        except Exception:
            policies = []
            exceptions.handle(self.tab_group.request,
                              _('Unable to retrieve l2 policy list.'))
        return policies


class ServicePolicyTab(tabs.TableTab):
    table_classes = (tables.ServicePolicyTable,)
    name = _("Service Policy")
    slug = "service_policy"
    template_name = "horizon/common/_detail_table.html"

    def get_service_policy_table_data(self):
        policies = []
        try:
            policies = client.networkservicepolicy_list(self.request,
                tenant_id=self.request.user.tenant_id)
            update = lambda x: gfilters.update_service_policy_attributes(x)
            policies = [update(item) for item in policies]
        except Exception:
            exceptions.handle(self.tab_group.request,
                    _('Unable to retrieve network service policy list.'))
        return policies


class ServicePolicyDetailsTab(tabs.Tab):
    name = _("Service Policy Details")
    slug = "service_policy_details"
    template_name = "project/network_policy/_service_policy_details.html"
    failure_url = reverse_lazy('horizon:project:network_policy:index')

    def get_context_data(self, request):
        policy_id = self.tab_group.kwargs['service_policy_id']
        try:
            policy = client.get_networkservice_policy(request, policy_id)
        except Exception:
            exceptions.handle(
                request, _('Unable to retrieve service policy details.'),
                redirect=self.failure_url)
        return {'policy': policy}


class ExternalConnectivityTab(tabs.TableTab):
    table_classes = (tables.ExternalConnectivityTable,)
    name = _("External Connectivity")
    slug = "external_connectivity"
    template_name = "horizon/common/_detail_table.html"

    def get_external_connectivity_table_data(self):
        external_segment_list = []
        try:
            external_segment_list = \
                client.externalconnectivity_list(self.request,
                    self.request.user.tenant_id)
        except Exception:
            exceptions.handle(self.tab_group.request,
                    _('Unable to retrieve network service policy list.'))
        return external_segment_list


class ExternalConnectivityDetailsTab(tabs.Tab):
    name = _("External Connectivity Details")
    slug = "external_connectivity_details"
    template_name = \
        "project/network_policy/_external_connectivity_details.html"
    failure_url = reverse_lazy('horizon:project:network_policy:index')

    def get_context_data(self, request):
        external_connectivity_id = \
            self.tab_group.kwargs['external_connectivity_id']
        try:
            external_connectivity = client.get_externalconnectivity(request,
                external_connectivity_id)
        except Exception:
            exceptions.handle(
                request, _('Unable to retrieve service policy details.'),
                redirect=self.failure_url)
        return {'external_connectivity': external_connectivity}


class NATPoolTab(tabs.TableTab):
    table_classes = (tables.NATPoolTable,)
    name = _("NAT Pool")
    slug = "nat_pool"
    template_name = "horizon/common/_detail_table.html"

    def get_nat_pool_table_data(self):
        nat_pool_list = []
        try:
            nat_pools = \
                client.natpool_list(self.request,
                    self.request.user.tenant_id)
            update = lambda x: gfilters.update_nat_pool_attributes(
                self.request, x)
            nat_pool_list = [update(nat_pool) for nat_pool in nat_pools]
        except Exception:
            exceptions.handle(self.tab_group.request,
                    _('Unable to retrieve nat pool list.'))
        return nat_pool_list


class NATPoolDetailsTab(tabs.Tab):
    name = _("NAT Pool Details")
    slug = "nat_pool_details"
    template_name = \
        "project/network_policy/_nat_pool_details.html"
    failure_url = reverse_lazy('horizon:project:network_policy:index')

    def get_context_data(self, request):
        nat_pool_id = \
            self.tab_group.kwargs['nat_pool_id']
        try:
            nat_pool = client.get_natpool(request,
                nat_pool_id)
        except Exception:
            exceptions.handle(
                request, _('Unable to retrieve nat pool details.'),
                redirect=self.failure_url)
        return {'nat_pool': nat_pool}


class ServicePolicyDetailsTabs(tabs.TabGroup):
    slug = "service_policy_details_tab"
    tabs = (ServicePolicyDetailsTab,)
    sticky = True


class ExternalConnectivityDetailsTabs(tabs.TabGroup):
    slug = "external_connectivity_details_tab"
    tabs = (ExternalConnectivityDetailsTab,)
    sticky = True


class NATPoolDetailsTabs(tabs.TabGroup):
    slug = "nat_pool_details_tab"
    tabs = (NATPoolDetailsTab,)
    sticky = True


class L3PolicyTabs(tabs.TabGroup):
    slug = "l3policy_tab"
    tabs = (L3PolicyTab, ServicePolicyTab, ExternalConnectivityTab, NATPoolTab)
    sticky = True


class L2PolicyDetailsTab(tabs.Tab):
    name = _("L2 Policy Details")
    slug = "l2_policy_details"
    template_name = "project/network_policy/_l2_policy_details.html"
    failure_url = reverse_lazy('horizon:project:endpoint_group:index')

    def get_context_data(self, request):
        l2policy_id = self.tab_group.kwargs['l2policy_id']
        try:
            l2policy = client.l2policy_get(request, l2policy_id)
            ptgs = []
            for item in l2policy.policy_target_groups:
                ptgs.append(client.policy_target_get(request, item))
            setattr(l2policy, 'ptgs', ptgs)
        except Exception:
            exceptions.handle(
                request, _('Unable to retrieve l2 policy details.'),
                redirect=self.failure_url)
        return {'l2policy': l2policy}


class L2PolicyDetailsTabs(tabs.TabGroup):
    slug = "l2policy_tabs"
    tabs = (L2PolicyDetailsTab,)


class L3PolicyDetailsTabs(tabs.TabGroup):
    slug = "l3policy_tabs"
    tabs = (L3PolicyDetailsTab, L2PolicyTab,)
