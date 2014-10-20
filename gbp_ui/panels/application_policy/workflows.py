
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

from horizon import exceptions
from horizon import forms
from horizon import workflows

from gbp_ui import client


class SelectPolicyRuleAction(workflows.Action):
    policy_rules = forms.MultipleChoiceField(
        label=_("Policy Rules"),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        help_text=_("Create a contract with selected rules."))

    class Meta:
        name = _("Rules")
        help_text = _("Select policy-rules for your contract.")

    def populate_policy_rules_choices(self, request, context):
        try:
            tenant_id = self.request.user.tenant_id
            rules = client.policyrule_list(request,
                                                     tenant_id=tenant_id)
            for r in rules:
                r.set_id_as_name_if_empty()
            rules = sorted(rules,
                           key=lambda rule: rule.name)
            rule_list = [(rule.id, rule.name) for rule in rules]
        except Exception as e:
            rule_list = []
            exceptions.handle(request,
                              _('Unable to retrieve rules (%(error)s).') % {
                                  'error': str(e)})
        return rule_list


class SelectPolicyRuleStep(workflows.Step):
    action_class = SelectPolicyRuleAction
    contributes = ("policy_rules",)

    def contribute(self, data, context):
        if data:
            rules = self.workflow.request.POST.getlist("policy_rules")
            if rules:
                rules = [r for r in rules if r != '']
                context['policy_rules'] = rules
            return context


class AddContractAction(workflows.Action):
    name = forms.CharField(max_length=80,
                           label=_("Name"),
                           required=False)
    description = forms.CharField(max_length=80,
                                  label=_("Description"),
                                  required=False)

    def __init__(self, request, *args, **kwargs):
        super(AddContractAction, self).__init__(request, *args, **kwargs)

    class Meta:
        name = _("Create Contract")
        help_text = _("Create a new Contract")


class AddContractStep(workflows.Step):
    action_class = AddContractAction
    contributes = ("name", "description")

    def contribute(self, data, context):
        context = super(AddContractStep, self).contribute(data, context)
        return context


class AddContract(workflows.Workflow):
    slug = "addcontract"
    name = _("Create Contract")
    finalize_button_name = _("Create")
    success_message = _('Created Contract "%s".')
    failure_message = _('Unable to create Contract "%s".')
    default_steps = (AddContractStep,
                     SelectPolicyRuleStep)
    wizard = True

    def get_success_url(self):
        return reverse("horizon:project:application_policy:index")

    def format_status_message(self, message):
        return message % self.context.get('name')

    def _create_contract(self, request, context):
        try:
            client.contract_create(request, **context)
            return True
        except Exception as e:
            msg = self.format_status_message(self.failure_message) + str(e)
            exceptions.handle(request, msg)
            return False

    def handle(self, request, context):
        contract = self._create_contract(request, context)
        if not contract:
            return False
        return True


class SelectPolicyClassifierAction(workflows.Action):
    classifier = forms.ChoiceField(
        label=_("Policy Classifier"),
        required=False,
        help_text=_("Create a policy with selected classifier."))

    class Meta:
        name = _("Classifiers")
        help_text = _("Select classifiers for your policy-rule.")

    def populate_classifier_choices(self, request, context):
        try:
            tenant_id = self.request.user.tenant_id
            classifiers = client.policyclassifier_list(request,
                tenant_id=tenant_id)
            for classifier in classifiers:
                classifier.set_id_as_name_if_empty()
            classifiers = sorted(classifiers,
                           key=lambda classifier: classifier.name)
            classifier_list = [(c.id, c.name) for c in classifiers]
        except Exception as e:
            classifier_list = []
            exceptions.handle(request,
                              _('Unable to retrieve classifiers (%(error)s).')
                              % {'error': str(e)})
        return classifier_list


class SelectPolicyActionAction(workflows.Action):
    actions = forms.MultipleChoiceField(
        label=_("Policy Action"),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        help_text=_("Create a policy-rule with selected action."))

    class Meta:
        name = _("actions")
        help_text = _("Select actions for your policy-rule.")

    def populate_actions_choices(self, request, context):
        try:
            tenant_id = self.request.user.tenant_id
            actions = client.policyaction_list(request,
                tenant_id=tenant_id)
            action_list = [a.id for a in actions]
            for action in actions:
                action.set_id_as_name_if_empty()
            actions = sorted(actions,
                           key=lambda action: action.name)
            action_list = [(a.id, a.name) for a in actions]
        except Exception as e:
            action_list = []
            exceptions.handle(request,
                              _('Unable to retrieve actions (%(error)s).')
                              % {'error': str(e)})
        return action_list


class SelectPolicyActionStep(workflows.Step):
    action_class = SelectPolicyActionAction
    contributes = ("policy_actions",)

    def contribute(self, data, context):
        if data:
            actions = self.workflow.request.POST.getlist(
                "actions")
            if actions:
                actions = [a for a in actions if a != '']
                context['policy_actions'] = actions
            return context


class SelectPolicyClassifierStep(workflows.Step):
    action_class = SelectPolicyClassifierAction
    contributes = ("policy_classifier_id",)

    def contribute(self, data, context):
        context = super(SelectPolicyClassifierStep, self).contribute(data,
                                                                     context)
        if data:
            context['policy_classifier_id'] = data['classifier']
            return context


