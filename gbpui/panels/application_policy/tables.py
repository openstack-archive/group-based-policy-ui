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

from horizon import tables


class AddAppPolicyLink(tables.LinkAction):
    name = "addpolicy_rule_set"
    verbose_name = _("Create Policy Rule Set")
    url = "horizon:project:application_policy:addpolicy_rule_set"
    classes = ("ajax-modal", "btn-addpolicy_rule_set",)


class UpdateAppPolicyLink(tables.LinkAction):
    name = "updatepolicy_rule_set"
    verbose_name = _("Edit")
    classes = ("ajax-modal", 'edit_policy_rule_set')

    def get_link_url(self, policy_rule_set):
        urlpath = "horizon:project:application_policy:updatepolicy_rule_set"
        base_url = reverse(urlpath, kwargs={
            'policy_rule_set_id': policy_rule_set.id})
        return base_url


class DeleteAppPolicyLink(tables.DeleteAction):
    name = "deletepolicyruleset"
    action_present = _("Delete")
    action_past = _("Scheduled deletion of %(data_type)s")
    data_type_singular = _("Policy Rule Set")
    data_type_plural = _("Policy Rule Sets")


class AddPolicyRuleLink(tables.LinkAction):
    name = "addpolicyrules"
    verbose_name = _("Create Policy Rule")
    url = "horizon:project:application_policy:addpolicyrule"
    classes = ("ajax-modal", "btn-addpolicyrule",)


class UpdatePolicyRuleLink(tables.LinkAction):
    name = "updatepolicyrule"
    verbose_name = _("Edit")
    classes = ("ajax-modal", "btn-update",)

    def get_link_url(self, policy_rule):
        urlstring = "horizon:project:application_policy:updatepolicyrule"
        base_url = reverse(urlstring,
                           kwargs={'policyrule_id': policy_rule.id})
        return base_url


class DeletePolicyRuleLink(tables.DeleteAction):
    name = "deletepolicyrule"
    action_present = _("Delete")
    action_past = _("Scheduled deletion of %(data_type)s")
    data_type_singular = _("Policy Rule")
    data_type_plural = _("Policy Rules")


class AddPolicyClassifierLink(tables.LinkAction):
    name = "addpolicyclassifiers"
    verbose_name = _("Create Policy Classifier")
    url = "horizon:project:application_policy:addpolicyclassifier"
    classes = ("ajax-modal", "btn-addpolicyclassifier",)


class UpdatePolicyClassifierLink(tables.LinkAction):
    name = "updatepolicyclassifier"
    verbose_name = _("Edit")
    classes = ("ajax-modal", "btn-update",)

    def get_link_url(self, policy_classifier):
        base_url = reverse(
            "horizon:project:application_policy:updatepolicyclassifier",
            kwargs={'policyclassifier_id': policy_classifier.id})
        return base_url


class DeletePolicyClassifierLink(tables.DeleteAction):
    name = "deletepolicyclassifier"
    action_present = _("Delete")
    action_past = _("Scheduled deletion of %(data_type)s")
    data_type_singular = _("Policy Classifier")
    data_type_plural = _("Policy Classifiers")


class AddPolicyActionLink(tables.LinkAction):
    name = "addpolicyactions"
    verbose_name = _("Create Policy Action")
    url = "horizon:project:application_policy:addpolicyaction"
    classes = ("ajax-modal", "btn-addpolicyaction",)


class UpdatePolicyActionLink(tables.LinkAction):
    name = "updatepolicyaction"
    verbose_name = _("Edit")
    classes = ("ajax-modal", "btn-update",)

    def get_link_url(self, policy_action):
        urlstring = "horizon:project:application_policy:updatepolicyaction"
        base_url = reverse(urlstring,
                           kwargs={'policyaction_id': policy_action.id})
        return base_url


class DeletePolicyActionLink(tables.DeleteAction):
    name = "deletepolicyaction"
    action_present = _("Delete")
    action_past = _("Scheduled deletion of %(data_type)s")
    data_type_singular = _("Policy Action")
    data_type_plural = _("Policy Actions")


class ApplicationPoliciesTable(tables.DataTable):
    name = tables.Column("name",
            verbose_name=_("Name"),
            link="horizon:project:application_policy:policy_rule_set_details")
    description = tables.Column("description",
                                verbose_name=_("Description"))
    policy_rules = tables.Column("policy_rules",
                                 sortable=False,
                                 verbose_name=_("Policy Rules"))

    class Meta:
        name = "application_policies_table"
        verbose_name = _("Policy Rule Set")
        table_actions = (AddAppPolicyLink, DeleteAppPolicyLink)
        row_actions = (UpdateAppPolicyLink, DeleteAppPolicyLink)


class PolicyRulesTable(tables.DataTable):
    name = tables.Column("name",
            verbose_name=_("Name"),
            link="horizon:project:application_policy:policyruledetails")
    description = tables.Column("description",
                                verbose_name=_("Description"))
    enabled = tables.Column("enabled",
                            verbose_name=_("Enabled"))
    policy_classifier = tables.Column("policy_classifier_id",
                                      verbose_name=_("Policy Classifier"))
    policy_actions = tables.Column("policy_actions",
                                      verbose_name=_("Policy Actions"))

    class Meta:
        name = "policyrulestable"
        verbose_name = _("Policy Rules")
        table_actions = (AddPolicyRuleLink, DeletePolicyRuleLink)
        row_actions = (UpdatePolicyRuleLink, DeletePolicyRuleLink)


class PolicyClassifiersTable(tables.DataTable):
    name = tables.Column("name",
            verbose_name=_("Name"),
            link="horizon:project:application_policy:policyclassifierdetails")
    description = tables.Column("description",
                                verbose_name=_("Description"))
    protocol = tables.Column("protocol",
                             verbose_name=_("Protocol"))
    port_range = tables.Column("port_range",
                               verbose_name=_("Port Range"))
    direction = tables.Column("direction",
                              verbose_name=_("Direction"))

    class Meta:
        name = "policyclassifierstable"
        verbose_name = _("Policy Classifiers")
        table_actions = (AddPolicyClassifierLink, DeletePolicyClassifierLink)
        row_actions = (UpdatePolicyClassifierLink, DeletePolicyClassifierLink)


class PolicyActionsTable(tables.DataTable):
    name = tables.Column("name",
            verbose_name=_("Name"),
            link="horizon:project:application_policy:policyactiondetails")
    description = tables.Column("description",
                                verbose_name=_("Description"))
    action_type = tables.Column("action_type",
                                verbose_name=_("Type"))
    action_value = tables.Column("action_value",
                                 verbose_name=_("Value"))

    class Meta:
        name = "policyactionstable"
        verbose_name = _("Policy Actions")
        table_actions = (AddPolicyActionLink, DeletePolicyActionLink)
        row_actions = (UpdatePolicyActionLink, DeletePolicyActionLink)
