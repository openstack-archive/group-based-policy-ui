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

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon import tables
from horizon import tabs

from gbpui import client

import forms as np_forms
import tables as np_tables
import tabs as np_tabs


class IndexView(tabs.TabView):
    tab_group_class = (np_tabs.L3PolicyTabs)
    template_name = 'project/network_policy/details_tabs.html'

    def post(self, request, *args, **kwargs):
        obj_ids = request.POST.getlist('object_ids')
        action = request.POST['action']
        obj_type = re.search('delete([0-9a-z]+)', action).group(1)
        if not obj_ids:
            obj_ids.append(re.search('([0-9a-z-]+)$', action).group(1))
        if obj_type == 'spolicy':
            for obj_id in obj_ids:
                try:
                    client.delete_networkservice_policy(request, obj_id)
                    messages.success(request,
                            _('Deleted service policy %s') % obj_id)
                except Exception as e:
                    msg = _('Unable to delete action. %s') % (str(e))
                    exceptions.handle(request, msg)
        if obj_type == 'l3policy':
            for obj_id in obj_ids:
                try:
                    client.l3policy_delete(request, obj_id)
                    messages.success(request,
                            _('Deleted L3 policy %s') % obj_id)
                except Exception as e:
                    msg = _('Unable to delete action. %s') % (str(e))
                    exceptions.handle(request, msg)
        if obj_type == 'externalconnectivity':
            for obj_id in obj_ids:
                try:
                    client.delete_externalconnectivity(request, obj_id)
                    messages.success(request,
                            _('Deleted External Connectivity %s') % obj_id)
                except Exception as e:
                    msg = _('Unable to delete action. %s') % (str(e))
                    exceptions.handle(request, msg)
        if obj_type == 'natpool':
            for obj_id in obj_ids:
                try:
                    client.delete_natpool(request, obj_id)
                    messages.success(request,
                            _('Deleted NAT Pool %s') % obj_id)
                except Exception as e:
                    msg = _('Unable to delete action. %s') % (str(e))
                    exceptions.handle(request, msg)
        return self.get(request, *args, **kwargs)


class AddL3policyView(forms.ModalFormView):
    form_class = np_forms.AddL3PolicyForm
    template_name = "project/network_policy/add_l3policy.html"

    def get_context_data(self, **kwargs):
        context = super(AddL3policyView, self).get_context_data(**kwargs)
        return context

    def get_initial(self):
        return self.kwargs


class L3PolicyUpdateView(forms.ModalFormView):
    form_class = np_forms.UpdateL3PolicyForm
    template_name = "project/network_policy/update_l3policy.html"

    def get_context_data(self, **kwargs):
        context = super(L3PolicyUpdateView, self).get_context_data(**kwargs)
        context['l3policy_id'] = self.kwargs['l3policy_id']
        return context

    def get_initial(self):
        return self.kwargs


class L3PolicyDetailsView(tables.MultiTableView):
    table_classes = (np_tables.L2PolicyTable,)
    template_name = 'project/network_policy/l3policy_details.html'

    def post(self, request, *args, **kwargs):
        obj_ids = request.POST.getlist('object_ids')
        action = request.POST['action']
        obj_type = re.search('delete([0-9a-z]+)', action).group(1)
        if not obj_ids:
            obj_ids.append(re.search('([0-9a-z-]+)$', action).group(1))
        if obj_type == 'l2policy':
            for obj_id in obj_ids:
                try:
                    client.l2policy_delete(request, obj_id)
                    messages.success(request,
                            _('Deleted L2 policy %s') % obj_id)
                except Exception as e:
                    msg = _('Unable to delete action. %s') % (str(e))
                    exceptions.handle(request, msg)
        return self.get(request, *args, **kwargs)

    def get_l2policy_table_data(self):
        l2_policies = []
        try:
            condition = {'l3_policy_id': self.kwargs['l3policy_id']}
            l2_policies = client.l2policy_list(self.request,
                    tenant_id=self.request.user.tenant_id, **condition)
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve l2 policy list.'))
        return l2_policies

    def get_context_data(self, **kwargs):
        context = super(L3PolicyDetailsView, self).get_context_data(**kwargs)
        p = client.l3policy_get(self.request, self.kwargs['l3policy_id'])
        context['l3policy'] = p
        return context


class AddL2policyView(forms.ModalFormView):
    form_class = np_forms.AddL2PolicyForm
    template_name = "project/network_policy/add_l2policy.html"

    def get_context_data(self, **kwargs):
        context = super(AddL2policyView, self).get_context_data(**kwargs)
        return context

    def get_initial(self):
        return self.kwargs


