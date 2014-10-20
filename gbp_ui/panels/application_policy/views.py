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

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from horizon import messages
from horizon import exceptions
from horizon import tabs
from horizon import workflows
from horizon import forms

from gbp_ui import client

import tabs as contract_tabs
import workflows as contract_workflows
import forms as contract_forms

ContractTabs = contract_tabs.ApplicationPoliciesTabs
ContractDetailsTabs = contract_tabs.ContractDetailsTabs
PolicyRuleDetailsTabs = contract_tabs.PolicyRuleDetailsTabs
PolicyClassifierDetailsTabs = contract_tabs.PolicyClassifierDetailsTabs
PolicyActionDetailsTabs = contract_tabs.PolicyActionDetailsTabs
AddContract = contract_workflows.AddContract
AddPolicyRule = contract_workflows.AddPolicyRule
AddPolicyClassifier = contract_workflows.AddPolicyClassifier
AddPolicyAction = contract_workflows.AddPolicyAction


class IndexView(tabs.TabView):
    tab_group_class = (ContractTabs)
    template_name = 'project/application_policy/details_tabs.html'

    def post(self, request, *args, **kwargs):
        obj_ids = request.POST.getlist('object_ids')
        action = request.POST['action']
        obj_type = re.search('.delete([a-z]+)', action).group(1)
        if not obj_ids:
            obj_ids.append(re.search('([0-9a-z-]+)$', action).group(1))
        if obj_type == 'policyaction':
            for obj_id in obj_ids:
                try:
                    client.policyaction_delete(request, obj_id)
                    messages.success(request, _('Deleted action %s') % obj_id)
                except Exception as e:
                    exceptions.handle(request,
                                      _('Unable to delete action. %s') % e)
        if obj_type == 'policyclassifier':
            for obj_id in obj_ids:
                try:
                    client.policyclassifier_delete(request, obj_id)
                    messages.success(request, _('Deleted classifer %s') % obj_id)
                except Exception as e:
                    exceptions.handle(request,
                                      _('Unable to delete classifier. %s') % e)
        if obj_type == 'policyrule':
            for obj_id in obj_ids:
                try:
                    client.policyrule_delete(request, obj_id)
                    messages.success(request,
                                     _('Deleted rule %s') % obj_id)
                except Exception as e:
                    exceptions.handle(request,
                                      _('Unable to delete rule. %s') % e)
        if obj_type == 'contract':
            for obj_id in obj_ids:
                try:
                    client.contract_delete(request, obj_id)
                    messages.success(request,
                                     _('Deleted rule %s') % obj_id)
                except Exception as e:
                    exceptions.handle(request,
                                      _('Unabled to delete contract. %s') % e)

        return self.get(request, *args, **kwargs)

class AddContractView(workflows.WorkflowView):
    workflow_class = AddContract
    template_name = "project/application_policy/addcontract.html"

class UpdateContractView(forms.ModalFormView):
    form_class = contract_forms.UpdateContractForm
    template_name = 'project/application_policy/update_contract.html'

    def get_context_data(self, **kwargs):
        context = super(UpdateContractView, self).get_context_data(**kwargs)
        context['contract_id'] = self.kwargs['contract_id']
        return context

    def get_initial(self):
        return {'contract_id': self.kwargs['contract_id']}
 


class AddPolicyRuleView(workflows.WorkflowView):
    workflow_class = AddPolicyRule
    template_name = "project/application_policy/addpolicyrule.html"


class AddPolicyClassifierView(workflows.WorkflowView):
    workflow_class = AddPolicyClassifier
    template_name = "project/application_policy/addpolicyclassifier.html"


class AddPolicyActionView(workflows.WorkflowView):
    workflow_class = AddPolicyAction
    template_name = "project/application_policy/addpolicyaction.html"

class UpdatePolicyActionView(forms.ModalFormView):
    form_class = contract_forms.UpdatePolicyActionForm
    template_name = "project/application_policy/update_policy_action.html"

    def get_context_data(self, **kwargs):
        context = super(UpdatePolicyActionView, self).get_context_data(**kwargs)
        context['policyaction_id'] = self.kwargs['policyaction_id']
        return context

    def get_initial(self):
        return {'policyaction_id': self.kwargs['policyaction_id']} 


class ContractDetailsView(tabs.TabView):
    tab_group_class = (ContractDetailsTabs)
    template_name = 'project/application_policy/details_tabs.html'


class PolicyRuleDetailsView(tabs.TabView):
    tab_group_class = (PolicyRuleDetailsTabs)
    template_name = 'project/application_policy/details_tabs.html'

class UpdatePolicyRuleView(forms.ModalFormView):
    form_class = contract_forms.UpdatePolicyRuleForm
    template_name = "project/application_policy/update_policy_rule.html"

    def get_context_data(self,**kwargs):
        context = super(UpdatePolicyRuleView,self).get_context_data(**kwargs)
        context['policyrule_id'] = self.kwargs['policyrule_id']
        return context

    def get_initial(self):
        return {'policyrule_id':self.kwargs['policyrule_id']} 

class PolicyClassifierDetailsView(tabs.TabView):
    tab_group_class = (PolicyClassifierDetailsTabs)
    template_name = 'project/application_policy/details_tabs.html'

class UpdatePolicyClassifierView(forms.ModalFormView):
    form_class = contract_forms.UpdatePolicyClassifierForm
    template_name = "project/application_policy/update_policy_classifier.html"

    def get_context_data(self,**kwargs):
        context = super(UpdatePolicyClassifierView,self).get_context_data(**kwargs)
        context['policyclassifier_id'] = self.kwargs['policyclassifier_id']
        return context

    def get_initial(self):
        return {'policyclassifier_id':self.kwargs['policyclassifier_id']}


class PolicyActionDetailsView(tabs.TabView):
    tab_group_class = (PolicyActionDetailsTabs)
    template_name = 'project/application_policy/details_tabs.html'
