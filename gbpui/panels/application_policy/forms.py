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
from django import http
from django.template.defaultfilters import filesizeformat  # noqa
from django.utils import html
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_variables  # noqa

from horizon import exceptions
from horizon import forms
from horizon import messages

from gbpui import client
from gbpui import column_filters as gfilters
from gbpui import fields

PROTOCOLS = ('TCP', 'UDP', 'ICMP', 'HTTP',
    'HTTPS', 'SMTP', 'DNS', 'FTP', 'ANY')
DIRECTIONS = [('in', _('IN')),
              ('out', _('OUT')),
              ('bi', _('BI'))]
POLICY_ACTION_TYPES = [('allow', _('ALLOW')),
                       ('redirect', _('REDIRECT')),
                       ('copy', _('COPY')),
                       ('log', _('LOG')),
                       ('qos', _('QoS'))]
PROTOCOL_MAP = {'http': 'tcp',
                'https': 'tcp',
                'smtp': 'tcp',
                'ftp': 'tcp',
                'dns': 'udp'
                }


class BaseUpdateForm(forms.SelfHandlingForm):

    def clean(self):
        cleaned_data = super(BaseUpdateForm, self).clean()
        updated_data = {d: cleaned_data[d] for d in cleaned_data
            if d in self.changed_data}
        return updated_data


class UpdatePolicyRuleSetForm(BaseUpdateForm):
    name = forms.CharField(label=_("Name"))
    description = forms.CharField(label=_("Description"), required=False)
    policy_rules = fields.TransferTableField(label=_("Policy Rules"), )
    shared = forms.BooleanField(label=_("Shared"), required=False)

    def __init__(self, request, *args, **kwargs):
        super(UpdatePolicyRuleSetForm, self).__init__(request, *args, **kwargs)
        rules = []
        try:
            items = client.policyrule_list(request,
                tenant_id=request.user.tenant_id)
            rules = [(p.id, p.name) for p in items]
            policy_rule_set = client.policy_rule_set_get(
                request, self.initial['policy_rule_set_id'])
            if policy_rule_set:
                self.fields['name'].initial = policy_rule_set.name
                self.fields[
                    'description'].initial = policy_rule_set.description
                self.fields['shared'].initial = policy_rule_set.shared
                existing = [item for item in policy_rule_set.policy_rules]
                self.fields['policy_rules'].initial = existing
        except Exception:
            exceptions.handle(request, _('Unable to retrieve policy rules'))
        self.fields['policy_rules'].choices = rules

    def handle(self, request, context):
        try:
            policy_rule_set_id = self.initial['policy_rule_set_id']
            if context.get('name'):
                context['name'] = html.escape(context['name'])
            if context.get('description'):
                context['description'] = html.escape(context['description'])
            client.policy_rule_set_update(request,
                                          policy_rule_set_id,
                                          **context
                                          )
            messages.success(request, _('PolicyRuleSet successfully updated.'))
            url = reverse('horizon:project:application_policy:index')
            return http.HttpResponseRedirect(url)
        except Exception:
            redirect = reverse('horizon:project:policy_rule_sets:index')
            exceptions.handle(
                request, _("Unable to update policy_rule_set."),
                redirect=redirect)


class AddPolicyActionForm(forms.SelfHandlingForm):
    name = forms.CharField(label=_("Name"))
    description = forms.CharField(label=_("Description"),
                                  required=False)
    action_type = forms.ChoiceField(label=_("Action"),
                                    choices=POLICY_ACTION_TYPES,
                                    widget=forms.Select(attrs={
                                        'class': 'switchable',
                                        'data-slug': 'source'
                                    }))
    action_value = forms.ChoiceField(label=_("Service Chain Spec"),
                                     required=False,
                                     choices=[],
                                     widget=forms.Select(attrs={
                                         'class': 'switched',
                                         'data-switch-on': 'source',
                                         'data-source-redirect':
                                         _('Service Chain Spec')
                                     }))
    shared = forms.BooleanField(label=_("Shared"),
                                initial=False, required=False)

    def __init__(self, request, *args, **kwargs):
        super(AddPolicyActionForm, self).__init__(request, *args, **kwargs)
        url = reverse('horizon:project:application_policy:index')
        try:
            sc_specs = client.servicechainspec_list(request,
                tenant_id=request.user.tenant_id)
            self.fields['action_value'].choices = \
                [(spec.id,
                  (spec.name if spec.name is not None else "") + ":" + spec.id)
                 for spec in sc_specs]
        except Exception:
            exceptions.handle(
                request, _("Unable to retrieve action values."), redirect=url)

    def handle(self, request, context):
        url = reverse('horizon:project:application_policy:index')
        try:
            if not context['action_value']:
                del context['action_value']
            if context.get('name'):
                context['name'] = html.escape(context['name'])
            if context.get('description'):
                context['description'] = html.escape(context['description'])
            action = client.policyaction_create(request, **context)
            messages.success(request, _('Policy Action successfully created.'))
            return action
        except Exception:
            exceptions.handle(
                request, _("Unable to create policy action."), redirect=url)