class L2PolicyUpdateView(forms.ModalFormView):
    form_class = np_forms.UpdateL2PolicyForm
    template_name = "project/network_policy/update_l2policy.html"

    def get_context_data(self, **kwargs):
        context = super(L2PolicyUpdateView, self).get_context_data(**kwargs)
        context['l2policy_id'] = self.kwargs['l2policy_id']
        return context

    def get_initial(self):
        return self.kwargs


class L2PolicyDetailsView(tabs.TabView):
    tab_group_class = (np_tabs.L2PolicyDetailsTabs)
    template_name = 'project/network_policy/details_tabs.html'


class CreateServicePolicyView(forms.ModalFormView):
    form_class = np_forms.CreateServicePolicyForm
    template_name = "project/network_policy/create_service_policy.html"

    def get_context_data(self, **kwargs):
        context = super(
            CreateServicePolicyView, self).get_context_data(**kwargs)
        return context


class AddExternalSegmentParamView(forms.ModalFormView):
    form_class = np_forms.CreateExternalSegmentParamForm
    template_name = "project/network_policy/create_external_segment_param.html"

    def get_object_id(self, params):
        return params.name


class AddNetworkServiceParamView(forms.ModalFormView):
    form_class = np_forms.CreateNetworkServiceParamForm
    template_name = "project/network_policy/create_network_service_param.html"

    def get_object_id(self, params):
        return params.name


class AddExternalRouteParamView(forms.ModalFormView):
    form_class = np_forms.CreateExternalRouteParamForm
    template_name = "project/network_policy/create_external_route_param.html"

    def get_object_id(self, params):
        return params.name


class UpdateNATPoolView(forms.ModalFormView):
    form_class = np_forms.UpdateNATPoolForm
    template_name = "project/network_policy/update_nat_pool.html"

    def get_context_data(self, **kwargs):
        context = super(
            UpdateNATPoolView, self).get_context_data(**kwargs)
        context['nat_pool_id'] = self.kwargs['nat_pool_id']
        return context

    def get_initial(self):
        return self.kwargs


class UpdateExternalConnectivityView(forms.ModalFormView):
    form_class = np_forms.UpdateExternalConnectivityForm
    template_name = "project/network_policy/update_external_connectivity.html"

    def get_context_data(self, **kwargs):
        context = super(
            UpdateExternalConnectivityView, self).get_context_data(**kwargs)
        context['external_connectivity_id'] = \
            self.kwargs['external_connectivity_id']
        return context

    def get_initial(self):
        return self.kwargs


class UpdateServicePolicyView(forms.ModalFormView):
    form_class = np_forms.UpdateServicePolicyForm
    template_name = "project/network_policy/update_service_policy.html"

    def get_context_data(self, **kwargs):
        context = super(
            UpdateServicePolicyView, self).get_context_data(**kwargs)
        context['service_policy_id'] = self.kwargs['service_policy_id']
        return context

    def get_initial(self):
        return self.kwargs


class ServicePolicyDetailsView(tabs.TabView):
    tab_group_class = (np_tabs.ServicePolicyDetailsTabs)
    template_name = 'project/network_policy/details_tabs.html'


class CreateExternalConnectivityView(forms.ModalFormView):
    form_class = np_forms.CreateExternalConnectivityForm
    template_name = "project/network_policy/create_external_connectivity.html"

    def get_context_data(self, **kwargs):
        context = super(
            CreateExternalConnectivityView, self).get_context_data(**kwargs)
        return context

    def get_success_url(self):
        return reverse('horizon:project:network_policy:index')

    def get_object_id(self, external_segment):
        return [external_segment.id]


class ExternalConnectivityDetailsView(tabs.TabView):
    tab_group_class = (np_tabs.ExternalConnectivityDetailsTabs)
    template_name = 'project/network_policy/details_tabs.html'


class CreateNATPoolView(forms.ModalFormView):
    form_class = np_forms.CreateNATPoolForm
    template_name = "project/network_policy/create_nat_pool.html"

    def get_context_data(self, **kwargs):
        context = super(
            CreateNATPoolView, self).get_context_data(**kwargs)
        return context


class NATPoolDetailsView(tabs.TabView):
    tab_group_class = (np_tabs.NATPoolDetailsTabs)
    template_name = 'project/network_policy/details_tabs.html'
