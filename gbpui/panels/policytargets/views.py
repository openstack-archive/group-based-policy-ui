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
from django.http import HttpResponse  # noqa
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs
from horizon.utils import memoized
from horizon import workflows

from gbpui import client
from gbpui.common import forms as gbforms


import forms as policy_target_forms
import tabs as policy_target_tabs
import workflows as policy_target_workflows

from openstack_dashboard import api

from netaddr import IPAddress
from netaddr import IPNetwork

PTGTabs = policy_target_tabs.PTGTabs
PTGDetailsTabs = policy_target_tabs.PTGDetailsTabs

AddPTG = policy_target_workflows.AddPTG
AddExternalPTG = policy_target_workflows.AddExternalPTG


class IndexView(tabs.TabbedTableView):
    tab_group_class = (PTGTabs)
    template_name = 'gbpui/details_tabs.html'
    page_title = _("Groups")


class AddPTGView(workflows.WorkflowView):
    workflow_class = AddPTG


class AddExternalPTGView(workflows.WorkflowView):
    workflow_class = AddExternalPTG


class PTGDetailsView(tabs.TabbedTableView):
    tab_group_class = (policy_target_tabs.PTGMemberTabs)
    template_name = 'gbpui/details_tabs.html'
    page_title = _("Group: {{ policy_target.name }}")

    def get_context_data(self, **kwargs):
        context = super(PTGDetailsView, self).get_context_data(**kwargs)
        try:
            policy_target = client.policy_target_get(
                self.request, context['policy_target_id'])
            context['policy_target'] = policy_target
        except Exception:
            pass
        return context


class ExternalPTGDetailsView(tabs.TabbedTableView):
    tab_group_class = (policy_target_tabs.ExternalPTGMemberTabs)
    template_name = 'gbpui/details_tabs.html'
    page_title = _("Group: {{ policy_target.name }}")

    def get_context_data(self, **kwargs):
        context = super(ExternalPTGDetailsView, self).get_context_data(
            **kwargs)
        try:
            ext_policy_target = client.ext_policy_target_get(
                self.request, context['ext_policy_target_id'])
            context['policy_target'] = ext_policy_target
        except Exception:
            pass
        return context


'''
class LaunchVMView(workflows.WorkflowView):
    workflow_class = policy_target_workflows.LaunchInstance

    def get_initial(self):
        initial = super( LaunchVMView, self).get_initial()
        initial['project_id'] = self.request.user.tenant_id
        initial['user_id'] = self.request.user.id
        return initial
'''


class UpdatePTGView(gbforms.HelpTextModalMixin,
                    gbforms.ReversingModalFormView):
    form_class = policy_target_forms.UpdatePolicyTargetForm
    form_id = "update_policy_target_form"
    modal_header = _("Edit Group")
    template_name = "gbpui/form_with_description.html"
    context_object_name = 'policy_target'
    submit_label = _("Save Changes")
    submit_url = "horizon:project:policytargets:updatepolicy_target"
    success_url = reverse_lazy("horizon:project:policytargets:index")
    page_title = _("Edit Group")
    help_text = _("You may update group details here.")

    def get_submit_url_params(self, **kwargs):
        return {
            "policy_target_id": self.kwargs["policy_target_id"]
        }

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


class UpdateExternalPTGView(gbforms.HelpTextModalMixin,
                            gbforms.ReversingModalFormView):
    form_class = policy_target_forms.UpdateExternalPolicyTargetForm
    form_id = "update_policy_target_form"
    modal_header = _("Edit Group")
    template_name = "gbpui/form_with_description.html"
    context_object_name = 'external_policy_target'
    submit_label = _("Save Changes")
    submit_url = "horizon:project:policytargets:update_ext_policy_target"
    success_url = reverse_lazy("horizon:project:policytargets:index")
    page_title = _("Edit Group")
    help_text = _("You may update external policy details here.")

    def get_submit_url_params(self, **kwargs):
        return {
            "ext_policy_target_id": self.kwargs["ext_policy_target_id"]
        }

    @memoized.memoized_method
    def _get_object(self, *args, **kwargs):
        ext_policy_target_id = self.kwargs['ext_policy_target_id']
        try:
            ext_policy_target = client.ext_policy_target_get(
                self.request, ext_policy_target_id)
            ext_policy_target.set_id_as_name_if_empty()
            return ext_policy_target
        except Exception:
            redirect = self.success_url
            msg = _('Unable to retrieve policy_target details.')
            exceptions.handle(self.request, msg, redirect=redirect)

    def get_initial(self):
        return self.kwargs


