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
from django.utils.translation import ugettext_lazy as _

import extractors

from horizon import tables

from gbpui import client

from gbpui.common import tables as gbtables

from gbpui import GBP_POLICY_FILE


class AddPolicyRuleSetLink(tables.LinkAction):
    name = "addpolicy_rule_set"
    verbose_name = _("Create Policy Rule Set")
    url = "horizon:project:application_policy:addpolicy_rule_set"
    classes = ("ajax-modal", "btn-addpolicy_rule_set",)
    policy_rules = ((GBP_POLICY_FILE, "create_policy_rule_set"),)


class UpdatePolicyRuleSetLink(tables.LinkAction):
    name = "updatepolicy_rule_set"
    verbose_name = _("Edit")
    classes = ("ajax-modal", 'edit_policy_rule_set')
    policy_rules = ((GBP_POLICY_FILE, "update_policy_rule_set"),)

    def get_link_url(self, policy_rule_set):
        urlpath = "horizon:project:application_policy:updatepolicy_rule_set"
        base_url = reverse(urlpath, kwargs={
            'policy_rule_set_id': policy_rule_set.id})
        return base_url


class DeletePolicyRuleSetLink(gbtables.GBPDeleteAction):
    name = "deletepolicyruleset"
    action_present = _("Delete")
    action_past = _("Deleted %(data_type)s")
    data_type_singular = _("Policy Rule Set")
    data_type_plural = _("Policy Rule Sets")
    policy_rules = ((GBP_POLICY_FILE, "delete_policy_rule_set"),)

    def action(self, request, object_id):
        client.policy_rule_set_delete(request, object_id)


class AddPolicyRuleLink(tables.LinkAction):
    name = "addpolicyrules"
    verbose_name = _("Create Policy Rule")
    url = "horizon:project:application_policy:addpolicyrule"
    classes = ("ajax-modal", "btn-addpolicyrule",)
    policy_rules = ((GBP_POLICY_FILE, "create_policy_rule"),)


class UpdatePolicyRuleLink(tables.LinkAction):
    name = "updatepolicyrule"
    verbose_name = _("Edit")
    classes = ("ajax-modal", "btn-update",)
    policy_rules = ((GBP_POLICY_FILE, "update_policy_rule"),)

    def get_link_url(self, policy_rule):
        urlstring = "horizon:project:application_policy:updatepolicyrule"
        base_url = reverse(urlstring,
                           kwargs={'policyrule_id': policy_rule.id})
        return base_url


class DeletePolicyRuleLink(gbtables.GBPDeleteAction):
    name = "deletepolicyrule"
    action_present = _("Delete")
    action_past = _("Scheduled deletion of %(data_type)s")
    data_type_singular = _("Policy Rule")
    data_type_plural = _("Policy Rules")
    policy_rules = ((GBP_POLICY_FILE, "delete_policy_rule"),)

    def action(self, request, object_id):
        client.policyrule_delete(request, object_id)


class AddPolicyClassifierLink(tables.LinkAction):
    name = "addpolicyclassifiers"
    verbose_name = _("Create Policy Classifier")
    url = "horizon:project:application_policy:addpolicyclassifier"
    classes = ("ajax-modal", "btn-addpolicyclassifier",)
    policy_rules = ((GBP_POLICY_FILE, "create_policy_classifier"),)


class UpdatePolicyClassifierLink(tables.LinkAction):
    name = "updatepolicyclassifier"
    verbose_name = _("Edit")
    classes = ("ajax-modal", "btn-update",)
    policy_rules = ((GBP_POLICY_FILE, "update_policy_classifier"),)

    def get_link_url(self, policy_classifier):
        base_url = reverse(
            "horizon:project:application_policy:updatepolicyclassifier",
            kwargs={'policyclassifier_id': policy_classifier.id})
        return base_url


class DeletePolicyClassifierLink(gbtables.GBPDeleteAction):
    name = "deletepolicyclassifier"
    action_present = _("Delete")
    action_past = _("Scheduled deletion of %(data_type)s")
    data_type_singular = _("Policy Classifier")
    data_type_plural = _("Policy Classifiers")
    policy_rules = ((GBP_POLICY_FILE, "delete_policy_classifier"),)

    def action(self, request, object_id):
        client.policyclassifier_delete(request, object_id)


class AddPolicyActionLink(tables.LinkAction):
    name = "addpolicyactions"
    verbose_name = _("Create Policy Action")
    url = "horizon:project:application_policy:addpolicyaction"
    classes = ("ajax-modal", "btn-addpolicyaction",)
    policy_rules = ((GBP_POLICY_FILE, "create_policy_action"),)