class UpdatePolicyActionForm(BaseUpdateForm):
    name = forms.CharField(label=_("Name"))
    description = forms.CharField(label=_("Description"),
                                  required=False)
    shared = forms.BooleanField(label=_("Shared"), required=False)

    def __init__(self, request, *args, **kwargs):
        super(UpdatePolicyActionForm, self).__init__(request, *args, **kwargs)

        try:
            policyaction_id = self.initial['policyaction_id']
            pa = client.policyaction_get(request, policyaction_id)
            self.fields['name'].initial = pa.name
            self.fields['description'].initial = pa.description
            self.fields['shared'].initial = pa.shared
        except Exception:
            pass

    def handle(self, request, context):
        url = reverse('horizon:project:application_policy:index')
        try:
            policyaction_id = self.initial['policyaction_id']
            if context.get('name'):
                context['name'] = html.escape(context['name'])
            if context.get('description'):
                context['description'] = html.escape(context['description'])
            client.policyaction_update(request, policyaction_id, **context)
            messages.success(request, _('Policy Action successfully updated.'))
            return http.HttpResponseRedirect(url)
        except Exception:
            exceptions.handle(
                request, _("Unable to update policy action."), redirect=url)


class AddPolicyClassifierForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=80, label=_("Name"), required=False)
    description = forms.CharField(label=_("Description"), required=False)
    protocol = forms.CharField(required=True)
    port_range = forms.CharField(max_length=80, label=_("Port/Range(min:max)"),
                    required=False,
                    widget=forms.TextInput(attrs={'class': 'switched',
                                'data-switch-on': 'source',
                                'data-source-tcp': _("Port/Range(min:max)"),
                                'data-source-udp': _("Port/Range(min:max)"),
                                'data-source-http': _("Port/Range(min:max)"),
                                'data-source-https': _("Port/Range(min:max)"),
                                'data-source-smtp': _("Port/Range(min:max)"),
                                'data-source-dns': _("Port/Range(min:max)"),
                                'data-source-ftp': _("Port/Range(min:max)"),
                                'data-source-any': _("Port/Range(min:max)")}))
    direction = forms.ChoiceField(label=_("Direction"),
        choices=[('in', _('IN')),
                 ('out', _('OUT')),
                 ('bi', _('BI'))])
    shared = forms.BooleanField(label=_("Shared"),
                                initial=False, required=False)

    def __init__(self, request, *args, **kwargs):
        super(AddPolicyClassifierForm, self).__init__(request, *args, **kwargs)
        self.fields['protocol'].widget = fields.DropdownEditWidget(
            data_list=PROTOCOLS, name='list')

    def handle(self, request, context):
        url = reverse('horizon:project:application_policy:index')
        try:
            protocol = context.get('protocol').lower()
            if protocol in PROTOCOL_MAP:
                context['protocol'] = PROTOCOL_MAP[protocol]
            elif protocol == "any":
                del context['protocol']
            if not context.get('port_range'):
                context['port_range'] = None
            if context.get('name'):
                context['name'] = html.escape(context['name'])
            classifier = client.policyclassifier_create(request, **context)
            messages.success(
                request, _('Policy Classifier successfully created.'))
            return classifier
        except Exception:
            exceptions.handle(
                request, _("Unable to create policy classifier."),
                redirect=url)