class ExtAddProvidedPRSView(gbforms.HelpTextModalMixin,
                            gbforms.ReversingModalFormView):
    form_class = policy_target_forms.ExtAddProvidedPRSForm
    form_id = "ext_add_provided_form"
    modal_header = _("Add Provided PRS")
    template_name = "gbpui/form_with_description.html"
    submit_label = _("Save Changes")
    submit_url = "horizon:project:policytargets:ext_add_provided_prs"
    page_title = _("Add Provided PRS")
    help_text = _(
        "Add provided policy rule set. Press Ctrl to select multiple items."
    )

    def get_submit_url_params(self, **kwargs):
        return {
            'ext_policy_target_id': self.kwargs['ext_policy_target_id']
        }

    def get_initial(self):
        return self.kwargs


class ExtRemoveProvidedPRSView(gbforms.HelpTextModalMixin,
                               gbforms.ReversingModalFormView):
    form_class = policy_target_forms.ExtRemoveProvidedPRSForm
    form_id = "ext_remove_provided_form"
    modal_header = _("Remove Provided PRS")
    template_name = "gbpui/form_with_description.html"
    submit_label = _("Save Changes")
    submit_url = "horizon:project:policytargets:ext_remove_provided_prs"
    page_title = _("Remove Provided PRS")
    help_text = _(
        "Remove provided policy rule set. Press Ctrl to select multiple items."
    )

    def get_submit_url_params(self, **kwargs):
        return {
            "ext_policy_target_id": self.kwargs['ext_policy_target_id']
        }

    def get_initial(self):
        return self.kwargs


class AddProvidedPRSView(gbforms.HelpTextModalMixin,
                         gbforms.ReversingModalFormView):
    form_class = policy_target_forms.AddProvidedPRSForm
    form_id = "add_provided_form"
    modal_header = _("Add Provided PRS")
    template_name = "gbpui/form_with_description.html"
    submit_label = _("Save Changes")
    submit_url = "horizon:project:policytargets:add_provided_prs"
    page_title = _("Add Provided PRS")
    help_text = _(
        "Add provided policy rule set. Press Ctrl to select multiple items."
    )

    def get_submit_url_params(self, **kwargs):
        return {
            "policy_target_id": self.kwargs['policy_target_id']
        }

    def get_initial(self):
        return self.kwargs


class RemoveProvidedPRSView(gbforms.HelpTextModalMixin,
                            gbforms.ReversingModalFormView):
    form_class = policy_target_forms.RemoveProvidedPRSForm
    form_id = "remove_provided_form"
    modal_header = _("Remove Provided PRS")
    template_name = "gbpui/form_with_description.html"
    submit_label = _("Save Changes")
    submit_url = "horizon:project:policytargets:remove_provided_prs"
    page_title = _("Remove Provided PRS")
    help_text = _(
        "Remove provided policy rule set. Press Ctrl to select multiple items."
    )

    def get_submit_url_params(self, **kwargs):
        return {
            "policy_target_id": self.kwargs['policy_target_id']
        }

    def get_initial(self):
        return self.kwargs


