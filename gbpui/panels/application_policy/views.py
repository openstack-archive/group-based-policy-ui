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
from django.core.urlresolvers import reverse

from horizon import tabs
from horizon import workflows

import forms as policy_rule_set_forms
import tabs as policy_rule_set_tabs
import workflows as policy_rule_set_workflows

from django.utils.translation import ugettext_lazy as _
from gbpui.common import forms as gbforms

PolicyRuleSetTabs = policy_rule_set_tabs.ApplicationPoliciesTabs
PolicyRuleSetDetailsTabs = policy_rule_set_tabs.PolicyRuleSetDetailsTabs
PolicyRuleDetailsTabs = policy_rule_set_tabs.PolicyRuleDetailsTabs
PolicyClassifierDetailsTabs = policy_rule_set_tabs.PolicyClassifierDetailsTabs
PolicyActionDetailsTabs = policy_rule_set_tabs.PolicyActionDetailsTabs
AddPolicyRuleSet = policy_rule_set_workflows.AddContract
AddPolicyRule = policy_rule_set_workflows.AddPolicyRule
AddPolicyClassifier = policy_rule_set_workflows.AddPolicyClassifier


class IndexView(tabs.TabbedTableView):
    tab_group_class = (PolicyRuleSetTabs)
    template_name = "gbpui/details_tabs.html"
    page_title = _("Application Policies")


class AddPolicyRuleSetView(workflows.WorkflowView):
    workflow_class = AddPolicyRuleSet


class UpdatePolicyRuleSetView(gbforms.HelpTextModalMixin,
                              gbforms.ReversingModalFormView):
    form_class = policy_rule_set_forms.UpdatePolicyRuleSetForm
    modal_header = _("Edit Policy Rule Set")
    submit_label = _("Update Policy Rule Set")
    submit_url = "horizon:project:application_policy:updatepolicy_rule_set"
    template_name = "gbpui/form_with_description.html"
    page_title = _("Update Rule Set")
    help_text = _("Update Rule Set.")

    def get_submit_url_params(self, **kwargs):
        return {"policy_rule_set_id": self.kwargs['policy_rule_set_id']}

    def get_initial(self):
        return {'policy_rule_set_id': self.kwargs['policy_rule_set_id']}


class AddPolicyRuleView(workflows.WorkflowView):
    workflow_class = AddPolicyRule


class AddPolicyClassifierView(gbforms.HelpTextModalMixin,
                              gbforms.ReversingModalFormView):
    form_class = policy_rule_set_forms.AddPolicyClassifierForm
    template_name = "gbpui/form_with_description.html"
    submit_url = "horizon:project:application_policy:addpolicyclassifier"
    modal_header = _("Create Policy Classifier")
    page_title = _("Create Policy Classifier")
    help_text = _("Create Policy Classifier.")
    submit_label = _("Save Changes")

    def get_success_url(self):
        return reverse('horizon:project:application_policy:index')

    def get_object_id(self, classifier):
        return [classifier.id]


class AddPolicyActionView(gbforms.HelpTextModalMixin,
                          gbforms.ReversingModalFormView):
    form_class = policy_rule_set_forms.AddPolicyActionForm
    template_name = "gbpui/form_with_description.html"
    submit_url = "horizon:project:application_policy:addpolicyaction"
    modal_header = _("Create Policy Action")
    page_title = _("Create Policy Action")
    submit_label = _("Create")
    help_text = _("Create Policy Action.")

    def get_success_url(self):
        return reverse('horizon:project:application_policy:index')


class UpdatePolicyActionView(gbforms.HelpTextModalMixin,
                             gbforms.ReversingModalFormView):
    form_class = policy_rule_set_forms.UpdatePolicyActionForm
    template_name = "gbpui/form_with_description.html"
    submit_url = "horizon:project:application_policy:updatepolicyaction"
    modal_header = _("Edit Policy Action")
    page_title = _("Edit Policy Action")
    submit_label = _("Save Changes")
    help_text = _("Edit Policy Action.")

    def get_submit_url_params(self, **kwargs):
        return {"policyaction_id": self.kwargs['policyaction_id']}

    def get_initial(self):
        return {'policyaction_id': self.kwargs['policyaction_id']}


class PolicyRuleSetDetailsView(tabs.TabView):
    tab_group_class = (PolicyRuleSetDetailsTabs)
    template_name = 'gbpui/details_tabs.html'
    page_title = _("Policy Rule Set Details")


class PolicyRuleDetailsView(tabs.TabView):
    tab_group_class = (PolicyRuleDetailsTabs)
    template_name = 'gbpui/details_tabs.html'
    page_title = _("Policy Rule Details")


class UpdatePolicyRuleView(gbforms.HelpTextModalMixin,
                           gbforms.ReversingModalFormView):
    form_class = policy_rule_set_forms.UpdatePolicyRuleForm

    modal_header = _("Edit Policy Rule")
    submit_label = _("Update Policy Rule")
    submit_url = "horizon:project:application_policy:updatepolicyrule"
    template_name = "gbpui/form_with_description.html"
    page_title = _("Edit Policy Rule")
    help_text = _("Edit Policy Rule.")

    def get_submit_url_params(self, **kwargs):
        return {"policyrule_id": self.kwargs['policyrule_id']}

    def get_initial(self):
        return {'policyrule_id': self.kwargs['policyrule_id']}


class PolicyClassifierDetailsView(tabs.TabView):
    tab_group_class = (PolicyClassifierDetailsTabs)
    template_name = "gbpui/details_tabs.html"
    page_title = _("Policy Classifier Details")


class UpdatePolicyClassifierView(gbforms.HelpTextModalMixin,
                                 gbforms.ReversingModalFormView):
    form_class = policy_rule_set_forms.UpdatePolicyClassifierForm
    modal_header = _("Edit Policy Classifier")
    submit_label = _("Update Policy Classifier")
    submit_url = "horizon:project:application_policy:updatepolicyclassifier"
    template_name = "gbpui/form_with_description.html"
    page_title = _("Edit Policy Classifier")
    help_text = _("Edit Policy Classifier.")

    def get_submit_url_params(self, **kwargs):
        return {"policyclassifier_id": self.kwargs['policyclassifier_id']}

    def get_initial(self):
        return {'policyclassifier_id': self.kwargs['policyclassifier_id']}


class PolicyActionDetailsView(tabs.TabView):
    tab_group_class = (PolicyActionDetailsTabs)
    template_name = "gbpui/details_tabs.html"
    page_title = _("Policy Action Details")
