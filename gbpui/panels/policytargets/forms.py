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

from django.core.urlresolvers import reverse
from django import http
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from gbpui import client

LOG = logging.getLogger(__name__)


class UpdatePolicyTargetForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=80,
                           label=_("Name"), required=False)
    description = forms.CharField(max_length=80,
                                  label=_("Description"), required=False)
    provided_policy_rule_sets = forms.MultipleChoiceField(
        label=_("Provided Policy Rule Set"), required=False)
    consumed_policy_rule_sets = forms.MultipleChoiceField(
        label=_("Consumed Policy Rule Set"), required=False)
    l2_policy_id = forms.ChoiceField(
        label=_("Network Policy"),
        required=False,
        help_text=_("Select network policy for Group."))
    network_service_policy_id = forms.ChoiceField(
        label=_("Network Services Policy"),
        required=False,
        help_text=_("Select network services policy for Group."))
    failure_url = 'horizon:project:policytargets:index'

    def __init__(self, request, *args, **kwargs):
        super(UpdatePolicyTargetForm, self).__init__(request, *args, **kwargs)
        try:
            policy_target_id = self.initial['policy_target_id']
            policy_target = client.policy_target_get(request, policy_target_id)
            policy_rule_sets = client.policy_rule_set_list(request)
            for c in policy_rule_sets:
                c.set_id_as_name_if_empty()
            policy_rule_sets = sorted(
                policy_rule_sets, key=lambda rule: rule.name)
            policy_rule_set_list = [(c.id, c.name) for c in policy_rule_sets]
            self.fields[
                'provided_policy_rule_sets'].choices = policy_rule_set_list
            self.fields[
                'consumed_policy_rule_sets'].choices = policy_rule_set_list
            provided_init = []
            consumed_init = []
            for item in policy_rule_set_list:
                if item[0] in policy_target.provided_policy_rule_sets:
                    provided_init.append(item[0])
                if item[0] in policy_target.consumed_policy_rule_sets:
                    consumed_init.append(item[0])
            self.fields['provided_policy_rule_sets'].initial = provided_init
            self.fields['consumed_policy_rule_sets'].initial = consumed_init
            n_policies = client.l2policy_list(request)
            ns_policies = client.networkservicepolicy_list(request)
            n_policies = [(item.id, item.name) for item in n_policies]
            ns_policies = [(item.id, item.name) for item in ns_policies]
            ns_policies.insert(0, ('None', 'None'))
            self.fields['l2_policy_id'].choices = n_policies
            self.fields['network_service_policy_id'].choices = ns_policies
            for i in ['name',
                      'description',
                      'l2_policy_id',
                      'network_service_policy_id']:
                self.fields[i].initial = getattr(policy_target, i)
        except Exception as e:
            msg = _('Unable to retrieve policy_rule_set details. %s') % (
                str(e))
            exceptions.handle(request, msg)
            pass

    def handle(self, request, context):
        policy_target_id = self.initial['policy_target_id']
        name_or_id = context.get('name') or policy_target_id
        try:
            context['provided_policy_rule_sets'] = dict(
                [(i, 'string') for i in context['provided_policy_rule_sets']])
            context['consumed_policy_rule_sets'] = dict(
                [(i, 'string') for i in context['consumed_policy_rule_sets']])
            if context['network_service_policy_id'] == 'None':
                context['network_service_policy_id'] = None
            policy_target = client.policy_target_update(
                request, policy_target_id, **context)
            msg = _('Group %s was successfully updated.') % name_or_id
            LOG.debug(msg)
            messages.success(request, msg)
            return policy_target
        except Exception as e:
            msg = _('Failed to update Group %(name)s. %(reason)s') % {'name':
                    name_or_id, 'reason': str(e)}
            LOG.error(msg)
            redirect = reverse(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)


