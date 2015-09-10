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

from openstack_dashboard import api
from openstack_dashboard.dashboards.project.instances import tables as itables

from gbpui import client
from gbpui import column_filters as gfilters

import tables

PTGsTable = tables.PTGsTable
External_PTGsTable = tables.ExternalPTGsTable


class PTGsTab(tabs.TableTab):
    table_classes = (PTGsTable,)
    name = _("Internal")
    slug = "policytargets"
    template_name = "horizon/common/_detail_table.html"

    def get_policy_targetstable_data(self):
        policy_targets = []
        try:
            policy_targets = client.policy_target_list(self.tab_group.request,
            tenant_id=self.tab_group.request.user.tenant_id)
            a = lambda x, y: gfilters.update_policy_target_attributes(x, y)
            policy_targets = [a(self.request, item) for item in policy_targets]
        except Exception as e:
            msg = _('Unable to retrieve policy_target list. %s') % (str(e))
            exceptions.handle(self.tab_group.request, msg)
            for policy_target in policy_targets:
                policy_target.set_id_as_name_if_empty()
        return policy_targets


class ExternalPTGsTab(tabs.TableTab):
    table_classes = (External_PTGsTable,)
    name = _("External")
    slug = "externalpolicytargets"
    template_name = "horizon/common/_detail_table.html"

    def get_external_policy_targetstable_data(self):
        external_policy_targets = []
        try:
            external_policy_targets = client.ext_policy_target_list(
                self.tab_group.request,
                tenant_id=self.tab_group.request.user.tenant_id)
            a = lambda x, y: gfilters.update_policy_target_attributes(x, y)
            external_policy_targets = [a(self.request, item)
                for item in external_policy_targets]
        except Exception as e:
            msg = _('Unable to retrieve policy_target list. %s') % (str(e))
            exceptions.handle(self.tab_group.request, msg)
            for policy_target in external_policy_targets:
                policy_target.set_id_as_name_if_empty()
        return external_policy_targets


class PTGTabs(tabs.TabGroup):
    slug = "policy_targettabs"
    tabs = (PTGsTab, ExternalPTGsTab)
    sticky = True


class PTGDetailsTab(tabs.Tab):
    name = _("Group Details")
    slug = "policy_targetdetails"
    template_name = "project/policytargets/_policy_target_details.html"
    failure_url = reverse_lazy('horizon:project:policy_target_group:index')

    def get_context_data(self, request):
        policy_targetid = self.tab_group.kwargs['policy_target_id']
        nsp = ''
        try:
            policy_target = client.policy_target_get(request, policy_targetid)
            l2_policy = client.l2policy_get(request,
                            policy_target["l2_policy_id"])
            l3_policy = client.l3policy_get(request,
                            l2_policy["l3_policy_id"])
            if policy_target['network_service_policy_id']:
                nsp_id = policy_target['network_service_policy_id']
                nsp = client.get_networkservice_policy(request, nsp_id)
        except Exception:
            exceptions.handle(
                request, _('Unable to retrieve group details.'),
                redirect=self.failure_url)
        return {'policy_target': policy_target,
                'l3_policy': l3_policy,
                'l2_policy': l2_policy,
                'nsp': nsp}


class PTGDetailsTabs(tabs.TabGroup):
    slug = "policy_targettabs"
    tabs = (PTGDetailsTab,)


class InstancesTab(tabs.TableTab):
    name = _("Members")
    slug = "members_tab"
    table_classes = (tables.InstancesTable,)
    template_name = ("horizon/common/_detail_table.html")
    preload = True

    def get_instances_data(self):
        policy_targetid = self.tab_group.kwargs['policy_target_id']
        filtered_instances = []
        try:
            policytargets = client.pt_list(self.request,
            tenant_id=self.request.user.tenant_id,
            policy_target_group_id=policy_targetid)
            policy_target_ports = [x.port_id for x in policytargets]
            marker = self.request.GET.get(
                tables.InstancesTable._meta.pagination_param, None)
            # TODO(Sumit): Setting paginate to False is a temporary
            # fix. Earlier, when paginate was set to True we were
            # retrieving instances in pages and were only processing
            # the first page. While pagination is required for
            # scaling to a large number of instances, we need to first
            # retrieve the instances in pages, then process them,
            # and then show the filtered list (filtered_instances)
            # in pages.
            instances, self._has_more = api.nova.server_list(
                self.request, search_opts={'marker': marker,
                                           'paginate': False})
            self._has_more = False
            instances = [item for item in instances
                    if not itables.is_deleting(item)]
            for item in instances:
                for port in api.neutron.port_list(self.request,
                                                  device_id=item.id):
                    if port.id in policy_target_ports:
                        filtered_instances.append(item)
                        break
        except Exception:
            self._has_more = False
            error_message = _('Unable to get instances')
            exceptions.handle(self.request, error_message)
            filtered_instances = []
        return filtered_instances


