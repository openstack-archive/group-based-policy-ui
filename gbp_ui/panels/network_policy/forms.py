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

import logging

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from django import http
from django.shortcuts import redirect
from horizon import exceptions
from horizon import forms
from horizon import messages


LOG = logging.getLogger(__name__)
 
class AddL3PolicyForm(forms.SelfHandlingForm):
 	name = forms.CharField(max_length=80, label=_("Name"))
	description = forms.CharField(max_length=80, label=_("Description"), required=False)
	ip_version = forms.ChoiceField(choices=[(4, 'IPv4'), (6, 'IPv6')],
								widget=forms.Select(attrs={
                                  'class': 'switchable',
                                  'data-slug': 'ipversion',
                                }), label=_("IP Version")) 
	ip_pool = forms.IPField(label=_("IP Pool"),
									initial="",
									help_text=_("IP Pool"),
									version=forms.IPv4 | forms.IPv6,
									mask=True) 
	subnet_prefix_length = forms.CharField(max_length=80,
									label=_("Subnet Prefix Length"),
									help_text=_("Between 2-30 for IP4 and 2-127 for IP6."),)

	def __init__(self,request,*args,**kwargs):
		super(AddL3PolicyForm,self).__init__(request,*args,**kwargs)

	def clean(self):
		cleaned_data = super(AddL3PolicyForm, self).clean()
		if self.is_valid():
			ipversion = int(cleaned_data['ip_version'])
			subnet_prefix_length = int(cleaned_data['subnet_prefix_length'])
			msg = _("Subnet prefix out of range.")
			if ipversion == 4 and subnet_prefix_length not in range(2,31):
				raise forms.ValidationError(msg)
			if ipversion == 6 and subnet_prefix_length not in range(2,128):
				raise forms.ValidationError(msg)
		return cleaned_data
	
	def handle(self,request,context):
		url = reverse("horizon:project:network_policy:index")
 		try:
			l3_policy = client.l3policy_create(request,**context)
			msg = _("L3 Policy Created Successfully!")
			LOG.debug(msg)
			return http.HttpResponseRedirect(url)
		except Exception:
			msg = _("Failed to create L3 policy")
			LOG.error(msg)
			exceptions.handle(request, msg, redirect=redirect)
 
class UpdateL3PolicyForm(forms.SelfHandlingForm):
 	name = forms.CharField(max_length=80, label=_("Name"))
	description = forms.CharField(max_length=80, label=_("Description"), required=False)
	ip_version = forms.ChoiceField(choices=[(4, 'IPv4'), (6, 'IPv6')],
								widget=forms.Select(attrs={
                                  'class': 'switchable',
                                  'data-slug': 'ipversion',
                                }), label=_("IP Version")) 
	ip_pool = forms.IPField(label=_("IP Pool"),
									initial="",
									help_text=_("IP Pool"),
									version=forms.IPv4 | forms.IPv6,
									mask=True) 
	subnet_prefix_length = forms.CharField(max_length=80,
									label=_("Subnet Prefix Length"),
									help_text=_("Between 2-30 for IP4 and 2-127 for IP6."),)

	def __init__(self,request,*args,**kwargs):
		super(UpdateL3PolicyForm,self).__init__(request,*args,**kwargs)
		try:
			l3policy_id = self.kwargs['l3policy_id']
			l3policy_id = self.initial['l2policy_id']
		except Exception:
			pass
	
	def clean(self):
		cleaned_data = super(UpdateL3PolicyForm, self).clean()
		if self.is_valid():
			ipversion = int(cleaned_data['ip_version'])
			subnet_prefix_length = int(cleaned_data['subnet_prefix_length'])
			msg = _("Subnet prefix out of range.")
			if ipversion == 4 and subnet_prefix_length not in range(2,31):
				raise forms.ValidationError(msg)
			if ipversion == 6 and subnet_prefix_length not in range(2,128):
				raise forms.ValidationError(msg)
		return cleaned_data

	def handle(self,request,context):
		url = reverse("horizon:project:network_policy:index")
 		try:
			l3_policy = client.l3policy_create(request,**context)
			msg = _("L3 Policy Updated Successfully!")
			LOG.debug(msg)
			return http.HttpResponseRedirect(url)
		except Exception:
			msg = _("Failed to update L3 policy")
			LOG.error(msg)
			exceptions.handle(request, msg, redirect=redirect)
 
