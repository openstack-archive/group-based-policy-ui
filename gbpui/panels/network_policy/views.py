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
        if not obj_ids:
            obj_ids.append(re.search('([0-9a-z-]+)$', action).group(1))
        for obj_id in obj_ids:
            try:
                client.epg_delete(request, obj_id)
                messages.success(request,
                                 _('Deleted EPG %s') % obj_id)
            except Exception as e:
                exceptions.handle(request,
                                  _('Unable to delete EPG. %s') % e)
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

    def get_l2policy_table_data(self):
        policies = []
        try:
            tenant_id = self.request.user.tenant_id
            policies = client.l2policy_list(self.request, tenant_id=tenant_id)
        except Exception:
            policies = []
            exceptions.handle(self.tab_group.request,
                              _('Unable to retrieve l2 policy list.'))
        return policies

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


class UpdateServicePolicyView(forms.ModalFormView):
    form_class = np_forms.UpdateServicePolicyForm
    template_name = "project/network_policy/update_service_policy.html"

    def get_context_data(self, **kwargs):
        context = super(
            CreateServicePolicyView, self).get_context_data(**kwargs)
        context['service_policy_id'] = self.kwargs['service_policy_id']
        return context

    def get_initial(self):
        return self.kwargs
