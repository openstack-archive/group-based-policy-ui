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

import extractors

from horizon import tables

from gbpui import client

from gbpui.common import tables as gbtables
from gbpui import GBP_POLICY_FILE


class CreateL2PolicyLink(tables.LinkAction):
    name = "create_l2policy"
    verbose_name = _("Create L2 Policy")
    url = "horizon:project:network_policy:addl2policy"
    classes = ("ajax-modal", "btn-addl2policy")
    policy_rules = ((GBP_POLICY_FILE, "create_l2_policy"),)


class EditL2PolicyLink(tables.LinkAction):
    name = "update_l2policy"
    verbose_name = _("Edit")
    classes = ("ajax-modal", "btn-update",)
    policy_rules = ((GBP_POLICY_FILE, "update_l2_policy"),)

    def get_link_url(self, l2policy):
        base_url = reverse("horizon:project:network_policy:update_l2policy",
                           kwargs={'l2policy_id': l2policy.id})
        return base_url


class DeleteL2PolicyLink(gbtables.GBPDeleteAction):
    name = "deletel2policy"
    action_present = _("Delete")
    action_past = _("Scheduled deletion of %(data_type)s")
    data_type_singular = _("L2Policy")
    data_type_plural = _("L2Policies")
    policy_rules = ((GBP_POLICY_FILE, "delete_l2_policy"),)

    def action(self, request, object_id):
        client.l2policy_delete(request, object_id)


class L2PolicyTable(tables.DataTable):
    name = gbtables.LinkColumn(
        "name",
        verbose_name=_("Name"),
        link="horizon:project:network_policy:l2policy_details",
        link_rules=((GBP_POLICY_FILE, "get_l2_policy"),)
    )
    description = tables.Column("description", verbose_name=_("Description"))
    id = tables.Column("id", verbose_name=_("ID"))
    l3_policy_id = tables.Column(
        "l3_policy_id", verbose_name=_("L3 Policy ID"))
    inject_default_route = tables.Column(
        "inject_default_route", verbose_name=_("Inject Default Route"))

    class Meta(object):
        name = "l2policy_table"
        verbose_name = _("L2 Policies")
        table_actions = (CreateL2PolicyLink, DeleteL2PolicyLink)
        row_actions = (EditL2PolicyLink, DeleteL2PolicyLink)


class CreateL3PolicyLink(tables.LinkAction):
    name = "create_l3policy"
    verbose_name = _("Create L3 Policy")
    url = "horizon:project:network_policy:addl3policy"
    classes = ("ajax-modal", "btn-addl3policy")
    policy_rules = ((GBP_POLICY_FILE, "create_l3_policy"),)


class EditL3PolicyLink(tables.LinkAction):
    name = "update_l3policy"
    verbose_name = _("Edit")
    classes = ("ajax-modal", "btn-update",)
    policy_rules = ((GBP_POLICY_FILE, "update_l3_policy"),)

    def get_link_url(self, l3policy):
        base_url = reverse("horizon:project:network_policy:update_l3policy",
                           kwargs={'l3policy_id': l3policy.id})
        return base_url


class DeleteL3PolicyLink(tables.DeleteAction):
    name = "deletel3policy"
    action_present = _("Delete")
    action_past = _("Deleted %(data_type)s")
    data_type_singular = _("L3 Policy")
    data_type_plural = _("L3 Policies")
    policy_rules = ((GBP_POLICY_FILE, "delete_l3_policy"),)

    def action(self, request, object_id):
        client.l3policy_delete(request, object_id)


class L3PolicyTable(tables.DataTable):
    name = gbtables.LinkColumn(
        "name",
        verbose_name=_("Name"),
        link="horizon:project:network_policy:l3policy_details",
        link_rules=((GBP_POLICY_FILE, "get_l3_policy"),)
    )
    description = tables.Column("description", verbose_name=_("Description"))
    id = tables.Column("id", verbose_name=_("ID"))
    ip_version = tables.Column("ip_version", verbose_name=_("IP Version"))
    ip_pool = tables.Column("ip_pool", verbose_name=_("IP Pool"))
    subnet_prefix_length = tables.Column(
        "subnet_prefix_length", verbose_name=_("Subnet Prefix Length"))
    external_segments = gbtables.ListColumn(
        extractors.get_external_segment_name,
        source_list="external_segments",
        verbose_name=_("External Segment"),
        empty_value="-"
    )

    class Meta(object):
        name = "l3policy_table"
        verbose_name = _("L3 Policy")
        table_actions = (CreateL3PolicyLink, DeleteL3PolicyLink,)
        row_actions = (EditL3PolicyLink, DeleteL3PolicyLink,)


class CreateServicePolicyLink(tables.LinkAction):
    name = "create_service_policy"
    verbose_name = _("Create Service Policy")
    url = "horizon:project:network_policy:create_servicepolicy"
    classes = ("ajax-modal", "btn-addservicepolicy")
    policy_rules = ((GBP_POLICY_FILE, "create_network_service_policy"),)


class EditServicePolicyLink(tables.LinkAction):
    name = "update_service_policy"
    verbose_name = _("Edit")
    classes = ("ajax-modal", "btn-update",)
    policy_rules = ((GBP_POLICY_FILE, "update_network_service_policy"),)

    def get_link_url(self, policy):
        urlstring = "horizon:project:network_policy:update_service_policy"
        base_url = reverse(urlstring, kwargs={'service_policy_id': policy.id})
        return base_url