class UpdatePolicyActionLink(tables.LinkAction):
    name = "updatepolicyaction"
    verbose_name = _("Edit")
    classes = ("ajax-modal", "btn-update",)
    policy_rules = ((GBP_POLICY_FILE, "update_policy_action"),)

    def get_link_url(self, policy_action):
        urlstring = "horizon:project:application_policy:updatepolicyaction"
        base_url = reverse(urlstring,
                           kwargs={'policyaction_id': policy_action.id})
        return base_url


class DeletePolicyActionLink(gbtables.GBPDeleteAction):
    name = "deletepolicyaction"
    action_present = _("Delete")
    action_past = _("Scheduled deletion of %(data_type)s")
    data_type_singular = _("Policy Action")
    data_type_plural = _("Policy Actions")
    policy_rules = ((GBP_POLICY_FILE, "delete_policy_action"),)

    def action(self, request, object_id):
        client.policyaction_delete(request, object_id)


class ApplicationPoliciesTable(tables.DataTable):
    name = gbtables.LinkColumn(
        "name",
        verbose_name=_("Name"),
        link="horizon:project:application_policy:policy_rule_set_details",
        link_rules=((GBP_POLICY_FILE, "get_policy_rule_set"),)
    )
    description = tables.Column(
        "description",
        verbose_name=_("Description"))
    policy_rules = gbtables.ListColumn(
        "name",
        sortable=False,
        verbose_name=_("Policy Rules"),
        source_list="policy_rules",
        link="horizon:project:application_policy:policyruledetails",
        list_rules=((GBP_POLICY_FILE, "get_policy_rule"),)
    )

    class Meta(object):
        name = "application_policies_table"
        verbose_name = _("Policy Rule Set")
        table_actions = (AddPolicyRuleSetLink, DeletePolicyRuleSetLink)
        row_actions = (UpdatePolicyRuleSetLink, DeletePolicyRuleSetLink)


class PolicyRulesTable(tables.DataTable):
    name = gbtables.LinkColumn(
        "name",
        verbose_name=_("Name"),
        link="horizon:project:application_policy:policyruledetails",
        link_rules=((GBP_POLICY_FILE, "get_policy_rule"),)
    )
    description = tables.Column("description",
                                verbose_name=_("Description"))
    enabled = tables.Column("enabled",
                            verbose_name=_("Enabled"))
    policy_classifier = gbtables.LinkColumn(
        extractors.get_classifier_name,
        verbose_name=_("Policy Classifier"),
        link=extractors.get_classifier_link,
        link_rules=((GBP_POLICY_FILE, "get_policy_classifier"),),
        get_policy_target=extractors.get_classifier_target
    )
    policy_actions = gbtables.ListColumn(
        "name",
        source_list="policy_actions",
        link="horizon:project:application_policy:policyactiondetails",
        verbose_name=_("Policy Actions"),
        list_rules=((GBP_POLICY_FILE, "get_policy_action"),)
    )

    class Meta(object):
        name = "policyrulestable"
        verbose_name = _("Policy Rules")
        table_actions = (AddPolicyRuleLink, DeletePolicyRuleLink)
        row_actions = (UpdatePolicyRuleLink, DeletePolicyRuleLink)


class PolicyClassifiersTable(tables.DataTable):
    name = gbtables.LinkColumn(
        "name",
        verbose_name=_("Name"),
        link="horizon:project:application_policy:policyclassifierdetails",
        link_rules=((GBP_POLICY_FILE, "get_policy_classifier"),)
    )
    description = tables.Column("description",
                                verbose_name=_("Description"))
    protocol = tables.Column("protocol",
                             verbose_name=_("Protocol"))
    port_range = tables.Column("port_range",
                               verbose_name=_("Port Range"))
    direction = tables.Column("direction",
                              verbose_name=_("Direction"))

    class Meta(object):
        name = "policyclassifierstable"
        verbose_name = _("Policy Classifiers")
        table_actions = (AddPolicyClassifierLink, DeletePolicyClassifierLink)
        row_actions = (UpdatePolicyClassifierLink, DeletePolicyClassifierLink)


class PolicyActionsTable(tables.DataTable):
    name = gbtables.LinkColumn(
        "name",
        verbose_name=_("Name"),
        link="horizon:project:application_policy:policyactiondetails",
        link_rules=((GBP_POLICY_FILE, "get_policy_action"),)
    )
    description = tables.Column("description",
                                verbose_name=_("Description"))
    action_type = tables.Column("action_type",
                                verbose_name=_("Type"))

    action_value = gbtables.LinkColumn(
        extractors.get_action_value_name,
        verbose_name=_("Value"),
        link=extractors.get_action_value_link,
        link_rules=((GBP_POLICY_FILE, "get_servicechain_spec"),)
    )

    class Meta(object):
        name = "policyactionstable"
        verbose_name = _("Policy Actions")
        table_actions = (AddPolicyActionLink, DeletePolicyActionLink)
        row_actions = (UpdatePolicyActionLink, DeletePolicyActionLink)
