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

import re

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon import tabs
from horizon.utils import memoized
from horizon import workflows
from horizon import tables

from gbp_ui import client

import forms as ns_forms
import tabs as ns_tabs
import workflow as ns_workflows
import tables as ns_tables


class IndexView(tabs.TabView):
    tab_group_class = (ns_tabs.ServiceChainTabs)
    template_name = 'project/network_services/details_tabs.html'

class CreateServiceChainNodeView(forms.ModalFormView):
 	form_class = ns_forms.CreateServiceChainNodeForm
	template_name = "project/network_services/create_service_chain_node.html"

	def get_context_data(self, **kwargs):
		context = super(CreateServiceChainNodeView,self).get_context_data(**kwargs)
		return context

class UpdateServiceChainNodeView(forms.ModalFormView):
 	form_class = ns_forms.UpdateServiceChainNodeForm
	template_name = "project/network_services/update_service_chain_node.html"

	def get_context_data(self, **kwargs):
		context = super(UpdateServiceChainNodeView,self).get_context_data(**kwargs)
		context['scnode_id'] = self.kwargs['scnode_id']
		return context

	def get_initial(self):
		return self.kwargs

class ServiceChainNodeDetailsView(tabs.TabView):
	tab_group_class = (ns_tabs.SCNodeDetailsTabGroup)
	template_name = 'project/network_services/details_tabs.html' 

class CreateServiceChainSpecView(forms.ModalFormView):
  	form_class = ns_forms.CreateServiceChainSpecForm
	template_name = "project/network_services/create_service_chain_spec.html"

	def get_context_data(self, **kwargs):
		context = super(CreateServiceChainSpecView,self).get_context_data(**kwargs)
		return context

class UpdateServiceChainSpecView(forms.ModalFormView):
  	form_class = ns_forms.UpdateServiceChainSpecForm
	template_name = "project/network_services/update_service_chain_spec.html"

	def get_context_data(self, **kwargs):
		context = super(UpdateServiceChainSpecView,self).get_context_data(**kwargs)
		context['scspec_id'] = self.kwargs['scspec_id']
		return context
 	
	def get_initial(self):
		return self.kwargs

class ServiceChainSpecDetailsView(tabs.TabView):
	tab_group_class = (ns_tabs.SCSpecDetailsTabGroup)
	template_name = 'project/network_services/details_tabs.html' 
 
class CreateServiceChainInstanceView(forms.ModalFormView):
   	form_class = ns_forms.CreateServiceChainInstanceForm
	template_name = "project/network_services/create_service_chain_instance.html"

	def get_context_data(self, **kwargs):
		context = super(CreateServiceChainInstanceView,self).get_context_data(**kwargs)
		return context

class UpdateServiceChainInstanceView(forms.ModalFormView):
   	form_class = ns_forms.UpdateServiceChainInstanceForm
	template_name = "project/network_services/update_service_chain_instance.html"

	def get_context_data(self, **kwargs):
		context = super(UpdateServiceChainInstanceView,self).get_context_data(**kwargs)
		context['scinstance_id'] = self.kwargs['scinstance_id']
		return context 
 	
	def get_initial(self):
		return self.kwargs

class ServiceChainInstanceDetailsView(tabs.TabView):
	tab_group_class = (ns_tabs.SCInstanceDetailsTabGroup)
	template_name = 'project/network_services/details_tabs.html' 
