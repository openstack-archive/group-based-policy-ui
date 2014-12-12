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
from django import shortcuts
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms

from gbpui import client
from gbpui import fields

LOG = logging.getLogger(__name__)

NETWORK_PARAM_URL = "horizon:project:network_policy:add_network_service_param"


class AddL3PolicyForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=80, label=_("Name"))
    description = forms.CharField(
        max_length=80, label=_("Description"), required=False)
    ip_version = forms.ChoiceField(choices=[(4, 'IPv4'), (6, 'IPv6')],
                                   widget=forms.Select(attrs={
                                       'class': 'switchable',
                                       'data-slug': 'ipversion',
                                   }),
                                   label=_("IP Version"))
    ip_pool = forms.IPField(label=_("IP Pool"),
                            initial="",
                            help_text=_("Network address in CIDR format "
                                        "(e.g. 192.168.0.0/24,"
                                        "2001:DB8::/48)"),
                            version=forms.IPv4 | forms.IPv6,
                            mask=True)
    subnet_prefix_length = forms.CharField(max_length=80,
                                           label=_("Subnet Prefix Length"),
                                           help_text=_("Between 2 - 30 for IP4"
                                                       "and 2-127 for IP6."),)

    def __init__(self, request, *args, **kwargs):
        super(AddL3PolicyForm, self).__init__(request, *args, **kwargs)

    def clean(self):
        cleaned_data = super(AddL3PolicyForm, self).clean()
        if self.is_valid():
            ipversion = int(cleaned_data['ip_version'])
            subnet_prefix_length = int(cleaned_data['subnet_prefix_length'])
            msg = _("Subnet prefix out of range.")
            if ipversion == 4 and subnet_prefix_length not in range(2, 31):
                raise forms.ValidationError(msg)
            if ipversion == 6 and subnet_prefix_length not in range(2, 128):
                raise forms.ValidationError(msg)
        return cleaned_data

    def handle(self, request, context):
        url = reverse("horizon:project:network_policy:index")
        try:
            client.l3policy_create(request, **context)
            msg = _("L3 Policy Created Successfully!")
            LOG.debug(msg)
            return http.HttpResponseRedirect(url)
        except Exception:
            msg = _("Failed to create L3 policy.")
            LOG.error(msg)
            exceptions.handle(request, msg, redirect=shortcuts.redirect)


class UpdateL3PolicyForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=80, label=_("Name"))
    description = forms.CharField(
        max_length=80, label=_("Description"), required=False)
    ip_version = forms.ChoiceField(choices=[(4, 'IPv4'), (6, 'IPv6')],
                                   widget=forms.Select(attrs={
                                       'class': 'switchable',
                                       'data-slug': 'ipversion',
                                   }), label=_("IP Version"))
    ip_pool = forms.IPField(label=_("IP Pool"),
                            initial="",
                            help_text=_("Network address in CIDR format "
                                        "(e.g. 192.168.0.0/24,"
                                        "2001:DB8::/48)"),
                            version=forms.IPv4 | forms.IPv6,
                            mask=True)
    subnet_prefix_length = forms.CharField(max_length=80,
                                           label=_("Subnet Prefix Length"),
                                           help_text=_("Between 2-30 for IP4"
                                                       "and 2-127 for IP6."),)

    def __init__(self, request, *args, **kwargs):
        super(UpdateL3PolicyForm, self).__init__(request, *args, **kwargs)

    def clean(self):
        cleaned_data = super(UpdateL3PolicyForm, self).clean()
        if self.is_valid():
            ipversion = int(cleaned_data['ip_version'])
            subnet_prefix_length = int(cleaned_data['subnet_prefix_length'])
            msg = _("Subnet prefix out of range.")
            if ipversion == 4 and subnet_prefix_length not in range(2, 31):
                raise forms.ValidationError(msg)
            if ipversion == 6 and subnet_prefix_length not in range(2, 128):
                raise forms.ValidationError(msg)
        return cleaned_data

    def handle(self, request, context):
        url = reverse("horizon:project:network_policy:index")
        try:
            client.l3policy_create(request, **context)
            msg = _("L3 Policy Updated Successfully!")
            LOG.debug(msg)
            return http.HttpResponseRedirect(url)
        except Exception:
            msg = _("Failed to update L3 policy")
            LOG.error(msg)
            exceptions.handle(request, msg, redirect=shortcuts.redirect)


class AddL2PolicyForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=80, label=_("Name"), required=False)
    description = forms.CharField(
        max_length=80, label=_("Description"), required=False)
    l3_policy_id = forms.ChoiceField(label=_("L3 Policy"), required=False)
    allow_broadcast = forms.BooleanField(
        label=_("Allow Broadcast"), initial=True, required=False)

    def __init__(self, request, *args, **kwargs):
        super(AddL2PolicyForm, self).__init__(request, *args, **kwargs)
        try:
            policies = client.l3policy_list(request)
            policies = [(item['id'], item['name'] + ":" + item['id'])
                        for item in policies]
            self.fields['l3_policy_id'].choices = policies
        except Exception:
            msg = _("Failed to get L3 policy list")
            LOG.error(msg)
            exceptions.handle(request, msg, redirect=shortcuts.redirect)

    def handle(self, request, context):
        url = reverse("horizon:project:network_policy:index")
        try:
            del context['allow_broadcast']
            client.l2policy_create(request, **context)
            msg = _("L2 Policy Created Successfully!")
            LOG.debug(msg)
            return http.HttpResponseRedirect(url)
        except Exception:
            msg = _("Failed to create L2 policy")
            LOG.error(msg)
            exceptions.handle(request, msg, redirect=shortcuts.redirect)