class DeleteServicePolicyLink(gbtables.GBPDeleteAction):
    name = "deletespolicy"
    action_present = _("Delete")
    action_past = _("Deleted %(data_type)s")
    data_type_singular = _("ServicePolicy")
    data_type_plural = _("ServicePolicies")
    policy_rules = ((GBP_POLICY_FILE, "delete_network_service_policy"),)

    def action(self, request, object_id):
        client.delete_networkservice_policy(request, object_id)


class ServicePolicyTable(tables.DataTable):
    name = gbtables.LinkColumn(
        "name",
        verbose_name=_("Name"),
        link="horizon:project:network_policy:service_policy_details",
        link_rules=((GBP_POLICY_FILE, "get_network_service_policy"),)
    )
    description = tables.Column("description", verbose_name=_("Description"))
    network_service_params = tables.Column('network_service_params',
                                           verbose_name=_(
                                               "Network Service Params"))

    class Meta(object):
        name = "service_policy_table"
        verbose_name = _("Service Policies")
        table_actions = (CreateServicePolicyLink, DeleteServicePolicyLink,)
        row_actions = (EditServicePolicyLink, DeleteServicePolicyLink,)


class CreateExternalConnectivityLink(tables.LinkAction):
    name = "create_external_connectivity"
    verbose_name = _("Create External Connectivity")
    url = "horizon:project:network_policy:create_external_connectivity"
    classes = ("ajax-modal", "btn-addexternalconnectivity")
    policy_rules = ((GBP_POLICY_FILE, "create_external_segment"),)


class EditExternalConnectivityLink(tables.LinkAction):
    name = "update_external_connectivity"
    verbose_name = _("Edit")
    classes = ("ajax-modal", "btn-update",)
    policy_rules = ((GBP_POLICY_FILE, "update_external_segment"),)

    def get_link_url(self, external_connectivity):
        urlstring = \
            "horizon:project:network_policy:update_externalconnectivity"
        base_url = reverse(
            urlstring,
            kwargs={
                'external_connectivity_id': external_connectivity.id
            }
        )
        return base_url


class DeleteExternalConnectivityLink(gbtables.GBPDeleteAction):
    name = "deleteexternalconnectivity"
    action_present = _("Delete")
    action_past = _("Deleted %(data_type)s")
    data_type_singular = _("External Connectivity")
    data_type_plural = _("External Connectivities")
    policy_rules = ((GBP_POLICY_FILE, "delete_external_segment"),)

    def action(self, request, object_id):
        client.delete_externalconnectivity(request, object_id)


class ExternalConnectivityTable(tables.DataTable):
    name = gbtables.LinkColumn(
        "name",
        verbose_name=_("Name"),
        link="horizon:project:network_policy:external_connectivity_details",
        link_rules=((GBP_POLICY_FILE, "get_external_segment"),)
    )
    description = tables.Column("description", verbose_name=_("Description"))
    ip_version = tables.Column("ip_version", verbose_name=_("IP Version"))
    cidr = tables.Column("cidr", verbose_name=_("CIDR"))

    class Meta(object):
        name = "external_connectivity_table"
        verbose_name = _("External Connectivity")
        table_actions = (CreateExternalConnectivityLink,
                         DeleteExternalConnectivityLink,)
        row_actions = (EditExternalConnectivityLink,
                       DeleteExternalConnectivityLink,)


class CreateNATPoolLink(tables.LinkAction):
    name = "create_nat_pool"
    verbose_name = _("Create NAT Pool")
    url = "horizon:project:network_policy:create_nat_pool"
    classes = ("ajax-modal", "btn-addnatpool")
    policy_rules = ((GBP_POLICY_FILE, "create_nat_pool"),)


class DeleteNATPoolLink(gbtables.GBPDeleteAction):
    name = "deletenatpool"
    action_present = _("Delete")
    action_past = _("Scheduled deletion of %(data_type)s")
    data_type_singular = _("NAT Pool")
    data_type_plural = _("NAT Pools")
    policy_rules = ((GBP_POLICY_FILE, "delete_nat_pool"),)

    def action(self, request, object_id):
        client.delete_natpool(request, object_id)


class EditNATPoolLink(tables.LinkAction):
    name = "update_nat_pool"
    verbose_name = _("Edit")
    classes = ("ajax-modal", "btn-update",)
    policy_rules = ((GBP_POLICY_FILE, "update_nat_pool"),)

    def get_link_url(self, nat_pool):
        urlstring = "horizon:project:network_policy:update_natpool"
        base_url = reverse(urlstring,
                           kwargs={'nat_pool_id': nat_pool.id})
        return base_url


class NATPoolTable(tables.DataTable):
    name = gbtables.LinkColumn(
        "name",
        verbose_name=_("Name"),
        link="horizon:project:network_policy:nat_pool_details",
        link_rules=((GBP_POLICY_FILE, "get_nat_pool"),)
    )
    description = tables.Column("description", verbose_name=_("Description"))
    ip_version = tables.Column("ip_version", verbose_name=_("IP Version"))
    cidr = tables.Column("ip_pool", verbose_name=_("IP Pool"))
    external_segment = gbtables.ListColumn(
        "name",
        source_list="external_segments",
        verbose_name=_("External Segment"),
        link="horizon:project:network_policy:external_connectivity_details",
        list_rules=((GBP_POLICY_FILE, "get_external_segment"),)
    )

    class Meta(object):
        name = "nat_pool_table"
        verbose_name = _("NAT Pool")
        table_actions = (CreateNATPoolLink, DeleteNATPoolLink,)
        row_actions = (EditNATPoolLink, DeleteNATPoolLink,)
