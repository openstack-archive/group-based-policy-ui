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
from horizon import tabs

import forms as ns_forms
import tabs as ns_tabs

from gbpui import client


class IndexView(tabs.TabView):
    tab_group_class = (ns_tabs.ServiceChainTabs)
    template_name = 'project/network_services/details_tabs.html'

    def post(self, request, *args, **kwargs):
        obj_ids = request.POST.getlist('object_ids')
        action = request.POST['action']
        obj_type = re.search('delete([a-z]+)', action).group(1)
        if not obj_ids:
            obj_ids.append(re.search('([0-9a-z-]+)$', action).group(1))
        if obj_type == 'scnode':
            for obj_id in obj_ids:
                try:
                    client.delete_servicechain_node(request, obj_id)
                    messages.success(request, _('Deleted %s') % obj_id)
                except Exception as e:
                    exceptions.handle(request,
                                      _('Unable to delete . %s') % e)
        if obj_type == 'scinstance':
            for obj_id in obj_ids:
                try:
                    client.delete_servicechain_instance(request, obj_id)
                    messages.success(
                        request, _('Deleted  %s') % obj_id)
                except Exception as e:
                    exceptions.handle(request,
                                      _('Unable to delete . %s') % e)
        if obj_type == 'scspec':
            for obj_id in obj_ids:
                try:
                    client.delete_servicechain_spec(request, obj_id)
                    messages.success(request,
                                     _('Deleted %s') % obj_id)
                except Exception as e:
                    exceptions.handle(request,
                                      _('Unable to delete . %s') % e)
        if obj_type == 'serviceprofile':
            for obj_id in obj_ids:
                try:
                    client.delete_service_profile(request, obj_id)
                    messages.success(request,
                                     _('Deleted %s') % obj_id)
                except Exception as e:
                    exceptions.handle(request,
                                      _('Unable to delete . %s') % e)
        return self.get(request, *args, **kwargs)


class ServiceProfileDetailsView(tabs.TabView):
    tab_group_class = (ns_tabs.ServiceProfileDetailsTabGroup)
    template_name = 'project/network_services/details_tabs.html'


class CreateServiceProfileView(forms.ModalFormView):
    form_class = ns_forms.CreateServiceProfileForm
    template_name = "project/network_services/create_service_profile.html"

    def get_context_data(self, **kwargs):
        context = super(
            CreateServiceProfileView, self).get_context_data(**kwargs)
        return context


class CreateServiceChainNodeView(forms.ModalFormView):
    form_class = ns_forms.CreateServiceChainNodeForm
    template_name = "project/network_services/create_service_chain_node.html"

    def get_context_data(self, **kwargs):
        context = super(
            CreateServiceChainNodeView, self).get_context_data(**kwargs)
        return context


class UpdateServiceChainNodeView(forms.ModalFormView):
    form_class = ns_forms.UpdateServiceChainNodeForm
    template_name = "project/network_services/update_service_chain_node.html"

    def get_context_data(self, **kwargs):
        context = super(
            UpdateServiceChainNodeView, self).get_context_data(**kwargs)
        context['scnode_id'] = self.kwargs['scnode_id']
        return context

    def get_initial(self):
        return self.kwargs


class ServiceChainNodeDetailsView(tabs.TabView):
    tab_group_class = (ns_tabs.SCNodeDetailsTabGroup)
    template_name = 'project/network_services/details_tabs.html'


class CreateServiceChainSpecView(forms.ModalFormView):
    form_class = ns_forms.CreateServiceChainSpecForm
    template_name = "project/network_services/create_service_chain_spec.html"

    def get_context_data(self, **kwargs):
        context = super(
            CreateServiceChainSpecView, self).get_context_data(**kwargs)
        return context


class UpdateServiceChainSpecView(forms.ModalFormView):
    form_class = ns_forms.UpdateServiceChainSpecForm
    template_name = "project/network_services/update_service_chain_spec.html"

    def get_context_data(self, **kwargs):
        context = super(
            UpdateServiceChainSpecView, self).get_context_data(**kwargs)
        context['scspec_id'] = self.kwargs['scspec_id']
        return context

    def get_initial(self):
        return self.kwargs


class ServiceChainSpecDetailsView(tabs.TabView):
    tab_group_class = (ns_tabs.SCSpecDetailsTabGroup)
    template_name = 'project/network_services/details_tabs.html'


class CreateServiceChainInstanceView(forms.ModalFormView):
    form_class = ns_forms.CreateServiceChainInstanceForm
    template_name = "project/network_services/"\
        "create_service_chain_instance.html"

    def get_context_data(self, **kwargs):
        context = super(
            CreateServiceChainInstanceView, self).get_context_data(**kwargs)
        return context


class UpdateServiceChainInstanceView(forms.ModalFormView):
    form_class = ns_forms.UpdateServiceChainInstanceForm
    template_name = "project/network_services/"\
            "update_service_chain_instance.html"

    def get_context_data(self, **kwargs):
        context = super(
            UpdateServiceChainInstanceView, self).get_context_data(**kwargs)
        context['scinstance_id'] = self.kwargs['scinstance_id']
        return context

    def get_initial(self):
        return self.kwargs


class ServiceChainInstanceDetailsView(tabs.TabView):
    tab_group_class = (ns_tabs.SCInstanceDetailsTabGroup)
    template_name = 'project/network_services/details_tabs.html'