class ExtAddConsumedPRSView(gbforms.HelpTextModalMixin,
                            gbforms.ReversingModalFormView):
    form_class = policy_target_forms.ExtAddConsumedPRSForm
    form_id = "ext_add_consumed_form"
    modal_header = _("Add Policy Rule Set")
    template_name = "gbpui/form_with_description.html"
    submit_label = _("Save Changes")
    submit_url = "horizon:project:policytargets:ext_add_consumed_prs"
    page_title = _("Add Policy Rule Set")
    help_text = _(
        "Add consumed policy rule set. Press Ctrl to select multiple items."
    )

    def get_submit_url_params(self, **kwargs):
        return {
            "ext_policy_target_id": self.kwargs['ext_policy_target_id']
        }

    def get_initial(self):
        return self.kwargs


class ExtRemoveConsumedPRSView(gbforms.HelpTextModalMixin,
                               gbforms.ReversingModalFormView):
    form_class = policy_target_forms.ExtRemoveConsumedPRSForm
    form_id = "remove_contract_form"
    modal_header = _("Remove Policy Rule Set")
    template_name = "gbpui/form_with_description.html"
    submit_label = _("Save Changes")
    submit_url = "horizon:project:policytargets:ext_remove_consumed_prs"
    page_title = _("Remove Policy Rule Set")
    help_text = _(
        "Remove consumed policy rule set. Press Ctrl to select multiple items."
    )

    def get_submit_url_params(self, **kwargs):
        return {
            "ext_policy_target_id": self.kwargs['ext_policy_target_id']
        }

    def get_initial(self):
        return self.kwargs


class AddConsumedPRSView(gbforms.HelpTextModalMixin,
                         gbforms.ReversingModalFormView):
    form_class = policy_target_forms.AddConsumedPRSForm
    form_id = "add_consumed_form"
    modal_header = _("Add ")
    template_name = "gbpui/form_with_description.html"
    submit_label = _("Save Changes")
    submit_url = "horizon:project:policytargets:add_consumed_prs"
    page_title = _("Add ")
    help_text = _(
        "Add consumed policy rule set. Press Ctrl to select multiple items."
    )

    def get_submit_url_params(self, **kwargs):
        return {
            "policy_target_id": self.kwargs['policy_target_id']
        }

    def get_initial(self):
        return self.kwargs


class RemoveConsumedPRSView(gbforms.HelpTextModalMixin,
                            gbforms.ReversingModalFormView):
    form_class = policy_target_forms.RemoveConsumedPRSForm
    form_id = "remove_contract_form"
    modal_header = _("Remove Policy Rule Set")
    template_name = "gbpui/form_with_description.html"
    submit_label = _("Save Changes")
    submit_url = "horizon:project:policytargets:remove_consumed_prs"
    page_title = _("Remove Policy Rule Set")
    help_text = _(
        "Remove consumed policy rule set. Press Ctrl to select multiple items."
    )

    def get_submit_url_params(self, **kwargs):
        return {
            "policy_target_id": self.kwargs['policy_target_id']
        }

    def get_initial(self):
        return self.kwargs


def check_ip_availability(request):
    fixed_ip = request.GET.get('fixed_ip')
    response = {'error': 'IP address is not within the allocated pool range'}
    subnets = request.GET.get('subnets')
    subnets = subnets.split(":")
    for subnet in subnets:
        subnet_details = subnet.split(",")
        try:
            if IPAddress(fixed_ip) in IPNetwork(subnet_details[0]):
                if IPAddress(fixed_ip) >= IPAddress(subnet_details[1]) and \
                        IPAddress(fixed_ip) <= IPAddress(subnet_details[2]):
                    fixed_ips = "ip_address=" + fixed_ip
                    ports = api.neutron.port_list(request,
                        tenant_id=request.user.tenant_id, fixed_ips=fixed_ips)
                    if ports:
                        response = {"inuse": False,
                                    "error": "IP address already in use"}
                    else:
                        response = {"inuse": True}
                    break
        except Exception:
            response = {'error': 'Unable to check IP availability'}
    json_string = json.dumps(response, ensure_ascii=False)
    return HttpResponse(json_string, content_type='text/json')