class UpdateL2PolicyForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=80, label=_("Name"), required=False)
    description = forms.CharField(
        max_length=80, label=_("Description"), required=False)
    l3_policy_id = forms.ChoiceField(label=_("L3 Policy"), required=False)
    allow_broadcast = forms.BooleanField(
        label=_("Allow Broadcast"), required=False)

    def __init__(self, request, *args, **kwargs):
        super(UpdateL2PolicyForm, self).__init__(request, *args, **kwargs)
        try:
            l2policy_id = self.initial['l2policy_id']
            l2 = client.l2policy_get(request, l2policy_id)
            policies = client.l3policy_list(request)
            policies = [(item['id'], item['name'] + ":" + item['id'])
                        for item in policies]
            self.fields['l3_policy_id'].choices = policies
            for item in ['name', 'description', 'l3_policy_id']:
                self.fields[item].initial = getattr(l2, item)
        except Exception:
            msg = _("Failed to get L3 policy list")
            LOG.error(msg)
            exceptions.handle(request, msg, redirect=shortcuts.redirect)

    def handle(self, request, context):
        url = reverse("horizon:project:network_policy:l3policy_details",
                      kwargs={'l3policy_id': context['l3_policy_id']})
        l2policy_id = self.initial['l2policy_id']
        try:
            del context['allow_broadcast']
            client.l2policy_update(request, l2policy_id, **context)
            msg = _("L2 Policy Updated Successfully!")
            LOG.debug(msg)
            return http.HttpResponseRedirect(url)
        except Exception:
            msg = _("Failed to update L2 policy")
            LOG.error(msg)
            exceptions.handle(request, msg, redirect=shortcuts.redirect)


class CreateServicePolicyForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=80, label=_("Name"))
    description = forms.CharField(
        max_length=80, label=_("Description"), required=False)
    network_service_params = fields.CustomMultiChoiceField(label=_(
        "Network Service Parameters"), add_item_link=NETWORK_PARAM_URL,
        required=False)

    def handle(self, request, context):
        url = reverse("horizon:project:network_policy:index")
        try:
            params = context['network_service_params']
            p = []
            if len(params) > 0:
                for item in params:
                    values = [i.split(":")[1] for i in item.split(",")]
                    values = {'type': values[0],
                              'name': values[1],
                              'value': values[2]}
                    p.append(values)
            context['network_service_params'] = p
            client.create_networkservice_policy(request, **context)
            msg = _("Service policy created successfully!")
            LOG.debug(msg)
            return http.HttpResponseRedirect(url)
        except Exception as e:
            msg = _("Failed to create service policy. %s") % (str(e))
            LOG.error(msg)
            exceptions.handle(request, msg, redirect=url)


class NetworkServiceParam(object):

    def __init__(self, context):
        self.ptype = context['param_type']
        self.pname = context['param_name']
        self.pvalue = context['param_value']
        self.name = "Type:%s,Name:%s,Value:%s" % (
            self.ptype, self.pname, self.pvalue)
        self.id = self.name


class CreateNetworkServiceParamForm(forms.SelfHandlingForm):
    param_type = forms.ChoiceField(label=_("Type"),
                                   choices=[('ip_single', 'ip_single'),
                                            ('ip_pool', 'ip_pool'),
                                            ('string', 'string')])
    param_name = forms.CharField(max_length=80, label=_("Name"))
    param_value = forms.CharField(max_length=80, label=_("Value"),
            help_text=_("Enter a string. For Types 'ip_single' or 'ip_pool',"
                        "the Value is 'self_subnet' or 'external_subnet'."
                        "For Type 'string' the Value is a user-specified"
                        "string that matches the requirements published"
                        "by a Service Chain Spec."))

    def handle(self, request, context):
        return NetworkServiceParam(context)


class UpdateServicePolicyForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=80, label=_("Name"))
    description = forms.CharField(
        max_length=80, label=_("Description"), required=False)

    def __init__(self, request, *args, **kwargs):
        super(UpdateServicePolicyForm, self).__init__(request, *args, **kwargs)
        try:
            policy_id = self.initial['service_policy_id']
            policy = client.get_networkservice_policy(request, policy_id)
            self.fields['name'].initial = policy.name
            self.fields['description'].initial = policy.description
        except Exception as e:
            msg = _("Failed to retrive service policy details. %s") % (str(e))
            LOG.debug(msg)

    def handle(self, request, context):
        url = reverse("horizon:project:network_policy:index")
        try:
            policy_id = self.initial['service_policy_id']
            client.update_networkservice_policy(
                request, policy_id, **context)
            msg = _("Service policy updatedsuccessfully!")
            LOG.debug(msg)
            return http.HttpResponseRedirect(url)
        except Exception:
            msg = _("Failed to update service policy")
            LOG.error(msg)
            exceptions.handle(request, msg, redirect=shortcuts.redirect)
