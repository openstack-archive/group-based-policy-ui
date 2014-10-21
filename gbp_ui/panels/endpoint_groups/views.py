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
#
# @author: Ronak Shah

import re

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon import tabs
from horizon.utils import memoized
from horizon import workflows

from gbp_ui import client

import forms as epg_forms
import tabs as epg_tabs
import workflows as epg_workflows

EPGTabs = epg_tabs.EPGTabs
EPGDetailsTabs = epg_tabs.EPGDetailsTabs

AddEPG = epg_workflows.AddEPG
LaunchVM = epg_workflows.CreateVM
CreateContractForm = epg_forms.CreateContractForm


class IndexView(tabs.TabView):
    tab_group_class = (EPGTabs)
    template_name = 'project/endpoint_groups/details_tabs.html'

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


class AddEPGView(workflows.WorkflowView):
    workflow_class = AddEPG
    template_name = "project/endpoint_groups/addepg.html"


class EPGDetailsView(tabs.TabbedTableView):
	tab_group_class = (epg_tabs.EPGMemberTabs)
	template_name = 'project/endpoint_groups/details_tabs.html'


class LaunchVMView(workflows.WorkflowView):
    workflow_class = LaunchVM
    template_name = "project/endpoint_groups/add_vm.html"
    
    def get_initial(self):
        return self.kwargs


class UpdateEPGView(forms.ModalFormView):
    form_class = epg_forms.UpdateEPGForm
    template_name = "project/endpoint_groups/updateepg.html"
    context_object_name = 'epg'
    success_url = reverse_lazy("horizon:project:endpoint_groups:index")

    def get_context_data(self, **kwargs):
        context = super(UpdateEPGView, self).get_context_data(**kwargs)
        context["epg_id"] = self.kwargs['epg_id']
        obj = self._get_object()
        if obj:
            context['name'] = obj.name
        return context

    @memoized.memoized_method
    def _get_object(self, *args, **kwargs):
        epg_id = self.kwargs['epg_id']
        try:
            epg = client.epg_get(self.request, epg_id)
            epg.set_id_as_name_if_empty()
            return epg
        except Exception:
            redirect = self.success_url
            msg = _('Unable to retrieve epg details.')
            exceptions.handle(self.request, msg, redirect=redirect)

    def get_initial(self):
        epg = self._get_object()
        initial = epg.get_dict()
        return initial

class CreateContractView(forms.ModalFormView):
    form_class = CreateContractForm
    template_name = "project/endpoint_groups/add_contract.html"

    def get_context_data(self, **kwargs):
        context = super(CreateContractView, self).get_context_data(**kwargs)
        context["epg_id"] = self.kwargs['epg_id']
        return context
    
    def get_initial(self):
        return self.kwargs

class RemoveContractView(forms.ModalFormView):
    form_class = epg_forms.RemoveContractForm
    template_name = "project/endpoint_groups/remove_contract.html"

    def get_context_data(self, **kwargs):
        context = super(RemoveContractView, self).get_context_data(**kwargs)
        context["epg_id"] = self.kwargs['epg_id']
        return context
    
    def get_initial(self):
        return self.kwargs 

class AddConsumedView(forms.ModalFormView):
    form_class = epg_forms.AddConsumedForm
    template_name = "project/endpoint_groups/add_consumed.html"

    def get_context_data(self, **kwargs):
        context = super(AddConsumedView, self).get_context_data(**kwargs)
        context["epg_id"] = self.kwargs['epg_id']
        return context
    
    def get_initial(self):
        return self.kwargs
 
class RemoveConsumedView(forms.ModalFormView):
    form_class = epg_forms.RemoveConsumedForm
    template_name = "project/endpoint_groups/remove_consumed.html"

    def get_context_data(self, **kwargs):
        context = super(RemoveConsumedView, self).get_context_data(**kwargs)
        context["epg_id"] = self.kwargs['epg_id']
        return context
    
    def get_initial(self):
        return self.kwargs 
