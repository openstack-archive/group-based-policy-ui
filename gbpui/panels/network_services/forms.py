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
from django.utils.translation import ugettext_lazy as _

from django import http
from django import shortcuts

from horizon import exceptions
from horizon import forms


from gbpui import client

LOG = logging.getLogger(__name__)

SERVICE_TYPES = [('LOADBALANCER', 'Load Balancer'),
                 ('FIREWALL', 'Firewall')]


class CreateServiceChainNodeForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=80, label=_("Name"))
    description = forms.CharField(
        max_length=80, label=_("Description"), required=False)
    service_type = forms.ChoiceField(
        label=_("Service Type"), choices=SERVICE_TYPES)
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
            client.create_servicechain_node(request, **context)
            msg = _("Service Chain Node Created Successfully!")
            LOG.debug(msg)
            return http.HttpResponseRedirect(url)
        except Exception as e:
            msg = _("Failed to create Service Chain Node. %s") % (str(e))
            LOG.error(msg)
            exceptions.handle(request, msg, redirect=shortcuts.redirect)


class UpdateServiceChainNodeForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=80, label=_("Name"))
    description = forms.CharField(
        max_length=80, label=_("Description"), required=False)

    def __init__(self, request, *args, **kwargs):
        super(UpdateServiceChainNodeForm, self).__init__(
            request, *args, **kwargs)
        try:
            scnode_id = self.initial['scnode_id']
            scnode = client.get_servicechain_node(request, scnode_id)
            for item in ['name', 'description']:
                self.fields[item].initial = getattr(scnode, item)
        except Exception:
            msg = _("Failed to retrive Service Chain Node details.")
            LOG.error(msg)

    def handle(self, request, context):
        url = reverse("horizon:project:network_services:index")
        try:
            scnode_id = self.initial['scnode_id']
            client.update_servicechain_node(
                request, scnode_id, **context)
            msg = _("Service Chain Node Created Successfully!")
            LOG.debug(msg)
            return http.HttpResponseRedirect(url)
        except Exception as e:
            msg = _("Failed to create Service Chain Node.  %s") % (str(e))
            LOG.error(msg)
            exceptions.handle(request, msg, redirect=url)


class CreateServiceChainSpecForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=80, label=_("Name"))
    description = forms.CharField(
        max_length=80, label=_("Description"), required=False)
    nodes = forms.MultipleChoiceField(label=_("Nodes"))

    def __init__(self, request, *args, **kwargs):
        super(CreateServiceChainSpecForm, self).__init__(
            request, *args, **kwargs)
        try:
            nodes = client.servicechainnode_list(request)
            nodes = [(item.id, item.name + ":" + str(item.id))
                     for item in nodes]
            self.fields['nodes'].choices = nodes
        except Exception:
            msg = _("Failed to retrive service chain nodes.")
            LOG.error(msg)
            exceptions.handle(request, msg, redirect=shortcuts.redirect)

    def handle(self, request, context):
        url = reverse("horizon:project:network_services:index")
        try:
            client.create_servicechain_spec(request, **context)
            msg = _("Service Chain Spec Created Successfully!")
            LOG.debug(msg)
            return http.HttpResponseRedirect(url)
        except Exception as e:
            msg = _("Failed to create Service Chain Spec.  %s") % (str(e))
            LOG.error(msg)
            exceptions.handle(request, msg, redirect=url)


class UpdateServiceChainSpecForm(CreateServiceChainSpecForm):

    def __init__(self, request, *args, **kwargs):
        super(UpdateServiceChainSpecForm, self).__init__(
            request, *args, **kwargs)
        try:
            scspec_id = self.initial['scspec_id']
            scspec = client.get_servicechain_spec(request, scspec_id)
            for attr in ['name', 'description', 'nodes']:
                self.fields[attr].initial = getattr(scspec, attr)
        except Exception:
            pass

    def handle(self, request, context):
        url = reverse("horizon:project:network_services:index")
        try:
            scspec_id = self.initial['scspec_id']
            client.update_servicechain_spec(request, scspec_id, **context)
            msg = _("Service Chain Spec Created Successfully!")
            LOG.debug(msg)
            return http.HttpResponseRedirect(url)
        except Exception as e:
            msg = _("Failed to create Service Chain Spec.  %s") % (str(e))
            LOG.error(msg)
            exceptions.handle(request, msg, redirect=shortcuts.redirect)


class CreateServiceChainInstanceForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=80, label=_("Name"))
    description = forms.CharField(
        max_length=80, label=_("Description"), required=False)
    servicechain_spec = forms.ChoiceField(label=_("ServiceChain Spec"))
    provider_ptg = forms.ChoiceField(label=_("Provider PTG"))
    consumer_ptg = forms.ChoiceField(label=_("Consumer PTG"))
    classifier = forms.ChoiceField(label=_("Classifier"))

    def __init__(self, request, *args, **kwargs):
        super(CreateServiceChainInstanceForm, self).__init__(
            request, *args, **kwargs)
        try:
            sc_specs = client.servicechainspec_list(request)
            ptgs = client.policy_target_list(request)
            ptgs = [(item.id, item.name) for item in ptgs]
            classifiers = client.policyclassifier_list(request)
            self.fields['servicechain_spec'].choices = [
                (item.id, item.name) for item in sc_specs]
            self.fields['provider_ptg'].choices = ptgs
            self.fields['consumer_ptg'].choices = ptgs
            self.fields['classifier'].choices = [
                (item.id, item.name) for item in classifiers]
        except Exception:
            msg = _("Failed to retrive policy targets")
            LOG.error(msg)

    def handle(self, request, context):
        url = reverse("horizon:project:network_services:index")
        try:
            client.create_servicechain_instance(request, **context)
            msg = _("Service Chain Instance Created Successfully!")
            LOG.debug(msg)
            return http.HttpResponseRedirect(url)
        except Exception as e:
            msg = _("Failed to create Service Chain Instance.  %s") % (str(e))
            LOG.error(msg)
            exceptions.handle(request, msg, redirect=shortcuts.redirect)


class UpdateServiceChainInstanceForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=80, label=_("Name"))
    description = forms.CharField(
        max_length=80, label=_("Description"), required=False)
    servicechain_spec = forms.ChoiceField(label=_("ServiceChain Spec"))

    def __init__(self, request, *args, **kwargs):
        super(UpdateServiceChainInstanceForm, self).__init__(
            request, *args, **kwargs)
        try:
            scinstance_id = self.initial['scinstance_id']
            sc_specs = client.servicechainspec_list(request)
            self.fields['servicechain_spec'].choices = [
                (item.id, item.name) for item in sc_specs]
            scinstance = client.get_servicechain_instance(
                request, scinstance_id)
            for attr in ['name', 'description', 'servicechain_spec']:
                self.fields[attr].initial = getattr(scinstance, attr)
        except Exception:
            pass

    def handle(self, request, context):
        url = reverse("horizon:project:network_services:index")
        try:
            scinstance_id = self.initial['scinstance_id']
            client.update_servicechain_instance(
                request, scinstance_id, **context)
            msg = _("Service Chain Instance Created Successfully!")
            LOG.debug(msg)
            return http.HttpResponseRedirect(url)
        except Exception as e:
            msg = _("Failed to create Service Chain Instance.  %s") % (str(e))
            LOG.error(msg)
            exceptions.handle(request, msg, redirect=shortcuts.redirect)
