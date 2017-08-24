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

import logging

from django.utils import html
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms

from horizon import workflows

from gbpui import client
from gbpui import fields

LOG = logging.getLogger(__name__)

POLICY_RULE_SET_URL = "horizon:project:application_policy:addpolicy_rule_set"
ADD_EXTERNAL_CONNECTIVITY = \
    "horizon:project:network_policy:create_external_connectivity"


class SelectPolicyRuleSetAction(workflows.Action):
    provided_policy_rule_set = fields.DynamicMultiChoiceField(
        label=_("Provided Policy Rule Set"),
        help_text=_("Choose a policy rule set for an Group."),
        add_item_link=POLICY_RULE_SET_URL,
        required=False)
    consumed_policy_rule_set = fields.DynamicMultiChoiceField(
        label=_("Consumed Policy Rule Set"),
        help_text=_("Select consumed policy rule set for Group."),
        add_item_link=POLICY_RULE_SET_URL,
        required=False)

    class Meta(object):
        name = _("Application Policy")
        help_text = _("Select Policy Rule Set for Group.")

    def _policy_rule_set_list(self, request):
        policy_rule_sets = client.policy_rule_set_list(request,
            tenant_id=request.user.tenant_id)
        for c in policy_rule_sets:
            c.set_id_as_name_if_empty()
        policy_rule_sets = sorted(policy_rule_sets,
                                  key=lambda rule: rule.name)
        return [(c.id, c.name) for c in policy_rule_sets]

    def populate_provided_policy_rule_set_choices(self, request, context):
        policy_rule_set_list = []
        try:
            rsets = self._policy_rule_set_list(request)
            if len(rsets) == 0:
                rsets.extend([('None', 'No Provided Policy Rule Sets')])
            policy_rule_set_list = rsets
        except Exception as e:
            policy_rule_set_list = []
            msg = _('Unable to retrieve policy rule set. %s.') % (str(e))
            exceptions.handle(request, msg)
        return policy_rule_set_list

    def populate_consumed_policy_rule_set_choices(self, request, context):
        policy_rule_set_list = []
        try:
            policy_rule_set_list = [('None', 'No Consumed Policy Rule Sets')]
            policy_rule_set_list =\
                self._policy_rule_set_list(request)
        except Exception as e:
            msg = _('Unable to retrieve policy rule set. %s.') % (str(e))
            exceptions.handle(request, msg)
        return policy_rule_set_list


class SelectL2policyAction(workflows.Action):
    l2policy_id = forms.ChoiceField(
        label=_("Network Policy"),
        help_text=_("Select network policy for Group."))
    network_service_policy_id = forms.ChoiceField(
        label=_("Network Services Policy"),
        help_text=_("Select network services policy for Group."),
        required=False)

    class Meta(object):
        name = _("Network Policy")
        help_text = _(
            "Select network policy for Group."
            "Selecting default will create an Network Policy implicitly.")

    def populate_l2policy_id_choices(self, request, context):
        policies = []
        try:
            policies = client.l2policy_list(request,
                tenant_id=request.user.tenant_id)
            for p in policies:
                p.set_id_as_name_if_empty()
            policies = sorted(policies, key=lambda rule: rule.name)
            policies = [(p.id, p.name + ":" + p.id) for p in policies]
            policies.insert(0, ('default', 'Default'))
        except Exception as e:
            exceptions.handle(request,
                              _("Unable to retrieve policies (%(error)s).")
                              % {'error': str(e)})
        return policies

    def populate_network_service_policy_id_choices(self, request, context):
        policies = []
        try:
            policies = client.networkservicepolicy_list(request,
                tenant_id=request.user.tenant_id)
            for p in policies:
                p.set_id_as_name_if_empty()
            policies = [(p.id, p.name + ":" + p.id) for p in policies]
            policies.insert(0, ('None', 'No Network Service Policy'))
        except Exception as e:
            msg = _("Unable to retrieve service policies. %s).") % (str(e))
            exceptions.handle(request, msg)
        return policies


class SelectL2policyStep(workflows.Step):
    action_class = SelectL2policyAction
    name = _("L2 Policy")
    contributes = ("l2policy_id", "network_services_policy_id",)

    def contribute(self, data, context):
        if data['l2policy_id'] != 'default':
            context['l2_policy_id'] = data['l2policy_id']
        if data['network_service_policy_id'] != 'None':
            context['network_service_policy_id'] = \
                data['network_service_policy_id']
        return context


class SelectPolicyRuleSetStep(workflows.Step):
    action_class = SelectPolicyRuleSetAction
    name = _("Provided Policy Rule Set")
    contributes = ("provided_policy_rule_sets", "consumed_policy_rule_sets",)

    def contribute(self, data, context):
        if data:
            policy_rule_sets = self.workflow.request.POST.getlist(
                "provided_policy_rule_set")
            if policy_rule_sets:
                policy_rule_set_dict = {}
                for policy_rule_set in policy_rule_sets:
                    if policy_rule_set != 'None':
                        policy_rule_set_dict[policy_rule_set] = None
                context['provided_policy_rule_sets'] = policy_rule_set_dict
            policy_rule_sets = self.workflow.request.POST.getlist(
                "consumed_policy_rule_set")
            if policy_rule_sets:
                policy_rule_set_dict = {}
                for policy_rule_set in policy_rule_sets:
                    if policy_rule_set != 'None':
                        policy_rule_set_dict[policy_rule_set] = None
                context['consumed_policy_rule_sets'] = policy_rule_set_dict
            return context


