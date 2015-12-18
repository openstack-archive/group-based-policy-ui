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
from django.utils import html
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages
from openstack_dashboard import api

from gbpui import client
from gbpui import fields

LOG = logging.getLogger(__name__)

EXT_SEG_PARAM_URL = "horizon:project:network_policy:add_external_segment_param"
NETWORK_PARAM_URL = "horizon:project:network_policy:add_network_service_param"
ROUTE_URL = "horizon:project:network_policy:add_external_route_param"


class BaseUpdateForm(forms.SelfHandlingForm):

    def clean(self):
        cleaned_data = super(BaseUpdateForm, self).clean()
        updated_data = {d: cleaned_data[d] for d in cleaned_data
            if d in self.changed_data}
        return updated_data


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
    external_segments = \
        fields.CustomMultiChoiceField(label=_("External Segments"),
                                      add_item_link=EXT_SEG_PARAM_URL,
                                      required=False)
    shared = forms.BooleanField(label=_("Shared"),
                                initial=False,
                                required=False)

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
        external_segment_dic = {}
        try:
            if context['external_segments']:
                dic = {}
                for external_segment in context['external_segments']:
                    values = [i.split(":")[1]
                        for i in external_segment.split(",")]
                    dic[values[0]] = [values[1]]
                    external_segment_dic.update(dic)
                context['external_segments'] = external_segment_dic
            else:
                context['external_segments'] = {}
            if context.get('name'):
                context['name'] = html.escape(context['name'])
            if context.get('description'):
                context['description'] = html.escape(context['description'])
            client.l3policy_create(request, **context)
            msg = _("L3 Policy Created Successfully!")
            LOG.debug(msg)
            return http.HttpResponseRedirect(url)
        except Exception as e:
            exceptions.handle(request, str(e), redirect=url)


class ExternalSegmentParam(object):

    def __init__(self, context):
        self.external_segment = context['external_segment']
        self.segment_ip = context['segment_ip']
        self.name = "ES:%s,IP:%s" % (
            self.external_segment, self.segment_ip)
        self.id = self.name


class CreateExternalSegmentParamForm(forms.SelfHandlingForm):
    external_segment = forms.ChoiceField(label=_("External Segment"),
                                          required=False)
    segment_ip = forms.IPField(label=_("External Segment IP"), initial="",
                               required=False)

    def __init__(self, request, *args, **kwargs):
        super(CreateExternalSegmentParamForm, self).__init__(request,
                                                             *args,
                                                             **kwargs)
        ec_list = client.externalconnectivity_list(request,
            tenant_id=request.user.tenant_id)
        external_segments_options = [(ec.id, ec.name) for ec in ec_list]
        self.fields['external_segment'].choices = external_segments_options

    def handle(self, request, context):
        return ExternalSegmentParam(context)


class UpdateL3PolicyForm(AddL3PolicyForm):
    def __init__(self, request, *args, **kwargs):
        super(UpdateL3PolicyForm, self).__init__(request, *args, **kwargs)
        try:
            l3policy_id = self.initial['l3policy_id']
            l3 = client.l3policy_get(request, l3policy_id)
            for item in ['name', 'description', 'ip_version',
                         'ip_pool', 'subnet_prefix_length']:
                self.fields[item].initial = str(l3[item])
            self.fields['shared'].initial = l3['shared']
            if bool(l3['external_segments']):
                es_choices = []
                es_initial = []
                for key, value in l3['external_segments'].items():
                    val = 'ES:' + key + ',IP:' + value[0]
                    es_choices.append((val, val))
                    es_initial.append(val)
                self.fields['external_segments'].choices = es_choices
                self.fields['external_segments'].initial = es_initial
        except Exception:
            msg = _("Failed to get L3 policy")
            LOG.error(msg)
            exceptions.handle(request, msg, redirect=shortcuts.redirect)

    def clean(self):
        external_segment_dict = {}
        cleaned_data = super(UpdateL3PolicyForm, self).clean()
        if self.is_valid():
            ipversion = int(cleaned_data['ip_version'])
            subnet_prefix_length = int(cleaned_data['subnet_prefix_length'])
            msg = _("Subnet prefix out of range.")
            if ipversion == 4 and subnet_prefix_length not in range(2, 31):
                raise forms.ValidationError(msg)
            if ipversion == 6 and subnet_prefix_length not in range(2, 128):
                raise forms.ValidationError(msg)
            if cleaned_data['external_segments']:
                dic = {}
                for external_segment in cleaned_data['external_segments']:
                    values = [i.split(":")[1]
                        for i in external_segment.split(",")]
                    dic[values[0]] = [values[1]]
                    external_segment_dict.update(dic)
                cleaned_data['external_segments'] = external_segment_dict
            else:
                cleaned_data['external_segments'] = {}
            updated_data = {d: cleaned_data[d] for d in cleaned_data
                if d in self.changed_data}
            cleaned_data = updated_data
        return cleaned_data

    def handle(self, request, context):
        url = reverse("horizon:project:network_policy:index")
        try:
            l3policy_id = self.initial['l3policy_id']
            if context.get('name'):
                context['name'] = html.escape(context['name'])
            if context.get('description'):
                context['description'] = html.escape(context['description'])
            client.l3policy_update(request, l3policy_id, **context)
            msg = _("L3 Policy Updated Successfully!")
            LOG.debug(msg)
            messages.success(request, msg)
            return http.HttpResponseRedirect(url)
        except Exception as e:
            exceptions.handle(request, str(e), redirect=url)


