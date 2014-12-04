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

import json

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs


from gbpui import client
from gbpui import column_filters as gfilters

import tables as ns_tables


class ServiceChainSpecTab(tabs.TableTab):
    name = _("Service Chain Specs")
    table_classes = (ns_tables.ServiceChainSpecTable,)
    slug = "service_chain_specs"
    template_name = "horizon/common/_detail_table.html"

    def get_service_chain_spec_table_data(self):
        specs = []
        try:
            specs = client.servicechainspec_list(self.request)
            specs = [gfilters.update_sc_spec_attributes(
                self.request, item) for item in specs]
        except Exception:
            pass
        return specs


class ServiceChainNodeTab(tabs.TableTab):
    name = _("Service Chain Nodes")
    table_classes = (ns_tables.ServiceChainNodeTable,)
    slug = "service_chain_node"
    template_name = "horizon/common/_detail_table.html"

    def get_service_chain_node_table_data(self):
        nodes = []
        try:
            nodes = client.servicechainnode_list(self.request)
        except Exception:
            pass
        return nodes


class ServiceChainInstanceTab(tabs.TableTab):
    name = _("Service Chain Instances")
    table_classes = (ns_tables.ServiceChainInstanceTable,)
    slug = "service_chain_instance"
    template_name = "horizon/common/_detail_table.html"

    def get_service_chain_instance_table_data(self):
        instances = []
        try:
            instances = client.servicechaininstance_list(self.request)
            instances = [gfilters.update_sc_instance_attributes(
                self.request, item) for item in instances]
        except Exception:
            pass
        return instances


class ServiceChainTabs(tabs.TabGroup):
    slug = "service_chain_spec_tabs"
    tabs = (ServiceChainSpecTab, ServiceChainNodeTab,)
    sticky = True


class ServiceChainNodeDetailsTab(tabs.Tab):
    name = _("Service Chain Node Details")
    slug = "scnode_details"
    template_name = "project/network_services/_scnode_details.html"
    failure_url = reverse_lazy('horizon:project:network_services:index')

    def get_context_data(self, request):
        scnode_id = self.tab_group.kwargs['scnode_id']
        try:
            scnode = client.get_servicechain_node(request, scnode_id)
        except Exception:
            exceptions.handle(request, _(
                'Unable to retrieve service node details.'),
                redirect=self.failure_url)
        return {'scnode': scnode}


class SCNodeDetailsTabGroup(tabs.TabGroup):
    slug = 'scnode_details'
    tabs = (ServiceChainNodeDetailsTab,)


class ServiceChainSpecDetailsTab(tabs.Tab):
    name = _("Service Chain Spec Details")
    slug = "scspec_details"
    template_name = "project/network_services/_scspec_details.html"
    failure_url = reverse_lazy('horizon:project:network_services:index')

    def get_context_data(self, request):
        scspec_id = self.tab_group.kwargs['scspec_id']
        try:
            scspec = client.get_servicechain_spec(request, scspec_id)
            nodes = []
            gn = lambda x, y: client.get_servicechain_node(x, y)
            for node in scspec.nodes:
                n = gn(self.request, node)
                setattr(n, 'config', json.loads(n.config))
                nodes.append(n)
            setattr(scspec, 'nodes', nodes)
        except Exception:
            exceptions.handle(request, _(
                'Unable to retrieve service chain spec details.'),
                redirect=self.failure_url)
        return {'scspec': scspec}


class SCSpecDetailsTabGroup(tabs.TabGroup):
    slug = 'scspec_details'
    tabs = (ServiceChainSpecDetailsTab,)


class ServiceChainInstanceDetailsTab(tabs.Tab):
    name = _("Service Chain Instance Details")
    slug = "scinstance_details"
    template_name = "project/network_services/_scinstance_details.html"
    failure_url = reverse_lazy('horizon:project:network_services:index')

    def get_context_data(self, request):
        scinstance_id = self.tab_group.kwargs['scinstance_id']
        try:
            scinstance = client.get_servicechain_instance(
                request, scinstance_id)
        except Exception:
            exceptions.handle(request, _(
                'Unable to retrieve service instance details.'),
                redirect=self.failure_url)
        return {'scinstance': scinstance}


class SCInstanceDetailsTabGroup(tabs.TabGroup):
    slug = 'scinstance_details'
    tabs = (ServiceChainInstanceDetailsTab,)
