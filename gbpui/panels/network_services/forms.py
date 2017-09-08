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

import json
import logging

from django.core.urlresolvers import reverse
from django.utils import html
from django.utils.translation import ugettext_lazy as _

from django import http
from django import shortcuts

from horizon import exceptions
from horizon import forms
from horizon import messages

from gbpui import client

LOG = logging.getLogger(__name__)

SERVICE_TYPES = [('LOADBALANCER', 'Load Balancer'),
                 ('FIREWALL', 'Firewall')]


class BaseUpdateForm(forms.SelfHandlingForm):

    def clean(self):
        cleaned_data = super(BaseUpdateForm, self).clean()
        updated_data = {d: cleaned_data[d] for d in cleaned_data
            if d in self.changed_data or (d == 'nodes' and
                self.fields['nodes'].initial != cleaned_data[d])}
        return updated_data


class CreateServiceProfileForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=80, label=_("Name"))
    description = forms.CharField(
        max_length=80, label=_("Description"), required=False)
    vendor = forms.CharField(
        max_length=80, label=_("Vendor"), required=True)
    service_flavor = forms.CharField(
        max_length=80, label=_("Service Flavor"), required=False)
    service_type = forms.ChoiceField(
        label=_("Service Type"), choices=SERVICE_TYPES)
    insertion_mode = forms.ChoiceField(
        label=_("Insertion Mode"), choices=[('l3', 'L3'), ('l2', 'L2')])
    shared = forms.BooleanField(label=_("Shared"),
                                initial=False, required=False)

    def handle(self, request, context):
        url = reverse("horizon:project:network_services:index")
        try:
            if context.get('name'):
                context['name'] = html.escape(context['name'])
            if context.get('description'):
                context['description'] = html.escape(context['description'])
            if context.get('vendor'):
                context['vendor'] = html.escape(context['vendor'])
            if context.get('service_flavor'):
                context['service_flavor'] = html.escape(
                    context['service_flavor'])
            client.create_service_profile(request, **context)
            msg = _("Service Profile  Created Successfully")
            messages.success(request, msg)
            return http.HttpResponseRedirect(url)
        except Exception as e:
            msg = _("Failed to create Service Profile. %s") % (str(e))
            LOG.error(msg)
            exceptions.handle(request, msg, redirect=shortcuts.redirect)


class CreateServiceChainNodeForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=80, label=_("Name"))
    description = forms.CharField(
        max_length=80, label=_("Description"), required=False)
    service_profile_id = forms.ChoiceField(
        label=_("Service Profile"))
    config_type = forms.ChoiceField(label=_("Config Type"),
                                    choices=[('file', 'Heat Template'),
                                             ('string', 'Config String')],
                                    widget=forms.Select(attrs={'class':
                                                'switchable',
                                                'data-slug': 'source'}))
    template_file = forms.FileField(label=_('Configuration File'),
                        help_text=_('A local Heat template file to upload.'),
                        required=False,
                        widget=forms.FileInput(attrs={'class': 'switched',
                            'data-switch-on': 'source',
                            'data-source-file': _("Configuration File")}))
    template_string = forms.CharField(label=_("Configuration String"),
                          help_text=_('A local Heat template string.'),
                          widget=forms.Textarea(attrs={'class': 'switched',
                                                'data-switch-on': 'source',
                                                'data-source-string':
                                                _("Configuration String")}),
                                            required=False)
    shared = forms.BooleanField(label=_("Shared"),
                                initial=False, required=False)

    def __init__(self, request, *args, **kwargs):
        super(CreateServiceChainNodeForm, self).__init__(
            request, *args, **kwargs)
        try:
            service_profile_tuples = []
            service_profile_list = client.serviceprofile_list(self.request)
            for service_profile in service_profile_list:
                sp = (service_profile.id,
                service_profile.name + ' : ' + service_profile.service_type)
                service_profile_tuples.append(sp)
            self.fields['service_profile_id'].choices = service_profile_tuples
        except Exception:
            msg = _("Failed to retrive Service profile details.")
            LOG.error(msg)

    def clean(self):
        cleaned_data = super(CreateServiceChainNodeForm, self).clean()
        files = self.request.FILES
        template_str = None
        if 'template_file' in files:
            temp = files['template_file'].read()
            try:
                template_str = json.loads(temp)
            except Exception:
                msg = _('Invalid file format.')
                raise forms.ValidationError(msg)
        else:
            try:
                tstr = cleaned_data["template_string"]
                if bool(tstr):
                    template_str = json.loads(tstr)
            except Exception:
                msg = _("Invalid template string.")
                raise forms.ValidationError(msg)
        if template_str is not None:
            cleaned_data['config'] = template_str
        else:
            msg = _("Please choose a template file or enter template string.")
            raise forms.ValidationError(msg)
        return cleaned_data

    def handle(self, request, context):
        url = reverse("horizon:project:network_services:index")
        try:
            try:
                del context['template_string']
                del context['template_file']
                del context['config_type']
            except KeyError:
                pass
            context['config'] = json.dumps(context['config'])
            if context.get('name'):
                context['name'] = html.escape(context['name'])
            if context.get('description'):
                context['description'] = html.escape(context['description'])
            client.create_servicechain_node(request, **context)
            msg = _("Service Chain Node Created Successfully!")
            LOG.debug(msg)
            return http.HttpResponseRedirect(url)
        except Exception as e:
            msg = _("Failed to create Service Chain Node. %s") % (str(e))
            LOG.error(msg)
            exceptions.handle(request, msg, redirect=shortcuts.redirect)


