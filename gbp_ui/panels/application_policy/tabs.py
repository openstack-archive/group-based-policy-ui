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

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import tabs

from gbp_ui import client
import tables

PolicyRulesTable = tables.PolicyRulesTable
PolicyClassifiersTable = tables.PolicyClassifiersTable
PolicyActionsTable = tables.PolicyActionsTable


class PolicyActionsTab(tabs.TableTab):
    table_classes = (PolicyActionsTable,)
    name = _("Policy-Actions")
    slug = "policyactions"
    template_name = "horizon/common/_detail_table.html"

    def get_policyactionstable_data(self):
        try:
            tenant_id = self.request.user.tenant_id
            actions = client.policyaction_list(
                self.tab_group.request,
                tenant_id=tenant_id)
        except Exception:
            actions = []
            exceptions.handle(self.tab_group.request,
                              _('Unable to retrieve actions list.'))

        for action in actions:
            action.set_id_as_name_if_empty()

        return actions


class PolicyClassifiersTab(tabs.TableTab):
    table_classes = (PolicyClassifiersTable,)
    name = _("Policy-Classifiers")
    slug = "policyclassifiers"
    template_name = "horizon/common/_detail_table.html"

    def get_policyclassifierstable_data(self):
        try:
            tenant_id = self.request.user.tenant_id
            classifiers = client.policyclassifier_list(
                self.tab_group.request,
                tenant_id=tenant_id)
        except Exception:
            classifiers = []
            exceptions.handle(self.tab_group.request,
                              _('Unable to retrieve classifier list.'))

        for classifier in classifiers:
            classifier.set_id_as_name_if_empty()

        return classifiers


class PolicyRulesTab(tabs.TableTab):
    table_classes = (PolicyRulesTable,)
    name = _("Policy-Rules")
    slug = "policyrules"
    template_name = "horizon/common/_detail_table.html"

    def get_policyrulestable_data(self):
        try:
            tenant_id = self.request.user.tenant_id
            policy_rules = client.policyrule_list(
                self.tab_group.request,
                tenant_id=tenant_id)
        except Exception:
            policy_rules = []
            exceptions.handle(self.tab_group.request,
                              _('Unable to retrieve policy-rule list.'))

        for rule in policy_rules:
            rule.set_id_as_name_if_empty()

        return policy_rules


class ApplicationPoliciesTab(tabs.TableTab):
    table_classes = (tables.ApplicationPoliciesTable,)
    name = _("Policy Rule Set")
    slug = "application_policies"
    template_name = "horizon/common/_detail_table.html"

    def get_application_policies_table_data(self):
        try:
            tenant_id = self.request.user.tenant_id
            contracts = client.contract_list(self.tab_group.request, tenant_id=tenant_id)
        except Exception:
            contracts = []
            exceptions.handle(self.tab_group.request, _('Unable to retrieve policy rule set list.'))

        for contract in contracts:
            contract.set_id_as_name_if_empty()

        return contracts


class ApplicationPoliciesTabs(tabs.TabGroup):
    slug = "application_policies_tabs"
    tabs = (ApplicationPoliciesTab,
            PolicyRulesTab,
            PolicyClassifiersTab,
            PolicyActionsTab)
    sticky = True


class ContractDetailsTab(tabs.Tab):
    name = _("Contract Details")
    slug = "contractdetails"
    template_name = "project/application_policy/_contract_details.html"
    failure_url = reverse_lazy('horizon:project:contract:index')

    def get_context_data(self, request):
        cid = self.tab_group.kwargs['contract_id']
        try:
            contract = client.contract_get(request, cid)
            rules = client.policyrule_list(request, contract_id=contract.id)
            rules = [item for item in rules if item.id in contract.policy_rules]
            rules_with_details = []
            for rule in rules:
                r = {}
                r['name'] = rule.name
                r['id'] = rule.id
                action_list = []
                for aid in rule.policy_actions:
                    action = client.policyaction_get(request,aid)
                    action_list.append(action.name+":"+str(action.id)+":"+str(action.action_type))
                r['actions'] = action_list
                r['classifier'] = client.policyclassifier_get(request,rule.policy_classifier_id)
                rules_with_details.append(r)
        except Exception:
            exceptions.handle(request,
                              _('Unable to retrieve contract details.'),
                              redirect=self.failure_url)
        return {'contract': contract,'rules_with_details':rules_with_details}


class ContractDetailsTabs(tabs.TabGroup):
    slug = "contracttabs"
    tabs = (ContractDetailsTab,)


class PolicyRulesDetailsTab(tabs.Tab):
    name = _("PolicyRule Details")
    slug = "policyruledetails"
    template_name = "project/application_policy/_policyrules_details.html"
    failure_url = reverse_lazy('horizon:project:policyrule:index')

    def get_context_data(self, request):
        ruleid = self.tab_group.kwargs['policyrule_id']
        actions = []
        classifiers = []
        try:
            policyrule = client.policyrule_get(request, ruleid)
            actions = client.policyaction_list(request, policyrule_id=ruleid)
            classifiers = client.policyclassifier_list(request, policyrule_id=ruleid)
            classifiers = [item for item in classifiers if item.id == policyrule.policy_classifier_id]
        except Exception:
            exceptions.handle(request,
                              _('Unable to retrieve policyrule details.'),
                              redirect=self.failure_url)
        return {'policyrule': policyrule, 'classifiers':classifiers,'actions':actions}


class PolicyRuleDetailsTabs(tabs.TabGroup):
    slug = "policyruletabs"
    tabs = (PolicyRulesDetailsTab,)


class PolicyClassifierDetailsTab(tabs.Tab):
    name = _("Policyclassifier Details")
    slug = "policyclassifierdetails"
    template_name = "project/application_policy/_policyclassifier_details.html"
    failure_url = reverse_lazy('horizon:project:contract:index')

    def get_context_data(self, request):
        pcid = self.tab_group.kwargs['policyclassifier_id']
        try:
            policyclassifier = client.policyclassifier_get(request, pcid)
        except Exception:
            exceptions.handle(request,
                              _('Unable to retrieve contract details.'),
                              redirect=self.failure_url)
        return {'policyclassifier': policyclassifier}


class PolicyClassifierDetailsTabs(tabs.TabGroup):
    slug = "policyclassifiertabs"
    tabs = (PolicyClassifierDetailsTab,)


class PolicyActionDetailsTab(tabs.Tab):
    name = _("PolicyAction Details")
    slug = "policyactiondetails"
    template_name = "project/application_policy/_policyaction_details.html"
    failure_url = reverse_lazy('horizon:project:contract:index')

    def get_context_data(self, request):
        paid = self.tab_group.kwargs['policyaction_id']
        try:
            policyaction = client.policyaction_get(request, paid)
        except Exception:
            exceptions.handle(request,
                              _('Unable to retrieve policyaction details.'),
                              redirect=self.failure_url)
        return {'policyaction': policyaction}


class PolicyActionDetailsTabs(tabs.TabGroup):
    slug = "policyactiontabs"
    tabs = (PolicyActionDetailsTab,)
