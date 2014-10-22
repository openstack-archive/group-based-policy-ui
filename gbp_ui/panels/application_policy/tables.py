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

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import tables


class AddAppPolicyLink(tables.LinkAction):
    name = "addcontract"
    verbose_name = _("Create Policy Rule Set")
    url = "horizon:project:application_policy:addcontract"
    classes = ("ajax-modal", "btn-addcontract",)


class UpdateAppPolicyLink(tables.LinkAction):
    name = "updatecontract"
    verbose_name = _("Edit Policy Rule Set")
    classes = ("ajax-modal",'edit_contract')

    def get_link_url(self, contract):
        base_url = reverse("horizon:project:application_policy:updatecontract", kwargs={'contract_id': contract.id})
        return base_url


class DeleteAppPolicyLink(tables.DeleteAction):
    name = "deletecontract"
    action_present = _("Delete")
    action_past = _("Scheduled deletion of %(data_type)s")
    data_type_singular = _("Policy Rule Set")
    data_type_plural = _("Policy Rule Set")


class AddPolicyRuleLink(tables.LinkAction):
    name = "addpolicyrules"
    verbose_name = _("Create Policy-Rule")
    url = "horizon:project:application_policy:addpolicyrule"
    classes = ("ajax-modal", "btn-addpolicyrule",)


class UpdatePolicyRuleLink(tables.LinkAction):
    name = "updatepolicyrule"
    verbose_name = _("Edit PolicyRule")
    classes = ("ajax-modal", "btn-update",)

    def get_link_url(self, policy_rule):
        base_url = reverse("horizon:project:application_policy:updatepolicyrule",
                           kwargs={'policyrule_id': policy_rule.id})
        return base_url


class DeletePolicyRuleLink(tables.DeleteAction):
    name = "deletepolicyrule"
    action_present = _("Delete")
    action_past = _("Scheduled deletion of %(data_type)s")
    data_type_singular = _("PolicyRule")
    data_type_plural = _("PolicyRules")


class AddPolicyClassifierLink(tables.LinkAction):
    name = "addpolicyclassifiers"
    verbose_name = _("Create Policy-Classifier")
    url = "horizon:project:application_policy:addpolicyclassifier"
    classes = ("ajax-modal", "btn-addpolicyclassifier",)


class UpdatePolicyClassifierLink(tables.LinkAction):
    name = "updatepolicyclassifier"
    verbose_name = _("Edit PolicyClassifier")
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
    data_type_singular = _("PolicyClassifier")
    data_type_plural = _("PolicyClassifiers")


class AddPolicyActionLink(tables.LinkAction):
    name = "addpolicyactions"
    verbose_name = _("Create Policy-Action")
    url = "horizon:project:application_policy:addpolicyaction"
    classes = ("ajax-modal", "btn-addpolicyaction",)


class UpdatePolicyActionLink(tables.LinkAction):
    name = "updatepolicyaction"
    verbose_name = _("Edit PolicyAction")
    classes = ("ajax-modal", "btn-update",)

    def get_link_url(self, policy_action):
        base_url = reverse("horizon:project:application_policy:updatepolicyaction",
                           kwargs={'policyaction_id': policy_action.id})
        return base_url


class DeletePolicyActionLink(tables.DeleteAction):
    name = "deletepolicyaction"
    action_present = _("Delete")
    action_past = _("Scheduled deletion of %(data_type)s")
    data_type_singular = _("PolicyAction")
    data_type_plural = _("PolicyActions")


class ApplicationPoliciesTable(tables.DataTable):
	name = tables.Column("name", verbose_name=_("Name"),
			link="horizon:project:application_policy:policy_rule_set_details")
	description = tables.Column("description",
			verbose_name=_("Description"))

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
	direction = tables.Column("direction",
			verbose_name=_("Direction"))
	protocol = tables.Column("protocol",
			verbose_name=_("Protocol"))

	class Meta:
		name = "policyclassifierstable"
		verbose_name = _("Policy Classifiers")
		table_actions = (AddPolicyClassifierLink, DeletePolicyClassifierLink)
		row_actions = (UpdatePolicyClassifierLink, DeletePolicyClassifierLink)


class PolicyActionsTable(tables.DataTable):
	name = tables.Column("name", verbose_name=_("Name"),
			link="horizon:project:application_policy:policyactiondetails")
	description = tables.Column("description",
			verbose_name=_("Description"))
	action_value = tables.Column("action_value",
			verbose_name=_("Action Value"))
	action_type = tables.Column("action_type",
			verbose_name=_("Action Type"))


	class Meta:
		name = "policyactionstable"
		verbose_name = _("Policy Actions")
		table_actions = (AddPolicyActionLink, DeletePolicyActionLink)
		row_actions = (UpdatePolicyActionLink, DeletePolicyActionLink)
