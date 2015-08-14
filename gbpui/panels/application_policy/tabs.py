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

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs

from gbpui import client
from gbpui import column_filters as gfilters

import tables

PolicyRulesTable = tables.PolicyRulesTable
PolicyClassifiersTable = tables.PolicyClassifiersTable
PolicyActionsTable = tables.PolicyActionsTable


class PolicyActionsTab(tabs.TableTab):
    table_classes = (PolicyActionsTable,)
    name = _("Policy Actions")
    slug = "policyactions"
    template_name = "horizon/common/_detail_table.html"

    def get_policyactionstable_data(self):
        actions = []
        try:
            actions = client.policyaction_list(self.tab_group.request,
                tenant_id=self.tab_group.request.user.tenant_id)
            a = lambda x, y: gfilters.update_policyaction_attributes(x, y)
            actions = [a(self.request, item) for item in actions]
        except Exception as e:
            msg = _('Unable to retrieve actions list. %s') % (str(e))
            exceptions.handle(self.tab_group.request, msg)
        return actions


class PolicyClassifiersTab(tabs.TableTab):
    table_classes = (PolicyClassifiersTable,)
    name = _("Policy Classifiers")
    slug = "policyclassifiers"
    template_name = "horizon/common/_detail_table.html"

    def get_policyclassifierstable_data(self):
        try:
            classifiers = client.policyclassifier_list(self.tab_group.request,
                tenant_id=self.tab_group.request.user.tenant_id)
        except Exception:
            classifiers = []
            exceptions.handle(self.tab_group.request,
                              _('Unable to retrieve classifier list.'))
        else:
            classifiers = gfilters.update_classifier_attributes(classifiers)
        return classifiers


class PolicyRulesTab(tabs.TableTab):
    table_classes = (PolicyRulesTable,)
    name = _("Policy Rules")
    slug = "policyrules"
    template_name = "horizon/common/_detail_table.html"

    def get_policyrulestable_data(self):
        try:
            policy_rules = client.policyrule_list(self.tab_group.request,
                tenant_id=self.tab_group.request.user.tenant_id)
            policy_rules = [gfilters.update_policyrule_attributes(
                self.request, item) for item in policy_rules]
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
        policy_rule_sets = []
        try:
            policy_rule_sets = client.policy_rule_set_list(
                self.tab_group.request,
                tenant_id=self.tab_group.request.user.tenant_id)
            policy_rule_sets = [gfilters.update_pruleset_attributes(
                self.request, item) for item in policy_rule_sets]
        except Exception:
            exceptions.handle(
                self.tab_group.request,
                _('Unable to retrieve policy rule set list.'))

        for policy_rule_set in policy_rule_sets:
            policy_rule_set.set_id_as_name_if_empty()
        return policy_rule_sets


class ApplicationPoliciesTabs(tabs.TabGroup):
    slug = "application_policies_tabs"
    tabs = (ApplicationPoliciesTab,
            PolicyRulesTab,
            PolicyClassifiersTab,
            PolicyActionsTab)
    sticky = True


class PolicyRuleSetDetailsTab(tabs.Tab):
    name = _("Policy Rule Set Details")
    slug = "policy_rule_setdetails"
    template_name = "project/application_policy/_policy_rule_set_details.html"
    failure_url = reverse_lazy('horizon:project:policy_rule_set:index')

    def get_context_data(self, request):
        cid = self.tab_group.kwargs['policy_rule_set_id']
        try:
            policy_rule_set = client.policy_rule_set_get(request, cid)
            rules = client.policyrule_list(
                request, tenant_id=request.user.tenant_id,
                policy_rule_set_id=policy_rule_set.id)
            rules = [
                item for item in rules if item.id in
                policy_rule_set.policy_rules]
            rules_with_details = []
            for rule in rules:
                r = {}
                r['name'] = rule.name
                r['id'] = rule.id
                action_list = []
                for aid in rule.policy_actions:
                    action = client.policyaction_get(request, aid)
                    a = {'id': action.id}
                    if action.action_value:
                        if action.action_type == 'redirect':
                            scspec = client.get_servicechain_spec(request,
                                   action.action_value)
                            a['name'] = "Redirect:%s" % scspec.name
                        else:
                            values = (str(action.action_type),
                                    str(action.action_value))
                            name = "%s:%s" % values
                            a['name'] = name
                    else:
                        a['name'] = str(action.action_type)
                    action_list.append(a)
                r['actions'] = action_list
                r['classifier'] = client.policyclassifier_get(
                    request, rule.policy_classifier_id)
                rules_with_details.append(r)
        except Exception as e:
            msg = _('Unable to retrieve policy_rule_set details.') % (str(e))
            exceptions.handle(request, msg, redirect=self.failure_url)
        return {'policy_rule_set': policy_rule_set,
                'rules_with_details': rules_with_details}