class ConsumedTab(tabs.TableTab):
    name = _('Consumed Policy Rule Set')
    slug = 'consumed_policy_rule_sets_tab'
    table_classes = (tables.ConsumedContractsTable,)
    template_name = ("horizon/common/_detail_table.html")

    def get_consumed_policy_rule_sets_data(self):
        try:
            policy_targetid = self.tab_group.kwargs['policy_target_id']
            policy_target = client.policy_target_get(
                self.request, policy_targetid)
            consumed_policy_rule_set_ids = policy_target.get(
                'consumed_policy_rule_sets')
            consumed_policy_rule_sets = []
            for _id in consumed_policy_rule_set_ids:
                consumed_policy_rule_sets.append(
                    client.policy_rule_set_get(self.request, _id))
            consumed_policy_rule_sets = [gfilters.update_pruleset_attributes(
                self.request, item) for item in consumed_policy_rule_sets]
            return consumed_policy_rule_sets
        except Exception:
            error_message = _('Unable to get consumed rule sets')
            exceptions.handle(self.request, error_message)
            return []


class ProvidedTab(tabs.TableTab):
    name = _('Provided Policy Rule Set')
    slug = 'provided_policy_rule_sets_tab'
    table_classes = (tables.ProvidedContractsTable,)
    template_name = ("horizon/common/_detail_table.html")

    def get_provided_policy_rule_sets_data(self):
        try:
            policy_targetid = self.tab_group.kwargs['policy_target_id']
            policy_target = client.policy_target_get(
                self.request, policy_targetid)
            provided_policy_rule_set_ids = policy_target.get(
                'provided_policy_rule_sets')
            provided_policy_rule_sets = []
            for _id in provided_policy_rule_set_ids:
                provided_policy_rule_sets.append(
                    client.policy_rule_set_get(self.request, _id))
            provided_policy_rule_sets = [gfilters.update_pruleset_attributes(
                self.request, item) for item in provided_policy_rule_sets]
            return provided_policy_rule_sets
        except Exception:
            error_message = _('Unable to get provided rule sets')
            exceptions.handle(self.request, error_message)
            return []


class PTGMemberTabs(tabs.TabGroup):
    slug = 'member_tabs'
    tabs = (InstancesTab, ProvidedTab, ConsumedTab, PTGDetailsTab,)
    stiky = True


class ExtProvidedTab(ProvidedTab):
    table_classes = (tables.ExtProvidedContractsTable,)

    def get_provided_policy_rule_sets_data(self):
        try:
            ext_policy_targetid = self.tab_group.kwargs['ext_policy_target_id']
            ext_policy_target = client.ext_policy_target_get(
                self.request, ext_policy_targetid)
            provided_policy_rule_set_ids = ext_policy_target.get(
                'provided_policy_rule_sets')
            provided_policy_rule_sets = []
            for _id in provided_policy_rule_set_ids:
                provided_policy_rule_sets.append(
                    client.policy_rule_set_get(self.request, _id))
            provided_policy_rule_sets = [gfilters.update_pruleset_attributes(
                self.request, item) for item in provided_policy_rule_sets]
            return provided_policy_rule_sets
        except Exception:
            error_message = _('Unable to get provided rule sets')
            exceptions.handle(self.request, error_message)
            return []


class ExtConsumedTab(ConsumedTab):
    table_classes = (tables.ExtConsumedContractsTable,)

    def get_consumed_policy_rule_sets_data(self):
        try:
            ext_policy_targetid = self.tab_group.kwargs['ext_policy_target_id']
            ext_policy_target = client.ext_policy_target_get(
                self.request, ext_policy_targetid)
            consumed_policy_rule_set_ids = ext_policy_target.get(
                'consumed_policy_rule_sets')
            consumed_policy_rule_sets = []
            for _id in consumed_policy_rule_set_ids:
                consumed_policy_rule_sets.append(
                    client.policy_rule_set_get(self.request, _id))
            consumed_policy_rule_sets = [gfilters.update_pruleset_attributes(
                self.request, item) for item in consumed_policy_rule_sets]
            return consumed_policy_rule_sets
        except Exception:
            error_message = _('Unable to get consumed rule sets')
            exceptions.handle(self.request, error_message)
            return []


class ExternalPTGMemberTabs(tabs.TabGroup):
    slug = 'members'
    tabs = (ExtProvidedTab, ExtConsumedTab)
    sticky = True
