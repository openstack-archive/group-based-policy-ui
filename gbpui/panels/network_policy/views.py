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
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tables
from horizon import tabs

from gbpui import client
from gbpui.common import forms as gbforms

import forms as np_forms
import tables as np_tables
import tabs as np_tabs


class IndexView(tabs.TabbedTableView):
    tab_group_class = (np_tabs.L3PolicyTabs)
    template_name = "gbpui/details_tabs.html"
    page_title = _("Network and Services' Policies")


class AddL3policyView(gbforms.HelpTextModalMixin,
                      gbforms.ReversingModalFormView):
    form_class = np_forms.AddL3PolicyForm

    template_name = "gbpui/form_with_description.html"
    submit_url = "horizon:project:network_policy:addl3policy"
    modal_header = _("Add L3Policy")
    submit_label = _("Create")
    page_title = _("Add L3Policy")
    help_text = _("Add L3 Policy.")

    def get_initial(self):
        return self.kwargs


class L3PolicyUpdateView(gbforms.HelpTextModalMixin,
                         gbforms.ReversingModalFormView):
    form_class = np_forms.UpdateL3PolicyForm
    template_name = "gbpui/form_with_description.html"
    submit_url = "horizon:project:network_policy:update_l3policy"
    modal_header = _("Update L3Policy")
    submit_label = _("Save Changes")
    page_title = _("Update L3Policy")
    help_text = _("Update L3Policy.")

    def get_submit_url_params(self, **kwargs):
        return {"l3policy_id": self.kwargs["l3policy_id"]}

    def get_initial(self):
        return self.kwargs


class L3PolicyDetailsView(tables.MultiTableView):
    table_classes = (np_tables.L2PolicyTable,)
    template_name = 'project/network_policy/l3policy_details.html'

    def get_l2policy_table_data(self):
        l2_policies = []
        try:
            condition = {'l3_policy_id': self.kwargs['l3policy_id']}
            l2_policies = client.l2policy_list(self.request,
                    tenant_id=self.request.user.tenant_id, **condition)
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve l2 policy list.'))
        return l2_policies

    def get_context_data(self, **kwargs):
        context = super(L3PolicyDetailsView, self).get_context_data(**kwargs)
        p = client.l3policy_get(self.request, self.kwargs['l3policy_id'])
        context['l3policy'] = p
        return context


class AddL2policyView(gbforms.HelpTextModalMixin,
                      gbforms.ReversingModalFormView):
    form_class = np_forms.AddL2PolicyForm
    template_name = "gbpui/form_with_description.html"
    submit_url = "horizon:project:network_policy:addl2policy"
    modal_header = _("Add L2Policy")
    submit_label = _("Save Changes")
    page_title = _("Add L2Policy")
    help_text = _("Add L2Policy.")


class L2PolicyUpdateView(gbforms.HelpTextModalMixin,
                         gbforms.ReversingModalFormView):
    form_class = np_forms.UpdateL2PolicyForm
    template_name = "gbpui/form_with_description.html"
    submit_url = "horizon:project:network_policy:update_l2policy"
    modal_header = _("Update L2Policy")
    submit_label = _("Save Changes")
    page_title = _("Update L2Policy")
    help_text = _("Update L2Policy.")

    def get_submit_url_params(self, **kwargs):
        return {"l2policy_id": self.kwargs["l2policy_id"]}

    def get_initial(self):
        return self.kwargs


class L2PolicyDetailsView(tabs.TabView):
    tab_group_class = (np_tabs.L2PolicyDetailsTabs)
    template_name = "gbpui/details_tabs.html"
    page_title = _("L2 Policy Details")


class CreateServicePolicyView(gbforms.HelpTextModalMixin,
                              gbforms.ReversingModalFormView):
    form_class = np_forms.CreateServicePolicyForm

    template_name = "gbpui/form_with_description.html"
    submit_url = "horizon:project:network_policy:create_servicepolicy"
    modal_header = _("Create Service Policy")
    submit_label = _("Create")
    page_title = _("Create Service Policy")
    help_text = _("Create Service Policy.")


class AddExternalSegmentParamView(gbforms.HelpTextModalMixin,
                                  gbforms.ReversingModalFormView):
    form_class = np_forms.CreateExternalSegmentParamForm
    template_name = "gbpui/form_with_description.html"
    submit_url = "horizon:project:network_policy:add_external_segment_param"
    modal_header = _("Add External Segment Parameter")
    submit_label = _("Create")
    page_title = _("Add External Segment Parameter")
    help_text = _("Add External Segment Parameter.")

    def get_object_id(self, params):
        return params.name