class AddL2PolicyForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=80, label=_("Name"), required=False)
    description = forms.CharField(
        max_length=80, label=_("Description"), required=False)
    l3_policy_id = forms.ChoiceField(label=_("L3 Policy"), required=False)
    inject_default_route = forms.BooleanField(label=_("Inject Default Route"),
                                initial=True,
                                required=False)

    def __init__(self, request, *args, **kwargs):
        super(AddL2PolicyForm, self).__init__(request, *args, **kwargs)
        try:
            policies = client.l3policy_list(request,
                tenant_id=request.user.tenant_id)
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
            if context.get('name'):
                context['name'] = html.escape(context['name'])
            if context.get('description'):
                context['description'] = html.escape(context['description'])
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
    inject_default_route = forms.BooleanField(label=_("Inject Default Route"),
                                required=False)

    def __init__(self, request, *args, **kwargs):
        super(UpdateL2PolicyForm, self).__init__(request, *args, **kwargs)
        try:
            l2policy_id = self.initial['l2policy_id']
            l2 = client.l2policy_get(request, l2policy_id)
            policies = client.l3policy_list(request,
                tenant_id=request.user.tenant_id)
            policies = [(item['id'], item['name'] + ":" + item['id'])
                        for item in policies]
            self.fields['l3_policy_id'].choices = policies
            for item in ['name', 'description', 'l3_policy_id',
                        'inject_default_route']:
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
            if context.get('name'):
                context['name'] = html.escape(context['name'])
            if context.get('description'):
                context['description'] = html.escape(context['description'])
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
    shared = forms.BooleanField(label=_("Shared"),
                                initial=False, required=False)

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
            if context.get('name'):
                context['name'] = html.escape(context['name'])
            if context.get('description'):
                context['description'] = html.escape(context['description'])
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
        self.pname = html.escape(context['param_name'])
        self.pvalue = html.escape(context['param_value'])
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


class UpdateServicePolicyForm(BaseUpdateForm):
    name = forms.CharField(max_length=80, label=_("Name"))
    description = forms.CharField(
        max_length=80, label=_("Description"), required=False)
    shared = forms.BooleanField(label=_("Shared"), required=False)

    def __init__(self, request, *args, **kwargs):
        super(UpdateServicePolicyForm, self).__init__(request, *args, **kwargs)
        try:
            policy_id = self.initial['service_policy_id']
            policy = client.get_networkservice_policy(request, policy_id)
            self.fields['name'].initial = policy.name
            self.fields['description'].initial = policy.description
            self.fields['shared'].initial = policy.shared
        except Exception as e:
            msg = _("Failed to retrive service policy details. %s") % (str(e))
            LOG.debug(msg)

    def handle(self, request, context):
        url = reverse("horizon:project:network_policy:index")
        try:
            policy_id = self.initial['service_policy_id']
            if context.get('name'):
                context['name'] = html.escape(context['name'])
            if context.get('description'):
                context['description'] = html.escape(context['description'])
            client.update_networkservice_policy(
                request, policy_id, **context)
            msg = _("Service policy updatedsuccessfully!")
            LOG.debug(msg)
            return http.HttpResponseRedirect(url)
        except Exception:
            msg = _("Failed to update service policy")
            LOG.error(msg)
            exceptions.handle(request, msg, redirect=shortcuts.redirect)


class CreateNATPoolForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=80, label=_("Name"))
    description = forms.CharField(
        max_length=80, label=_("Description"), required=False)
    ip_version = forms.ChoiceField(choices=[(4, 'IPv4'), (6, 'IPv6')],
                                   widget=forms.Select(attrs={
                                       'class': 'switchable',
                                       'data-slug': 'ipversion',
                                   }),
                                   label=_("IP Version"))
    ip_pool = forms.IPField(label=_("CIDR"),
                            initial="", required=True,
                            help_text=_("Network address in CIDR format "
                                        "(e.g. 192.168.0.0/24,"
                                        "2001:DB8::/48)"),
                            version=forms.IPv4 | forms.IPv6, mask=True)
    external_segment_id = forms.ChoiceField(label=_("External Segment"),
                                          required=True)
    shared = forms.BooleanField(label=_("Shared"),
                                initial=False, required=False)

    def __init__(self, request, *args, **kwargs):
        super(CreateNATPoolForm, self).__init__(request,
                                                *args,
                                                **kwargs)
        ec_list = client.externalconnectivity_list(request,
            tenant_id=request.user.tenant_id)
        external_segments_options = [(ec.id, ec.name) for ec in ec_list]
        self.fields['external_segment_id'].choices = external_segments_options

    def handle(self, request, context):
        url = reverse("horizon:project:network_policy:index")
        try:
            if context.get('name'):
                context['name'] = html.escape(context['name'])
            if context.get('description'):
                context['description'] = html.escape(context['description'])
            client.create_natpool(request, **context)
            msg = _("NAT Pool created successfully!")
            LOG.debug(msg)
            messages.success(request, msg)
            return http.HttpResponseRedirect(url)
        except Exception as e:
            msg = _("Failed to NAT Pool. %s") % (str(e))
            LOG.error(msg)
            exceptions.handle(request, msg, redirect=url)


class UpdateNATPoolForm(BaseUpdateForm):
    name = forms.CharField(max_length=80, label=_("Name"))
    description = forms.CharField(
        max_length=80, label=_("Description"), required=False)
    ip_version = forms.ChoiceField(choices=[(4, 'IPv4'), (6, 'IPv6')],
                                   widget=forms.Select(attrs={
                                       'class': 'switchable',
                                       'data-slug': 'ipversion',
                                   }),
                                   label=_("IP Version"))
    ip_pool = forms.IPField(label=_("CIDR"),
                            initial="", required=True,
                            help_text=_("Network address in CIDR format "
                                        "(e.g. 192.168.0.0/24,"
                                        "2001:DB8::/48)"),
                            version=forms.IPv4 | forms.IPv6, mask=True)
    external_segment_id = forms.ChoiceField(label=_("External Segment"),
                                          required=True)
    shared = forms.BooleanField(label=_("Shared"),
                                initial=False, required=False)

    def __init__(self, request, *args, **kwargs):
        super(UpdateNATPoolForm, self).__init__(request,
                                                *args,
                                                **kwargs)
        nat_pool_id = self.initial['nat_pool_id']
        ec_list = client.externalconnectivity_list(request,
            tenant_id=request.user.tenant_id)
        external_segments_options = [(ec.id, ec.name) for ec in ec_list]
        self.fields['external_segment_id'].choices = external_segments_options
        nat_pool = client.get_natpool(request, nat_pool_id)
        attributes = ['name', 'description',
                        'ip_version', 'ip_pool', 'external_segment_id']
        for attr in attributes:
            self.fields[attr].initial = str(nat_pool[attr])
        self.fields['shared'].initial = nat_pool['shared']

    def handle(self, request, context):
        url = reverse("horizon:project:network_policy:index")
        try:
            if context.get('name'):
                context['name'] = html.escape(context['name'])
            if context.get('description'):
                context['description'] = html.escape(context['description'])
            nat_pool_id = self.initial['nat_pool_id']
            client.update_natpool(
                request, nat_pool_id, **context)
            msg = _("NAT Pool updated successfully!")
            LOG.debug(msg)
            messages.success(request, msg)
            return http.HttpResponseRedirect(url)
        except Exception as e:
            msg = _("Failed to update NAT Pool.%s") % \
                (str(e))
            LOG.error(msg)
            exceptions.handle(request, msg, redirect=url)


class UpdateExternalConnectivityForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=80, label=_("Name"))
    description = forms.CharField(
        max_length=80, label=_("Description"), required=False)
    shared = forms.BooleanField(label=_("Shared"), required=False)

    def __init__(self, request, *args, **kwargs):
        super(UpdateExternalConnectivityForm, self).__init__(request,
            *args, **kwargs)
        try:
            external_connectivity_id = \
                self.initial['external_connectivity_id']
            external_connectivity = client.get_externalconnectivity(request,
                external_connectivity_id)
            self.fields['name'].initial = external_connectivity.name
            self.fields['description'].initial = \
                external_connectivity.description
            self.fields['shared'].initial = external_connectivity.shared
        except Exception as e:
            msg = _("Failed to retrive external connectivity details. %s") % \
                (str(e))
            LOG.debug(msg)

    def handle(self, request, context):
        url = reverse("horizon:project:network_policy:index")
        try:
            external_connectivity_id = self.initial['external_connectivity_id']
            client.update_externalconnectivity(
                request, external_connectivity_id, **context)
            msg = _("External Connectivity updated successfully!")
            LOG.debug(msg)
            return http.HttpResponseRedirect(url)
        except Exception as e:
            msg = _("Failed to update External Connectivity.%s") % \
                (str(e))
            LOG.error(msg)
            exceptions.handle(request, msg, redirect=shortcuts.redirect)


class CreateExternalConnectivityForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=80, label=_("Name"))
    description = forms.CharField(
        max_length=80, label=_("Description"), required=False)
    ip_version = forms.ChoiceField(choices=[(4, 'IPv4'), (6, 'IPv6')],
                                   widget=forms.Select(attrs={
                                       'class': 'switchable',
                                       'data-slug': 'ipversion',
                                   }),
                                   label=_("IP Version"))
    cidr = forms.IPField(label=_("CIDR"),
                            initial="", required=False,
                            help_text=_("Network address in CIDR format "
                                        "(e.g. 192.168.0.0/24,"
                                        "2001:DB8::/48)"),
                            version=forms.IPv4 | forms.IPv6, mask=True)
    external_routes = fields.CustomMultiChoiceField(
        label=_("External Routes"), add_item_link=ROUTE_URL,
        required=False)
    subnet_id = forms.ChoiceField(label=_("Subnet ID"), required=False)
    port_address_translation = forms.BooleanField(
        label=_("Port Address Translation"),
        initial=False, required=False)
    shared = forms.BooleanField(label=_("Shared"),
                                initial=False, required=False)

    def __init__(self, request, *args, **kwargs):
        super(CreateExternalConnectivityForm, self).__init__(request,
            *args, **kwargs)
        net_id_list = []
        dic = {"router:external": True}
        try:
            net_list = api.neutron.network_list(request, **dic)
            subnet_list = api.neutron.subnet_list(request)
            net_id_list = [net.id for net in net_list]
            self.fields['subnet_id'].choices = [('', 'Select')] + \
                [(subnet.id, subnet.name) for subnet in subnet_list
                if subnet.network_id in net_id_list]
        except Exception:
            msg = _("Failed to get Subnet ID list.")
            exceptions.handle(request, msg)

    def handle(self, request, context):
        try:
            if context['subnet_id'] == '':
                del context['subnet_id']
            if context['cidr'] == '':
                del context['cidr']
            routes = context['external_routes']
            p = []
            if len(routes) > 0:
                for item in routes:
                    values = [i.split(":")[1] for i in item.split(",")]
                    values = {'destination': values[0],
                              'nexthop': values[1]}
                    p.append(values)
            context['external_routes'] = p
            external_segment = client.create_externalconnectivity(
                request, **context)
            msg = _('External Connectivity successfully created.')
            LOG.debug(msg)
            messages.success(request, msg)
            return external_segment
        except Exception as e:
            msg = str(e)
            LOG.error(msg)
            exceptions.handle(request, msg, redirect=shortcuts.redirect)


class ExternalRouteParam(object):

    def __init__(self, context):
        self.destination = context['destination']
        self.next_hop = context['next_hop']
        self.name = 'destination:%s,next_hop:%s' % (
            self.destination, self.next_hop)
        self.id = self.name


class CreateExternalRouteParamForm(forms.SelfHandlingForm):
    destination = forms.IPField(label=_("Destination"),
                            initial="",
                            help_text=_(
                                "(e.g. 192.168.0.0/24,"
                                "2001:DB8::/48)"),
                            version=forms.IPv4 | forms.IPv6,
                            mask=True)
    next_hop = forms.IPField(label=_("Next hop"))

    def handle(self, request, context):
        return ExternalRouteParam(context)