class AddProvidedPRSForm(forms.SelfHandlingForm):
    policy_rule_set = forms.MultipleChoiceField(
        label=_("Provided Policy Rule Sets"),)

    def __init__(self, request, *args, **kwargs):
        super(AddProvidedPRSForm, self).__init__(request, *args, **kwargs)
        policy_rule_sets = []
        try:
            policy_target_id = kwargs['initial']['policy_target_id']
            policy_target = client.policy_target_get(request, policy_target_id)
            providedpolicy_rule_sets = policy_target.get(
                "provided_policy_rule_sets")
            items = client.policy_rule_set_list(request)
            policy_rule_sets = [
                (p.id, p.name) for p in items
                if p.id not in providedpolicy_rule_sets]
        except Exception as e:
            msg = _('Unable to retrieve policy rule set list.') % (str(e))
            LOG.debug(msg)
        self.fields['policy_rule_set'].choices = policy_rule_sets

    def handle(self, request, context):
        policy_target_id = self.initial['policy_target_id']
        policy_target = client.policy_target_get(request, policy_target_id)
        url = reverse("horizon:project:policytargets:policy_targetdetails",
                      kwargs={'policy_target_id': policy_target_id})
        try:
            for policy_rule_set in policy_target.get(
                    "provided_policy_rule_sets"):
                context['policy_rule_set'].append(policy_rule_set)
            policy_rule_sets = dict([(item, 'string')
                                     for item in context['policy_rule_set']])
            client.policy_target_update(
                request, policy_target_id,
                provided_policy_rule_sets=policy_rule_sets)
            msg = _('Policy Rule Set added successfully!')
            messages.success(request, msg)
            LOG.debug(msg)
            return http.HttpResponseRedirect(url)
        except Exception:
            u = "horizon:project:policytargets:policy_targetdetails"
            msg = _('Failed to add policy_rule_set!')
            redirect = reverse(u, kwargs={'policy_target_id':
                                          policy_target_id})
            LOG.error(msg)
            exceptions.handle(request, msg, redirect=redirect)


class RemoveProvidedPRSForm(forms.SelfHandlingForm):
    policy_rule_set = forms.MultipleChoiceField(
        label=_("Provided Policy Rule Sets"),)

    def __init__(self, request, *args, **kwargs):
        super(RemoveProvidedPRSForm, self).__init__(request, *args, **kwargs)
        policy_rule_sets = []
        try:
            policy_target_id = kwargs['initial']['policy_target_id']
            policy_target = client.policy_target_get(request, policy_target_id)
            providedpolicy_rule_sets = policy_target.get(
                "provided_policy_rule_sets")
            items = client.policy_rule_set_list(request)
            policy_rule_sets = [(p.id, p.name)
                                for p in items if p.id in
                                providedpolicy_rule_sets]
        except Exception as e:
            msg = _('Unable to retrieve policy rule set list.') % (str(e))
            LOG.debug(msg)
        self.fields['policy_rule_set'].choices = policy_rule_sets

    def handle(self, request, context):
        policy_target_id = self.initial['policy_target_id']
        url = reverse("horizon:project:policytargets:policy_targetdetails",
                      kwargs={'policy_target_id': policy_target_id})
        try:
            policy_target = client.policy_target_get(request, policy_target_id)
            old_policy_rule_sets = policy_target.get(
                "provided_policy_rule_sets")
            for policy_rule_set in context['policy_rule_set']:
                old_policy_rule_sets.remove(policy_rule_set)
            policy_rule_sets = dict([(item, 'string')
                                     for item in old_policy_rule_sets])
            client.policy_target_update(
                request, policy_target_id,
                provided_policy_rule_sets=policy_rule_sets)
            msg = _('Policy Rule Set removed successfully!')
            messages.success(request, msg)
            LOG.debug(msg)
            return http.HttpResponseRedirect(url)
        except Exception:
            msg = _('Failed to remove policy_rule_set!')
            u = "horizon:project:policytargets:policy_targetdetails"
            redirect = reverse(u,
                               kwargs={'policy_target_id': policy_target_id})
            LOG.error(msg)
            exceptions.handle(request, msg, redirect=redirect)