class UpdateServiceChainNodeForm(BaseUpdateForm):
    name = forms.CharField(max_length=80, label=_("Name"))
    description = forms.CharField(
        max_length=80, label=_("Description"), required=False)
    shared = forms.BooleanField(label=_("Shared"), required=False)

    def __init__(self, request, *args, **kwargs):
        super(UpdateServiceChainNodeForm, self).__init__(
            request, *args, **kwargs)
        try:
            scnode_id = self.initial['scnode_id']
            scnode = client.get_servicechain_node(request, scnode_id)
            for item in ['name', 'description', 'shared']:
                self.fields[item].initial = getattr(scnode, item)
        except Exception:
            msg = _("Failed to retrive Service Chain Node details.")
            LOG.error(msg)

    def handle(self, request, context):
        url = reverse("horizon:project:network_services:index")
        try:
            scnode_id = self.initial['scnode_id']
            if context.get('name'):
                context['name'] = html.escape(context['name'])
            if context.get('description'):
                context['description'] = html.escape(context['description'])
            client.update_servicechain_node(
                request, scnode_id, **context)
            msg = _("Service Chain Node Updated Successfully!")
            LOG.debug(msg)
            messages.success(request, msg)
            return http.HttpResponseRedirect(url)
        except Exception as e:
            msg = _("Failed to create Service Chain Node.  %s") % (str(e))
            LOG.error(msg)
            exceptions.handle(request, msg, redirect=url)


class CreateServiceChainSpecForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=255, label=_("Name"))
    description = forms.CharField(
        max_length=80, label=_("Description"), required=False)
    shared = forms.BooleanField(label=_("Shared"),
                                initial=False, required=False)
    nodes = forms.MultipleChoiceField(label=_("Nodes"),
                                        widget=forms.CheckboxSelectMultiple(),
                                        error_messages={
                                            'required': _(
                                                "At least one node must"
                                                " be specified.")},
                              help_text=_("Create service chain spec with"
                                                    " these nodes"))

    def __init__(self, request, *args, **kwargs):
        super(CreateServiceChainSpecForm, self).__init__(
            request, *args, **kwargs)
        try:
            node_list = []
            nodes = client.servicechainnode_list(request,
                tenant_id=request.user.tenant_id)
            for n in nodes:
                n.set_id_as_name_if_empty()
                node_list.append((n.id, n.name))
            self.fields['nodes'].choices = sorted(
                node_list, key=lambda obj: obj[1])
        except Exception:
            msg = _("Failed to retrieve service chain spec")
            LOG.error(msg)
            exceptions.handle(request, msg, redirect=shortcuts.redirect)

    def handle(self, request, context):
        url = reverse("horizon:project:network_services:index")
        try:
            if context.get('name'):
                context['name'] = html.escape(context['name'])
            if context.get('description'):
                context['description'] = html.escape(context['description'])
            client.create_servicechain_spec(request, **context)
            msg = _("Service Chain Spec Created Successfully!")
            LOG.debug(msg)
            messages.success(request, msg)
            return http.HttpResponseRedirect(url)
        except Exception as e:
            msg = _("Failed to create Service Chain Spec.  %s") % (str(e))
            LOG.error(msg)
            exceptions.handle(request, msg, redirect=url)


class UpdateServiceChainSpecForm(CreateServiceChainSpecForm, BaseUpdateForm):

    def __init__(self, request, *args, **kwargs):
        super(UpdateServiceChainSpecForm, self).__init__(
            request, *args, **kwargs)
        try:
            scspec_id = self.initial['scspec_id']
            scspec = client.get_servicechain_spec(request, scspec_id)
            for attr in ['name', 'description', 'nodes', 'shared']:
                self.fields[attr].initial = getattr(scspec, attr)
            nodes_available = dict(self.fields['nodes'].choices)
            nodes_selected = [
                (x, nodes_available[x]) for x in self.fields['nodes'].initial]
            nodes_unselected = set(self.fields['nodes'].choices) - set(
                nodes_selected)
            self.fields['nodes'].choices = nodes_selected + list(
                nodes_unselected)
        except Exception:
            msg = _("Failed to retrieve service chain spec")
            LOG.error(msg)

    def handle(self, request, context):
        url = reverse("horizon:project:network_services:index")
        try:
            scspec_id = self.initial['scspec_id']
            if context.get('name'):
                context['name'] = html.escape(context['name'])
            if context.get('description'):
                context['description'] = html.escape(context['description'])
            client.update_servicechain_spec(request, scspec_id, **context)
            msg = _("Service Chain Spec Updated Successfully!")
            LOG.debug(msg)
            messages.success(request, msg)
            return http.HttpResponseRedirect(url)
        except Exception as e:
            msg = _("Failed to update Service Chain Spec.  %s") % (str(e))
            LOG.error(msg)
            exceptions.handle(request, msg, redirect=shortcuts.redirect)
