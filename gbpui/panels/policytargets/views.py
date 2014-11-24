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

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon import tabs
from horizon.utils import memoized
from horizon import workflows

from gbpui import client

import forms as policy_target_forms
import tabs as policy_target_tabs
import workflows as policy_target_workflows

PTGTabs = policy_target_tabs.PTGTabs
PTGDetailsTabs = policy_target_tabs.PTGDetailsTabs

AddPTG = policy_target_workflows.AddPTG
LaunchVM = policy_target_workflows.CreateVM


class IndexView(tabs.TabView):
    tab_group_class = (PTGTabs)
    template_name = 'project/policytargets/details_tabs.html'

    def post(self, request, *args, **kwargs):
        obj_ids = request.POST.getlist('object_ids')
        action = request.POST['action']
        if not obj_ids:
            obj_ids.append(re.search('([0-9a-z-]+)$', action).group(1))
        for obj_id in obj_ids:
            try:
                client.policy_target_delete(request, obj_id)
                messages.success(request,
                                 _('Deleted Group %s') % obj_id)
            except Exception as e:
                exceptions.handle(request,
                                  _('Unable to delete Group. %s') % e)
        return self.get(request, *args, **kwargs)


class AddPTGView(workflows.WorkflowView):
    workflow_class = AddPTG
    template_name = "project/policytargets/addpolicy_target.html"


class PTGDetailsView(tabs.TabbedTableView):
    tab_group_class = (policy_target_tabs.PTGMemberTabs)
    template_name = 'project/policytargets/group_details.html'

    def get_context_data(self, **kwargs):
        context = super(PTGDetailsView, self).get_context_data(**kwargs)
        try:
            policy_target = client.policy_target_get(
                self.request, context['policy_target_id'])
            context['policy_target'] = policy_target
        except Exception:
            pass
        return context


class LaunchVMView(workflows.WorkflowView):
    workflow_class = LaunchVM
    template_name = "project/policytargets/add_vm.html"

    def get_initial(self):
        return self.kwargs


class UpdatePTGView(forms.ModalFormView):
    form_class = policy_target_forms.UpdatePolicyTargetForm
    template_name = "project/policytargets/update_policy_target.html"
    context_object_name = 'policy_target'
    success_url = reverse_lazy("horizon:project:policytargets:index")

    def get_context_data(self, **kwargs):
        context = super(UpdatePTGView, self).get_context_data(**kwargs)
        context["policy_target_id"] = self.kwargs['policy_target_id']
        obj = self._get_object()
        if obj:
            context['name'] = obj.name
        return context

    @memoized.memoized_method
    def _get_object(self, *args, **kwargs):
        policy_target_id = self.kwargs['policy_target_id']
        try:
            policy_target = client.policy_target_get(
                self.request, policy_target_id)
            policy_target.set_id_as_name_if_empty()
            return policy_target
        except Exception:
            redirect = self.success_url
            msg = _('Unable to retrieve policy_target details.')
            exceptions.handle(self.request, msg, redirect=redirect)

    def get_initial(self):
        return self.kwargs


class AddProvidedPRSView(forms.ModalFormView):
    form_class = policy_target_forms.AddProvidedPRSForm
    template_name = "project/policytargets/add_provided_prs.html"

    def get_context_data(self, **kwargs):
        context = super(AddProvidedPRSView, self).get_context_data(**kwargs)
        context["policy_target_id"] = self.kwargs['policy_target_id']
        return context

    def get_initial(self):
        return self.kwargs


class RemoveProvidedPRSView(forms.ModalFormView):
    form_class = policy_target_forms.RemoveProvidedPRSForm
    template_name = "project/policytargets/remove_provided_prs.html"

    def get_context_data(self, **kwargs):
        context = super(RemoveProvidedPRSView, self).get_context_data(**kwargs)
        context["policy_target_id"] = self.kwargs['policy_target_id']
        return context

    def get_initial(self):
        return self.kwargs


class AddConsumedPRSView(forms.ModalFormView):
    form_class = policy_target_forms.AddConsumedPRSForm
    template_name = "project/policytargets/add_consumed_prs.html"

    def get_context_data(self, **kwargs):
        context = super(AddConsumedPRSView, self).get_context_data(**kwargs)
        context["policy_target_id"] = self.kwargs['policy_target_id']
        return context

    def get_initial(self):
        return self.kwargs


class RemoveConsumedPRSView(forms.ModalFormView):
    form_class = policy_target_forms.RemoveConsumedPRSForm
    template_name = "project/policytargets/remove_consumed_prs.html"

    def get_context_data(self, **kwargs):
        context = super(RemoveConsumedPRSView, self).get_context_data(**kwargs)
        context["policy_target_id"] = self.kwargs['policy_target_id']
        return context

    def get_initial(self):
        return self.kwargs
