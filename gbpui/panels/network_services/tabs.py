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
import yaml

from django.contrib.staticfiles.templatetags.staticfiles import static
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
            specs = client.servicechainspec_list(self.request,
                tenant_id=self.request.user.tenant_id)
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
            nodes = client.servicechainnode_list(self.request,
                tenant_id=self.request.user.tenant_id)
            nodes = [gfilters.update_sc_node_attributes(
                self.request, item) for item in nodes]
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
            instances = client.servicechaininstance_list(self.request,
                tenant_id=self.request.user.tenant_id)
            instances = [gfilters.update_sc_instance_attributes(
                self.request, item) for item in instances]
        except Exception:
            pass
        return instances


class ServiceProfileTab(tabs.TableTab):
    name = _("Service Profiles")
    table_classes = (ns_tables.ServiceProfileTable,)
    slug = "service_profile"
    template_name = "horizon/common/_detail_table.html"

    def get_service_profile_table_data(self):
        service_profiles = []
        try:
            service_profiles = client.serviceprofile_list(self.request)
        except Exception:
            pass
        return service_profiles


class ServiceChainTabs(tabs.TabGroup):
    slug = "service_chain_spec_tabs"
    tabs = (ServiceChainSpecTab, ServiceChainNodeTab, ServiceProfileTab,
            ServiceChainInstanceTab)
    sticky = True


class ServiceProfileDetailsTab(tabs.Tab):
    name = _("Service Profile Details")
    slug = "serviceprofile_details"
    template_name = "project/network_services/_serviceprofile_details.html"
    failure_url = reverse_lazy('horizon:project:network_services:index')

    def get_context_data(self, request):
        service_profile_id = self.tab_group.kwargs['sp_id']
        try:
            service_profile = client.get_service_profile(
                request, service_profile_id)
        except Exception:
            exceptions.handle(request, _(
                'Unable to retrieve service profile details.'),
                redirect=self.failure_url)
        return {'service_profile': service_profile}


class ServiceProfileDetailsTabGroup(tabs.TabGroup):
    slug = 'scnode_details'
    tabs = (ServiceProfileDetailsTab,)


class ServiceChainNodeDetailsTab(tabs.Tab):
    name = _("Service Chain Node Details")
    slug = "scnode_details"
    template_name = "project/network_services/_scnode_details.html"
    failure_url = reverse_lazy('horizon:project:network_services:index')

    def get_context_data(self, request):
        scnode_id = self.tab_group.kwargs['scnode_id']
        try:
            scnode = client.get_servicechain_node(request, scnode_id)
            config = scnode.config
            config = config.strip()
            if config.startswith('{'):
                config = yaml.load(config)
                if 'heat_template_version' in config:
                    scnode.config = yaml.dump(
                        config, default_flow_style=False, indent=4)
                else:
                    scnode.config = json.dumps(
                        config, sort_keys=False, indent=4)
            else:
                config = yaml.load(config)
                scnode.config = yaml.dump(
                    config, default_flow_style=False, indent=4)
            scnode.tree = self.prepare_config_as_tree(config)
        except Exception:
            exceptions.handle(request, _(
                'Unable to retrieve service node details.'),
                redirect=self.failure_url)
        return {'scnode': scnode}

    def prepare_config_as_tree(self, config):
        tree = []
        for key, value in config.iteritems():
            node = {}
            if isinstance(value, dict):
                node = self.prepare_root_node(value)
                node["text"] = key
            else:
                node["text"] = key + " : " + str(value)
                node["icon"] = static("dashboard/img/text.png")

            tree.append(node)
        return json.dumps(tree)

    def prepare_root_node(self, obj):
        node = {}
        if obj:
            children = self.prepare_children(obj)
            node["children"] = children
            state = {}
            state["opened"] = True
            node["state"] = state
        return node

    def prepare_children(self, obj):
        children = []
        for key, value in obj.iteritems():
            node = {}
            child = self.json2array(value)
            node["text"] = key
            node["children"] = child
            children.append(node)

        return children

    def json2array(self, obj):
        arr = []
        for key, value in obj.iteritems():
            node = {}
            if isinstance(value, dict):
                children = self.json2array(value)
                node["text"] = key
                node["children"] = children
            elif isinstance(value, list):
                items = []
                for item in value:
                    items.append(json.dumps(item))
                node["children"] = items
                node["text"] = key
            else:
                node["text"] = key + " : " + str(value)
                node["icon"] = static("dashboard/img/text.png")
            arr.append(node)
        return arr


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
                config = n.config
                config = config.strip()
                if config.startswith('{'):
                    config = yaml.load(config)
                    if 'heat_template_version' in config:
                        config = yaml.dump(
                            config, default_flow_style=False, indent=4)
                    else:
                        config = json.dumps(config, sort_keys=False, indent=4)
                else:
                    config = yaml.load(config)
                    config = yaml.dump(
                        config, default_flow_style=False, indent=4)
                setattr(n, 'config', config)
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
