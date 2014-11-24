# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import re

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon import tabs
from horizon import workflows

from gbpui import client

import forms as policy_rule_set_forms
import tabs as policy_rule_set_tabs
import workflows as policy_rule_set_workflows

PolicyRuleSetTabs = policy_rule_set_tabs.ApplicationPoliciesTabs
PolicyRuleSetDetailsTabs = policy_rule_set_tabs.PolicyRuleSetDetailsTabs
PolicyRuleDetailsTabs = policy_rule_set_tabs.PolicyRuleDetailsTabs
PolicyClassifierDetailsTabs = policy_rule_set_tabs.PolicyClassifierDetailsTabs
PolicyActionDetailsTabs = policy_rule_set_tabs.PolicyActionDetailsTabs
AddPolicyRuleSet = policy_rule_set_workflows.AddContract
AddPolicyRule = policy_rule_set_workflows.AddPolicyRule
AddPolicyClassifier = policy_rule_set_workflows.AddPolicyClassifier


class IndexView(tabs.TabView):
    tab_group_class = (PolicyRuleSetTabs)
    template_name = 'project/application_policy/details_tabs.html'

    def post(self, request, *args, **kwargs):
        obj_ids = request.POST.getlist('object_ids')
        action = request.POST['action']
        obj_type = re.search('delete([a-z]+)', action).group(1)
        if not obj_ids:
            obj_ids.append(re.search('([0-9a-z-]+)$', action).group(1))
        if obj_type == 'policyaction':
            for obj_id in obj_ids:
                try:
                    client.policyaction_delete(request, obj_id)
                    messages.success(request, _('Deleted action %s') % obj_id)
                except Exception as e:
                    msg = _('Unable to delete action. %s') % (str(e))
                    exceptions.handle(request, msg)
        if obj_type == 'policyclassifier':
            for obj_id in obj_ids:
                try:
                    client.policyclassifier_delete(request, obj_id)
                    messages.success(
                        request, _('Deleted classifer %s') % obj_id)
                except Exception as e:
                    msg = _('Unable to delete action. %s') % (str(e))
                    exceptions.handle(request, msg)
        if obj_type == 'policyrule':
            for obj_id in obj_ids:
                try:
                    client.policyrule_delete(request, obj_id)
                    messages.success(request,
                                     _('Deleted rule %s') % obj_id)
                except Exception as e:
                    msg = _('Unable to delete action. %s') % (str(e))
                    exceptions.handle(request, msg)
        if obj_type == 'policyruleset':
            for obj_id in obj_ids:
                try:
                    client.policy_rule_set_delete(request, obj_id)
                    messages.success(request,
                                     _('Deleted rule %s') % obj_id)
                except Exception as e:
                    msg = _('Unable to delete action. %s') % (str(e))
                    exceptions.handle(request, msg)

        return self.get(request, *args, **kwargs)


class AddPolicyRuleSetView(workflows.WorkflowView):
    workflow_class = AddPolicyRuleSet
    template_name = "project/application_policy/addpolicy_rule_set.html"

    def get_object_id(self, policy_rule_set):
        return [policy_rule_set.id]


class UpdatePolicyRuleSetView(forms.ModalFormView):
    form_class = policy_rule_set_forms.UpdatePolicyRuleSetForm
    template_name = 'project/application_policy/update_policy_rule_set.html'

    def get_context_data(self, **kwargs):
        context = super(
            UpdatePolicyRuleSetView, self).get_context_data(**kwargs)
        context['policy_rule_set_id'] = self.kwargs['policy_rule_set_id']
        return context

    def get_initial(self):
        return {'policy_rule_set_id': self.kwargs['policy_rule_set_id']}


class AddPolicyRuleView(workflows.WorkflowView):
    workflow_class = AddPolicyRule
    template_name = "project/application_policy/addpolicyrule.html"

    def get_object_id(self, rule):
        return [rule.id]


class AddPolicyClassifierView(forms.ModalFormView):
    form_class = policy_rule_set_forms.AddPolicyClassifierForm
    template_name = "project/application_policy/add_policy_classifier.html"

    def get_success_url(self):
        return reverse('horizon:project:application_policy:index')

    def get_object_id(self, classifier):
        return [classifier.id]


class AddPolicyActionView(forms.ModalFormView):
    form_class = policy_rule_set_forms.AddPolicyActionForm
    template_name = "project/application_policy/add_policy_action.html"

    def get_success_url(self):
        return reverse('horizon:project:application_policy:index')

    def get_object_id(self, policyaction):
        return [policyaction.id]


class UpdatePolicyActionView(forms.ModalFormView):
    form_class = policy_rule_set_forms.UpdatePolicyActionForm
    template_name = "project/application_policy/update_policy_action.html"

    def get_context_data(self, **kwargs):
        context = super(
            UpdatePolicyActionView, self).get_context_data(**kwargs)
        context['policyaction_id'] = self.kwargs['policyaction_id']
        return context

    def get_initial(self):
        return {'policyaction_id': self.kwargs['policyaction_id']}


class PolicyRuleSetDetailsView(tabs.TabView):
    tab_group_class = (PolicyRuleSetDetailsTabs)
    template_name = 'project/application_policy/details_tabs.html'


class PolicyRuleDetailsView(tabs.TabView):
    tab_group_class = (PolicyRuleDetailsTabs)
    template_name = 'project/application_policy/details_tabs.html'


class UpdatePolicyRuleView(forms.ModalFormView):
    form_class = policy_rule_set_forms.UpdatePolicyRuleForm
    template_name = "project/application_policy/update_policy_rule.html"

    def get_context_data(self, **kwargs):
        context = super(UpdatePolicyRuleView, self).get_context_data(**kwargs)
        context['policyrule_id'] = self.kwargs['policyrule_id']
        return context

    def get_initial(self):
        return {'policyrule_id': self.kwargs['policyrule_id']}


class PolicyClassifierDetailsView(tabs.TabView):
    tab_group_class = (PolicyClassifierDetailsTabs)
    template_name = 'project/application_policy/details_tabs.html'


class UpdatePolicyClassifierView(forms.ModalFormView):
    form_class = policy_rule_set_forms.UpdatePolicyClassifierForm
    template_name = "project/application_policy/update_policy_classifier.html"

    def get_context_data(self, **kwargs):
        context = super(
            UpdatePolicyClassifierView, self).get_context_data(**kwargs)
        context['policyclassifier_id'] = self.kwargs['policyclassifier_id']
        return context

    def get_initial(self):
        return {'policyclassifier_id': self.kwargs['policyclassifier_id']}


class PolicyActionDetailsView(tabs.TabView):
    tab_group_class = (PolicyActionDetailsTabs)
    template_name = 'project/application_policy/details_tabs.html'
