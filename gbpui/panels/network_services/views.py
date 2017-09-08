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
from horizon import forms
from horizon import tabs

import forms as ns_forms
import tabs as ns_tabs

from django.utils.translation import ugettext_lazy as _
from gbpui.common import forms as gbforms


class IndexView(tabs.TabbedTableView):
    tab_group_class = (ns_tabs.ServiceChainTabs)
    template_name = 'gbpui/details_tabs.html'
    page_title = _("Network Services")


class ServiceProfileDetailsView(tabs.TabView):
    tab_group_class = (ns_tabs.ServiceProfileDetailsTabGroup)
    template_name = 'gbpui/details_tabs.html'
    page_title = _("Service Profile Details")


class CreateServiceProfileView(gbforms.HelpTextModalMixin,
                               gbforms.ReversingModalFormView):
    form_class = ns_forms.CreateServiceProfileForm
    template_name = "gbpui/form_with_description.html"
    submit_url = "horizon:project:network_services:create_service_profile"
    modal_header = _("Create Service Profile")
    submit_label = _("Create")
    page_title = _("Create Service Profile")
    help_text = _("Create Service Profile.")


class CreateServiceChainNodeView(gbforms.HelpTextModalMixin,
                                 gbforms.ReversingModalFormView):
    form_class = ns_forms.CreateServiceChainNodeForm
    template_name = "gbpui/form_with_description.html"
    submit_url = "horizon:project:network_services:create_sc_node"
    modal_header = _("Create Service Chain Node")
    submit_label = _("Create")
    page_title = _("Create Service Chain Node")
    help_text = _("Create Service Chain Node.")


class UpdateServiceChainNodeView(gbforms.HelpTextModalMixin,
                                 gbforms.ReversingModalFormView):
    form_class = ns_forms.UpdateServiceChainNodeForm
    template_name = "gbpui/form_with_description.html"
    submit_url = "horizon:project:network_services:update_sc_node"
    modal_header = _("Update Service Chain Node")
    submit_label = _("Save Changes")
    page_title = _("Update Service Chain Node")
    help_text = _("Update Service Chain Node.")

    def get_submit_url_params(self, **kwargs):
        return {"scnode_id": self.kwargs['scnode_id']}

    def get_initial(self):
        return self.kwargs


class ServiceChainNodeDetailsView(tabs.TabView):
    tab_group_class = (ns_tabs.SCNodeDetailsTabGroup)
    template_name = 'gbpui/details_tabs.html'
    page_title = _("Service Chain Node Details")


class CreateServiceChainSpecView(forms.ModalFormView):
    form_class = ns_forms.CreateServiceChainSpecForm
    template_name = "project/network_services/create_service_chain_spec.html"

    def get_context_data(self, **kwargs):
        context = super(
            CreateServiceChainSpecView, self).get_context_data(**kwargs)
        return context


class UpdateServiceChainSpecView(forms.ModalFormView):
    form_class = ns_forms.UpdateServiceChainSpecForm
    template_name = "project/network_services/update_service_chain_spec.html"

    def get_context_data(self, **kwargs):
        context = super(
            UpdateServiceChainSpecView, self).get_context_data(**kwargs)
        context['scspec_id'] = self.kwargs['scspec_id']
        return context

    def get_initial(self):
        return self.kwargs


class ServiceChainSpecDetailsView(tabs.TabView):
    tab_group_class = (ns_tabs.SCSpecDetailsTabGroup)
    template_name = 'gbpui/details_tabs.html'
    page_title = _("Service Chain Spec Details")


class ServiceChainInstanceDetailsView(tabs.TabView):
    tab_group_class = (ns_tabs.SCInstanceDetailsTabGroup)
    template_name = 'gbpui/details_tabs.html'
    page_title = _("Service Chain Instance Details")