class AddPolicyRuleAction(workflows.Action):
    name = forms.CharField(max_length=80,
                           label=_("Name"),
                           required=False)
    description = forms.CharField(max_length=80,
                                  label=_("Description"),
                                  required=False)

    def __init__(self, request, *args, **kwargs):
        super(AddPolicyRuleAction, self).__init__(request, *args, **kwargs)

    class Meta:
        name = _("Create Policy-Rule")
        help_text = _("Create a new Policy-Rule")


class AddPolicyRuleStep(workflows.Step):
    action_class = AddPolicyRuleAction
    contributes = ("name", "description")

    def contribute(self, data, context):
        context = super(AddPolicyRuleStep, self).contribute(data, context)
        return context


class AddPolicyRule(workflows.Workflow):
    slug = "addpolicyrule"
    name = _("Create Policy-Rule")
    finalize_button_name = _("Create")
    success_message = _('Created Policy-Rule "%s".')
    failure_message = _('Unable to create Policy-Rule "%s".')
    default_steps = (AddPolicyRuleStep,
                     SelectPolicyClassifierStep,
                     SelectPolicyActionStep)
    wizard = True

    def get_success_url(self):
        return reverse("horizon:project:application_policy:index")

    def format_status_message(self, message):
        return message % self.context.get('name')

    def _create_policyrule(self, request, context):
        try:
            client.policyrule_create(request, **context)
            return True
        except Exception as e:
            msg = self.format_status_message(self.failure_message) + str(e)
            exceptions.handle(request, msg)
            return False

    def handle(self, request, context):
        policy_rule = self._create_policyrule(request, context)
        if not policy_rule:
            return False
        return True


class AddClassifierAction(workflows.Action):
    name = forms.CharField(max_length=80, label=_("Name"), required=False)
    protocol = forms.ChoiceField(
        label=_("Protocol"),
        choices=[('tcp', _('TCP')),
                 ('udp', _('UDP')),
                 ('icmp', _('ICMP')),
                 ('any', _('ANY'))],)
    port_range = forms.CharField(
        max_length=80,
        label=_("Port/Range(min:max)"),
        required=False)
    direction = forms.ChoiceField(
        label=_("Direction"),
        choices=[('in', _('IN')),
                 ('out', _('OUT')),
                 ('bi', _('BI'))])

    def __init__(self, request, *args, **kwargs):
        super(AddClassifierAction, self).__init__(request, *args, **kwargs)

    class Meta:
        name = _("Create Classifier")
        help_text = _("Create a new Classifier")


class AddClassifierStep(workflows.Step):
    action_class = AddClassifierAction
    contributes = ("name", "protocol", "port_range", "direction")

    def contribute(self, data, context):
        context = super(AddClassifierStep, self).contribute(data, context)
        return context


class AddPolicyClassifier(workflows.Workflow):
    slug = "addpolicyclassifier"
    name = _("Create Classifier")
    finalize_button_name = _("Create")
    success_message = _('Created Classifier "%s".')
    failure_message = _('Unable to create Classifier "%s".')
    success_url = "horizon:project:application_policy:index"
    default_steps = (AddClassifierStep,)

    def format_status_message(self, message):
        return message % self.context.get('name')

    def _create_classifer(self, request, context):
        try:
            client.policyclassifier_create(request, **context)
            return True
        except Exception as e:
            msg = self.format_status_message(self.failure_message) + str(e)
            exceptions.handle(request, msg)
            return False

    def handle(self, request, context):
        classifier = self._create_classifer(request, context)
        if not classifier:
            return False
        return True


class AddPolicyActionAction(workflows.Action):
    name = forms.CharField(max_length=80,
                           label=_("Name"),
                           required=False)
    action_type = forms.ChoiceField(
        label=_("Action"),
        choices=[('allow', _('ALLOW')), ('redirect', _('REDIRECT'))],)
    action_value = forms.CharField(max_length=36,
                           label=_("Action value"),
                           required=False)

    def __init__(self, request, *args, **kwargs):
        super(AddPolicyActionAction, self).__init__(request, *args, **kwargs)

    class Meta:
        name = _("Create Action")
        help_text = _("Create a new Action")


class AddPolicyActionStep(workflows.Step):
    action_class = AddPolicyActionAction
    contributes = ("name", "action_type", "action_value")

    def contribute(self, data, context):
        context = super(AddPolicyActionStep, self).contribute(data, context)
        if data:
            if not context['action_value']:
                del context['action_value']
            return context


class AddPolicyAction(workflows.Workflow):
    slug = "addpolicyaction"
    name = _("Create Action")
    finalize_button_name = _("Create")
    success_message = _('Created Action "%s".')
    failure_message = _('Unable to create Action "%s".')
    success_url = "horizon:project:application_policy:index"
    default_steps = (AddPolicyActionStep,)

    def format_status_message(self, message):
        return message % self.context.get('name')

    def _create_action(self, request, context):
        try:
            client.policyaction_create(request, **context)
            return True
        except Exception as e:
            msg = self.format_status_message(self.failure_message) + str(e)
            exceptions.handle(request, msg)
            return False

    def handle(self, request, context):
        action = self._create_action(request, context)
        if not action:
            return False
        return True