class AddNetworkServiceParamView(gbforms.HelpTextModalMixin,
                                 gbforms.ReversingModalFormView):
    form_class = np_forms.CreateNetworkServiceParamForm
    template_name = "gbpui/form_with_description.html"
    submit_url = "horizon:project:network_policy:add_network_service_param"
    modal_header = _("Add Network Service Parameter")
    submit_label = _("Create")
    page_title = _("Add Network Service Parameter")
    help_text = _("Add Network Service Parameter.")

    def get_object_id(self, params):
        return params.name


class AddExternalRouteParamView(gbforms.HelpTextModalMixin,
                                 gbforms.ReversingModalFormView):
    form_class = np_forms.CreateExternalRouteParamForm
    template_name = "gbpui/form_with_description.html"
    submit_url = "horizon:project:network_policy:add_external_route_param"
    modal_header = _("Add External Route Parameter")
    submit_label = _("Create")
    page_title = _("Add External Route Parameter")
    help_text = _("Add External Route Parameter.")

    def get_object_id(self, params):
        return params.name


class UpdateNATPoolView(gbforms.HelpTextModalMixin,
                        gbforms.ReversingModalFormView):
    form_class = np_forms.UpdateNATPoolForm
    template_name = "gbpui/form_with_description.html"
    submit_url = "horizon:project:network_policy:update_natpool"
    modal_header = _("Update NAT Pool")
    submit_label = _("Save Changes")
    page_title = _("Update NAT Pool")
    help_text = _("Update NAT Pool.")

    def get_submit_url_params(self, **kwargs):
        return {"nat_pool_id": self.kwargs["nat_pool_id"]}

    def get_initial(self):
        return self.kwargs


class UpdateExternalConnectivityView(gbforms.HelpTextModalMixin,
                                     gbforms.ReversingModalFormView):
    form_class = np_forms.UpdateExternalConnectivityForm
    template_name = "gbpui/form_with_description.html"
    submit_url = "horizon:project:network_policy:update_externalconnectivity"
    modal_header = _("Update External Connectivity")
    submit_label = _("Save Changes")
    page_title = _("Update External Connectivity")
    help_text = _("Update External Connectivity.")

    def get_submit_url_params(self, **kwargs):
        return {
            "external_connectivity_id": self.kwargs["external_connectivity_id"]
        }

    def get_initial(self):
        return self.kwargs


class UpdateServicePolicyView(gbforms.HelpTextModalMixin,
                              gbforms.ReversingModalFormView):
    form_class = np_forms.UpdateServicePolicyForm
    template_name = "gbpui/form_with_description.html"
    submit_url = "horizon:project:network_policy:update_service_policy"
    modal_header = _("Update Service Policy")
    submit_label = _("Save Changes")
    page_title = _("Update Service Policy")
    help_text = _("Update Service Policy.")

    def get_submit_url_params(self, **kwargs):
        return {"service_policy_id": self.kwargs["service_policy_id"]}

    def get_initial(self):
        return self.kwargs


class ServicePolicyDetailsView(tabs.TabView):
    tab_group_class = (np_tabs.ServicePolicyDetailsTabs)
    template_name = 'gbpui/details_tabs.html'
    page_title = _("Service Policy Details")


class CreateExternalConnectivityView(gbforms.HelpTextModalMixin,
                                     gbforms.ReversingModalFormView):
    form_class = np_forms.CreateExternalConnectivityForm
    template_name = "gbpui/form_with_description.html"
    submit_url = "horizon:project:network_policy:create_external_connectivity"
    modal_header = _("Create External Connectivity")
    submit_label = _("Save Changes")
    page_title = _("Create External Connectivity")
    help_text = _("Create External Connectivity.")

    def get_success_url(self):
        return reverse('horizon:project:network_policy:index')


class ExternalConnectivityDetailsView(tabs.TabView):
    tab_group_class = (np_tabs.ExternalConnectivityDetailsTabs)
    template_name = "gbpui/details_tabs.html"
    page_title = _("External Connectivity Details")


class CreateNATPoolView(gbforms.HelpTextModalMixin,
                        gbforms.ReversingModalFormView):
    form_class = np_forms.CreateNATPoolForm
    template_name = "gbpui/form_with_description.html"
    submit_url = "horizon:project:network_policy:create_nat_pool"
    modal_header = _("Create NAT Pool")
    submit_label = _("Create")
    page_title = _("Create NAT Pool")
    help_text = _("Create NAT Pool.")

    def get_success_url(self):
        return reverse('horizon:project:application_policy:index')


class NATPoolDetailsView(tabs.TabView):
    tab_group_class = (np_tabs.NATPoolDetailsTabs)
    template_name = 'gbpui/details_tabs.html'
    page_title = _("NAT Pool Details")