class AddConsumedPRSForm(forms.SelfHandlingForm):
    policy_rule_set = forms.MultipleChoiceField(
        label=_("Consumed Policy Rule Sets"),)

    def __init__(self, request, *args, **kwargs):
        super(AddConsumedPRSForm, self).__init__(request, *args, **kwargs)
        policy_rule_sets = []
        try:
            policy_target_id = kwargs['initial']['policy_target_id']
            policy_target = client.policy_target_get(request, policy_target_id)
            consumedpolicy_rule_sets = policy_target.get(
                "consumed_policy_rule_sets")
            items = client.policy_rule_set_list(request)
            policy_rule_sets = [
                (p.id, p.name) for p in items
                if p.id not in consumedpolicy_rule_sets]
        except Exception:
            pass
        self.fields['policy_rule_set'].choices = policy_rule_sets

    def handle(self, request, context):
        policy_target_id = self.initial['policy_target_id']
        url = reverse("horizon:project:policytargets:policy_targetdetails",
                      kwargs={'policy_target_id': policy_target_id})
        try:
            policy_target = client.policy_target_get(request, policy_target_id)
            for policy_rule_set in policy_target.get(
                    "consumed_policy_rule_sets"):
                context['policy_rule_set'].append(policy_rule_set)
            consumed = dict([(item, 'string')
                             for item in context['policy_rule_set']])
            client.policy_target_update(
                request, policy_target_id, consumed_policy_rule_sets=consumed)
            msg = _('Policy Rule Set Added successfully!')
            messages.success(request, msg)
            LOG.debug(msg)
            return http.HttpResponseRedirect(url)
        except Exception:
            msg = _('Failed to add policy_rule_set!')
            u = "horizon:project:policytargets:policy_targetdetails"
            redirect = reverse(u,
                               kwargs={'policy_target_id': policy_target_id})
            LOG.error(msg)
            exceptions.handle(request, msg, redirect=redirect)


class RemoveConsumedPRSForm(forms.SelfHandlingForm):
    policy_rule_set = forms.MultipleChoiceField(
        label=_("Consumed Policy Rule Sets"),)

    def __init__(self, request, *args, **kwargs):
        super(RemoveConsumedPRSForm, self).__init__(request, *args, **kwargs)
        policy_rule_sets = []
        try:
            policy_target_id = kwargs['initial']['policy_target_id']
            policy_target = client.policy_target_get(request, policy_target_id)
            consumedpolicy_rule_sets = policy_target.get(
                "consumed_policy_rule_sets")
            items = client.policy_rule_set_list(request)
            policy_rule_sets = [(p.id, p.name)
                                for p in items if p.id
                                in consumedpolicy_rule_sets]
        except Exception:
            pass
        self.fields['policy_rule_set'].choices = policy_rule_sets

    def handle(self, request, context):
        policy_target_id = self.initial['policy_target_id']
        url = reverse("horizon:project:policytargets:policy_targetdetails",
                      kwargs={'policy_target_id': policy_target_id})
        try:
            policy_target = client.policy_target_get(request, policy_target_id)
            old_policy_rule_sets = policy_target.get(
                "consumed_policy_rule_sets")
            for policy_rule_set in context['policy_rule_set']:
                old_policy_rule_sets.remove(policy_rule_set)
            consumed = dict([(item, 'string')
                             for item in old_policy_rule_sets])
            client.policy_target_update(
                request, policy_target_id, consumed_policy_rule_sets=consumed)
            msg = _('Policy Rule Set removed successfully!')
            messages.success(request, msg)
            LOG.debug(msg)
            return http.HttpResponseRedirect(url)
        except Exception:
            msg = _('Failed to remove policy_rule_set!')
            redirect = url
            LOG.error(msg)
            exceptions.handle(request, msg, redirect=redirect)