class AddPTGAction(workflows.Action):
    name = forms.CharField(max_length=80,
                           label=_("Name"))
    description = forms.CharField(max_length=80,
                                  label=_("Description"),
                                  required=False)
    shared = forms.BooleanField(label=_("Shared"),
                                initial=False, required=False)

    def __init__(self, request, *args, **kwargs):
        super(AddPTGAction, self).__init__(request, *args, **kwargs)

    class Meta(object):
        name = _("Group")
        help_text = _("Create Internal Group")


class AddPTGStep(workflows.Step):
    action_class = AddPTGAction
    contributes = ("name", "description", "shared")

    def contribute(self, data, context):
        context = super(AddPTGStep, self).contribute(data, context)
        return context


class AddPTG(workflows.Workflow):
    slug = "addpolicy_target"
    name = _("Create Internal Group")
    finalize_button_name = _("Create")
    success_message = _('Create Group "%s".')
    failure_message = _('Unable to create Group "%s".')
    success_url = "horizon:project:policytargets:index"
    default_steps = (AddPTGStep,
                     SelectPolicyRuleSetStep,
                     SelectL2policyStep,)
    wizard = True

    def format_status_message(self, message):
        return message % self.context.get('name')

    def handle(self, request, context):
        try:
            if context.get('name'):
                context['name'] = html.escape(context['name'])
            if context.get('description'):
                context['description'] = html.escape(context['description'])
            group = client.policy_target_create(request, **context)
            return group
        except Exception as e:
            msg = self.format_status_message(self.failure_message) + str(e)
            exceptions.handle(request, msg)
            return False


class ExternalConnectivityAction(workflows.Action):
    external_segments = fields.DynamicMultiChoiceField(
        label=_("External Connectivity"),
        required=True,
        add_item_link=ADD_EXTERNAL_CONNECTIVITY,
        help_text=_("Select external segment(s) for Group."))

    class Meta(object):
        name = _("External Connectivity")
        help_text = _(
            "Select External Connectivity for Group.")

    def populate_external_segments_choices(self, request, context):
        external_connectivities = []
        try:
            external_connectivities = client.externalconnectivity_list(
                request, tenant_id=request.user.tenant_id)
            for p in external_connectivities:
                p.set_id_as_name_if_empty()
            ext_conn_list = sorted(external_connectivities,
                key=lambda segment: segment.name)
            ext_conn_list = \
                [(p.id, p.name + ":" + p.id) for p in ext_conn_list]
        except Exception as e:
            exceptions.handle(request,
                              _("Unable to retrieve policies (%(error)s).")
                              % {'error': str(e)})
        return ext_conn_list


class ExternalConnectivityStep(workflows.Step):
    action_class = ExternalConnectivityAction
    name = _("External Connectivity")
    contributes = ("external_segments",)

    def contribute(self, data, context):
        context['external_segments'] = data.get('external_segments', [])
        return context


class ExtAddPTGAction(workflows.Action):
    name = forms.CharField(max_length=80,
                           label=_("Name"))
    description = forms.CharField(max_length=80,
                                  label=_("Description"),
                                  required=False)
    shared = forms.BooleanField(label=_("Shared"),
                                initial=False, required=False)

    def __init__(self, request, *args, **kwargs):
        super(ExtAddPTGAction, self).__init__(request, *args, **kwargs)

    class Meta(object):
        name = _("Group")
        help_text = _("Create External Group")


class ExtAddPTGStep(workflows.Step):
    action_class = ExtAddPTGAction
    contributes = ("name", "description", "shared")

    def contribute(self, data, context):
        context = super(ExtAddPTGStep, self).contribute(data, context)
        return context


class AddExternalPTG(workflows.Workflow):
    slug = "addexternal_policy_target"
    name = _("Create External Group")
    finalize_button_name = _("Create")
    success_message = _('Create External Group "%s".')
    failure_message = _('Unable to create External Group "%s".')
    success_url = "horizon:project:policytargets:index"
    default_steps = (ExtAddPTGStep,
                     SelectPolicyRuleSetStep,
                     ExternalConnectivityStep,)
    wizard = True

    def format_status_message(self, message):
        return message % self.context.get('name')

    def handle(self, request, context):
        try:
            if context.get('name'):
                context['name'] = html.escape(context['name'])
            if context.get('description'):
                context['description'] = html.escape(context['description'])
            group = client.ext_policy_target_create(request, **context)
            return group
        except Exception as e:
            msg = self.format_status_message(self.failure_message) + str(e)
            exceptions.handle(request, msg)
            return False


KEYPAIR_IMPORT_URL = "horizon:project:access_and_security:keypairs:import"
