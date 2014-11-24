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
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_variables  # noqa

from horizon import exceptions
from horizon import forms
from horizon import messages

from gbpui import client

PROTOCOLS = [('tcp', _('TCP')),
             ('udp', _('UDP')),
             ('icmp', _('ICMP')),
             ('http', _('HTTP')),
             ('https', _('HTTPS')),
             ('smtp', _('SMTP')),
             ('dns', _('DNS')),
             ('ftp', _('FTP')),
             ('any', _('ANY'))
             ]
DIRECTIONS = [('in', _('IN')),
              ('out', _('OUT')),
              ('bi', _('BI'))]
POLICY_ACTION_TYPES = [('allow', _('ALLOW')),
                       ('redirect', _('REDIRECT')),
                       ('copy', _('COPY')),
                       ('log', _('LOG')),
                       ('qos', _('QoS'))]


class UpdatePolicyRuleSetForm(forms.SelfHandlingForm):
    name = forms.CharField(label=_("Name"))
    description = forms.CharField(label=_("Description"), required=False)
    rules = forms.MultipleChoiceField(label=_("Policy Rules"),)

    def __init__(self, request, *args, **kwargs):
        super(UpdatePolicyRuleSetForm, self).__init__(request, *args, **kwargs)
        rules = []
        try:
            items = client.policyrule_list(request)
            rules = [(p.id, p.name) for p in items]
            policy_rule_set = client.policy_rule_set_get(
                request, self.initial['policy_rule_set_id'])
            if policy_rule_set:
                self.fields['name'].initial = policy_rule_set.name
                self.fields[
                    'description'].initial = policy_rule_set.description
                existing = [item for item in policy_rule_set.policy_rules]
                self.fields['rules'].initial = existing
        except Exception:
            exceptions.handle(request, _('Unable to retrieve policy rules'))
        self.fields['rules'].choices = rules

    def handle(self, request, context):
        try:
            policy_rule_set_id = self.initial['policy_rule_set_id']
            client.policy_rule_set_update(request,
                                          policy_rule_set_id,
                                          name=context['name'],
                                          description=context[
                                              'description'],
                                          policy_rules=context['rules'],
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
            action = client.policyaction_create(request, **context)
            messages.success(request, _('Policy Action successfully created.'))
            return action
        except Exception:
            exceptions.handle(
                request, _("Unable to create policy action."), redirect=url)


class UpdatePolicyActionForm(forms.SelfHandlingForm):
    name = forms.CharField(label=_("Name"))
    description = forms.CharField(label=_("Description"),
                                  required=False)

    def __init__(self, request, *args, **kwargs):
        super(UpdatePolicyActionForm, self).__init__(request, *args, **kwargs)

        try:
            policyaction_id = self.initial['policyaction_id']
            pa = client.policyaction_get(request, policyaction_id)
            self.fields['name'].initial = pa.name
            self.fields['description'].initial = pa.description
        except Exception:
            pass

    def handle(self, request, context):
        url = reverse('horizon:project:application_policy:index')
        try:
            policyaction_id = self.initial['policyaction_id']
            client.policyaction_update(request, policyaction_id, **context)
            messages.success(request, _('Policy Action successfully updated.'))
            return http.HttpResponseRedirect(url)
        except Exception:
            exceptions.handle(
                request, _("Unable to update policy action."), redirect=url)


class AddPolicyClassifierForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=80, label=_("Name"), required=False)
    protocol = forms.ChoiceField(label=_("Protocol"), choices=PROTOCOLS,
                widget=forms.Select(attrs={'class': 'switchable',
                                           'data-slug': 'source'}))
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

    def __init__(self, request, *args, **kwargs):
        super(AddPolicyClassifierForm, self).__init__(request, *args, **kwargs)

    def handle(self, request, context):
        url = reverse('horizon:project:application_policy:index')
        try:
            if not bool(context['port_range']):
                context['port_range'] = None
            classifier = client.policyclassifier_create(request, **context)
            messages.success(
                request, _('Policy Classifier successfully created.'))
            return classifier
        except Exception:
            exceptions.handle(
                request, _("Unable to create policy classifier."),
                redirect=url)


class UpdatePolicyClassifierForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=80, label=_("Name"), required=False)
    description = forms.CharField(label=_("Description"), required=False)
    protocol = forms.ChoiceField(label=_("Protocol"), choices=PROTOCOLS)
    port_range = forms.CharField(max_length=80, label=_("Port/Range(min:max)"),
            required=False)
    direction = forms.ChoiceField(label=_("Direction"), choices=DIRECTIONS)

    def __init__(self, request, *args, **kwargs):
        super(UpdatePolicyClassifierForm, self).__init__(
            request, *args, **kwargs)
        try:
            policyclassifier_id = self.initial['policyclassifier_id']
            classifier = client.policyclassifier_get(
                request, policyclassifier_id)
            for item in ['name', 'description',
                         'protocol', 'port_range', 'direction']:
                self.fields[item].initial = getattr(classifier, item)
        except Exception:
            exceptions.handle(
                request, _("Unable to retrive policy classifier details."))

    def handle(self, request, context):
        url = reverse('horizon:project:application_policy:index')
        try:
            policyclassifier_id = self.initial['policyclassifier_id']
            if not bool(context['port_range']):
                context['port_range'] = None
            client.policyclassifier_update(self.request,
                    policyclassifier_id, **context)
            messages.success(
                request, _('Policy classifier successfully updated.'))
            return http.HttpResponseRedirect(url)
        except Exception:
            exceptions.handle(
                request, _("Unable to update policy classifier."),
                redirect=url)


class UpdatePolicyRuleForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=80, label=_("Name"), required=False)
    description = forms.CharField(label=_("Description"), required=False)
    policy_classifier_id = forms.ChoiceField(label=_("Policy Classifier"))
    policy_actions = forms.MultipleChoiceField(label=_("Policy Actions"))

    def __init__(self, request, *args, **kwargs):
        super(UpdatePolicyRuleForm, self).__init__(request, *args, **kwargs)
        try:
            tenant_id = request.user.tenant_id
            policyrule_id = self.initial['policyrule_id']
            rule = client.policyrule_get(request, policyrule_id)
            for item in ['name', 'description',
                         'policy_classifier_id', 'policy_actions']:
                self.fields[item].initial = getattr(rule, item)
            actions = client.policyaction_list(request, tenant_id=tenant_id)
            action_list = [a.id for a in actions]
            for action in actions:
                action.set_id_as_name_if_empty()
            actions = sorted(actions, key=lambda action: action.name)
            action_list = [(a.id, a.name) for a in actions]
            self.fields['policy_actions'].choices = action_list
            classifiers = client.policyclassifier_list(
                request, tenant_id=tenant_id)
            classifier_list = [(c.id, c.name) for c in classifiers]
            self.fields['policy_classifier_id'].choices = classifier_list
        except Exception:
            exceptions.handle(
                request, _("Unable to retrive policy rule details."))

    def handle(self, request, context):
        url = reverse('horizon:project:application_policy:index')
        try:
            prid = self.initial['policyrule_id']
            client.policyrule_update(request, prid, **context)
            messages.success(request, _('Policy rule successfully updated.'))
            return http.HttpResponseRedirect(url)
        except Exception as e:
            msg = _("Unable to update policy rule. %s") % (str(e))
            exceptions.handle(request, msg, redirect=url)