class UpdatePolicyClassifierForm(BaseUpdateForm):
    name = forms.CharField(max_length=80, label=_("Name"), required=False)
    description = forms.CharField(label=_("Description"), required=False)
    protocol = forms.CharField(required=True)
    port_range = forms.CharField(max_length=80, label=_("Port/Range(min:max)"),
            required=False)
    direction = forms.ChoiceField(label=_("Direction"), choices=DIRECTIONS)
    shared = forms.BooleanField(label=_("Shared"), required=False)

    def __init__(self, request, *args, **kwargs):
        super(UpdatePolicyClassifierForm, self).__init__(
            request, *args, **kwargs)
        self.fields['protocol'].widget = fields.DropdownEditWidget(
            data_list=PROTOCOLS, name='list')
        try:
            policyclassifier_id = self.initial['policyclassifier_id']
            classifier = client.policyclassifier_get(
                request, policyclassifier_id)
            classifier = gfilters.update_classifier_attributes(classifier)
            for item in ['name', 'description',
                         'port_range', 'direction', 'shared']:
                self.fields[item].initial = getattr(classifier, item)
            protocol = getattr(classifier, "protocol")
            if protocol is not None:
                self.fields['protocol'].initial = protocol
            else:
                self.fields['protocol'].initial = "any"
        except Exception:
            exceptions.handle(
                request, _("Unable to retrive policy classifier details."))

    def handle(self, request, context):
        url = reverse('horizon:project:application_policy:index')
        try:
            policyclassifier_id = self.initial['policyclassifier_id']
            if 'protocol' in context:
                protocol = context.get('protocol').lower()
                if protocol in PROTOCOL_MAP:
                    context['protocol'] = PROTOCOL_MAP[protocol]
                elif protocol == "any":
                    context['protocol'] = None
            if 'port_range' in context and context['port_range'] == '':
                context['port_range'] = None
            if context.get('name'):
                context['name'] = html.escape(context['name'])
            if context.get('description'):
                context['description'] = html.escape(context['description'])
            client.policyclassifier_update(self.request,
                    policyclassifier_id, **context)
            messages.success(
                request, _('Policy classifier successfully updated.'))
            return http.HttpResponseRedirect(url)
        except Exception:
            exceptions.handle(
                request, _("Unable to update policy classifier."),
                redirect=url)


class UpdatePolicyRuleForm(BaseUpdateForm):
    name = forms.CharField(max_length=80, label=_("Name"), required=False)
    description = forms.CharField(label=_("Description"), required=False)
    policy_classifier_id = forms.ChoiceField(label=_("Policy Classifier"))
    policy_actions = fields.TransferTableField(
        label=_("Policy Actions"),
        required=False,
    )

    shared = forms.BooleanField(label=_("Shared"), required=False)

    def __init__(self, request, *args, **kwargs):
        super(UpdatePolicyRuleForm, self).__init__(request, *args, **kwargs)
        try:
            policyrule_id = self.initial['policyrule_id']
            rule = client.policyrule_get(request, policyrule_id)

            for item in ['name', 'description',
                         'policy_classifier_id', 'policy_actions', 'shared']:
                self.fields[item].initial = getattr(rule, item)

            actions = client.policyaction_list(request,
                tenant_id=request.user.tenant_id)
            for action in actions:
                action.set_id_as_name_if_empty()
            actions = sorted(actions, key=lambda action: action.name)
            action_list = [(a.id, a.name) for a in actions]
            self.fields['policy_actions'].choices = action_list

            classifiers = client.policyclassifier_list(request,
                tenant_id=request.user.tenant_id)
            classifier_list = [(c.id, c.name) for c in classifiers]
            self.fields['policy_classifier_id'].choices = classifier_list
        except Exception:
            exceptions.handle(
                request, _("Unable to retrive policy rule details."))

    def handle(self, request, context):
        url = reverse('horizon:project:application_policy:index')
        try:
            prid = self.initial['policyrule_id']
            if context.get('name'):
                context['name'] = html.escape(context['name'])
            if context.get('description'):
                context['description'] = html.escape(context['description'])
            client.policyrule_update(request, prid, **context)
            messages.success(request, _('Policy rule successfully updated.'))
            return http.HttpResponseRedirect(url)
        except Exception as e:
            msg = _("Unable to update policy rule. %s") % (str(e))
            exceptions.handle(request, msg, redirect=url)
