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

from horizon import tables


class CreateL2PolicyLink(tables.LinkAction):
    name = "create_l2policy"
    verbose_name = _("Create L2 Policy")
    url = "horizon:project:network_policy:addl2policy"
    classes = ("ajax-modal", "btn-addl2policy")


class EditL2PolicyLink(tables.LinkAction):
    name = "update_l2policy"
    verbose_name = _("Edit L2Policy")
    classes = ("ajax-modal", "btn-update",)

    def get_link_url(self, l2policy):
        base_url = reverse("horizon:project:network_policy:update_l2policy",
                kwargs={'l2policy_id': l2policy.id})
        return base_url


class DeleteL2PolicyLink(tables.DeleteAction):
    name = "deletel2policy"
    action_present = _("Delete")
    action_past = _("Scheduled deletion of %(data_type)s")
    data_type_singular = _("L2Policy")
    data_type_plural = _("L2Policies")


class L2PolicyTable(tables.DataTable):
    name = tables.Column("name",
            verbose_name=_("Name"),
            link="horizon:project:network_policy:l2policy_details")
    description = tables.Column("description", verbose_name=_("Description"))
    id = tables.Column("id", verbose_name=_("ID"))
    l3_policy_id = tables.Column(
        "l3_policy_id", verbose_name=_("L3 Policy ID"))

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


class EditL3PolicyLink(tables.LinkAction):
    name = "update_l3policy"
    verbose_name = _("Edit L3Policy")
    classes = ("ajax-modal", "btn-update",)

    def get_link_url(self, l3policy):
        base_url = reverse("horizon:project:network_policy:update_l3policy",
                kwargs={'l3policy_id': l3policy.id})
        return base_url


class DeleteL3PolicyLink(tables.DeleteAction):
    name = "deletel3policy"
    action_present = _("Delete")
    action_past = _("Scheduled deletion of %(data_type)s")
    data_type_singular = _("L3 Policy")
    data_type_plural = _("L3 Policies")


class L3PolicyTable(tables.DataTable):
    name = tables.Column("name",
            verbose_name=_("Name"),
            link="horizon:project:network_policy:l3policy_details")
    description = tables.Column("description", verbose_name=_("Description"))
    id = tables.Column("id", verbose_name=_("ID"))
    ip_version = tables.Column("ip_version", verbose_name=_("IP Version"))
    ip_pool = tables.Column("ip_pool", verbose_name=_("IP Pool"))
    subnet_prefix_length = tables.Column(
        "subnet_prefix_length", verbose_name=_("Subnet Prefix Length"))
    external_segments = tables.Column("external_segments",
        verbose_name=_("External Segment"))

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


class EditServicePolicyLink(tables.LinkAction):
    name = "update_service_policy"
    verbose_name = _("Edit")
    classes = ("ajax-modal", "btn-update",)

    def get_link_url(self, policy):
        urlstring = "horizon:project:network_policy:update_service_policy"
        base_url = reverse(urlstring, kwargs={'service_policy_id': policy.id})
        return base_url


class DeleteServicePolicyLink(tables.DeleteAction):
    name = "deletespolicy"
    action_present = _("Delete")
    action_past = _("Scheduled deletion of %(data_type)s")
    data_type_singular = _("ServicePolicy")
    data_type_plural = _("ServicePolicies")


class ServicePolicyTable(tables.DataTable):
    name = tables.Column("name", verbose_name=_("Name"),
            link="horizon:project:network_policy:service_policy_details")
    description = tables.Column("description", verbose_name=_("Description"))
    network_service_params = tables.Column('network_service_params',
                                    verbose_name=_("Network Service Params"))

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


class EditExternalConnectivityLink(tables.LinkAction):
    name = "update_external_connectivity"
    verbose_name = _("Edit")
    classes = ("ajax-modal", "btn-update",)

    def get_link_url(self, external_connectivity):
        urlstring = \
            "horizon:project:network_policy:update_externalconnectivity"
        base_url = reverse(urlstring,
            kwargs={'external_connectivity_id': external_connectivity.id})
        return base_url


class DeleteExternalConnectivityLink(tables.DeleteAction):
    name = "deleteexternalconnectivity"
    action_present = _("Delete")
    action_past = _("Scheduled deletion of %(data_type)s")
    data_type_singular = _("ExternalConnectivity")
    data_type_plural = _("ExternalConnectivities")


class ExternalConnectivityTable(tables.DataTable):
    name = tables.Column("name", verbose_name=_("Name"),
        link="horizon:project:network_policy:external_connectivity_details")
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