class PolicyRuleSetDetailsTabs(tabs.TabGroup):
    slug = "policy_rule_settabs"
    tabs = (PolicyRuleSetDetailsTab,)


class PolicyRulesDetailsTab(tabs.Tab):
    name = _("Policy Rule Details")
    slug = "policyruledetails"
    template_name = "project/application_policy/_policyrules_details.html"
    failure_url = reverse_lazy('horizon:project:policyrule:index')

    def get_context_data(self, request):
        ruleid = self.tab_group.kwargs['policyrule_id']
        actions = []
        classifiers = []
        try:
            policyrule = client.policyrule_get(request, ruleid)
            actions = client.policyaction_list(request,
                tenant_id=request.user.tenant_id, policyrule_id=ruleid)
            actions = [
                item for item in actions if item.id in
                policyrule.policy_actions]
            classifiers = client.policyclassifier_list(
                request, tenant_id=request.user.tenant_id,
                policyrule_id=ruleid)
            classifiers = [
                item for item in classifiers if
                item.id == policyrule.policy_classifier_id]
        except Exception:
            exceptions.handle(request,
                              _('Unable to retrieve policyrule details.'),
                              redirect=self.failure_url)
        return {'policyrule': policyrule,
                'classifiers': classifiers,
                'actions': actions}


class PolicyRuleDetailsTabs(tabs.TabGroup):
    slug = "policyruletabs"
    tabs = (PolicyRulesDetailsTab,)


class PolicyClassifierDetailsTab(tabs.Tab):
    name = _("Policy Classifier Details")
    slug = "policyclassifierdetails"
    template_name = "project/application_policy/_policyclassifier_details.html"
    failure_url = reverse_lazy('horizon:project:policy_rule_set:index')

    def get_context_data(self, request):
        pcid = self.tab_group.kwargs['policyclassifier_id']
        try:
            policyclassifier = client.policyclassifier_get(request, pcid)
            policyclassifier = gfilters.update_classifier_attributes(
                policyclassifier)
        except Exception:
            exceptions.handle(request,
                              _('Unable to retrieve policy_rule_set details.'),
                              redirect=self.failure_url)
        return {'policyclassifier': policyclassifier}


class PolicyClassifierDetailsTabs(tabs.TabGroup):
    slug = "policyclassifiertabs"
    tabs = (PolicyClassifierDetailsTab,)


class PolicyActionDetailsTab(tabs.Tab):
    name = _("Policy Action Details")
    slug = "policyactiondetails"
    template_name = "project/application_policy/_policyaction_details.html"
    failure_url = reverse_lazy('horizon:project:policy_rule_set:index')

    def get_context_data(self, request):
        paid = self.tab_group.kwargs['policyaction_id']
        try:
            policyaction = client.policyaction_get(request, paid)
            policyaction = gfilters.update_policyaction_attributes(request,
                    policyaction)
        except Exception:
            exceptions.handle(request,
                              _('Unable to retrieve policyaction details.'),
                              redirect=self.failure_url)
        return {'policyaction': policyaction}


class PolicyActionDetailsTabs(tabs.TabGroup):
    slug = "policyactiontabs"
    tabs = (PolicyActionDetailsTab,)
