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


class CreateServiceChainSpecLink(tables.LinkAction):
    name = "create_scspec_link"
    verbose_name = _("Create Service Chain Spec")
    url = "horizon:project:network_services:create_sc_spec"
    classes = ("ajax-modal", "btn-create_scspec")


class EditServiceChainSpecLink(tables.LinkAction):
    name = "edit_sc_spec"
    verbose_name = _("Edit")
    classes = ("ajax-modal", "btn-update",)

    def get_link_url(self, scspec):
        base_url = reverse("horizon:project:network_services:update_sc_spec",
                kwargs={'scspec_id': scspec.id})
        return base_url


class DeleteServiceChainSpecLink(tables.DeleteAction):
    name = "deletescspec"
    action_present = _("Delete")
    action_past = _("Scheduled deletion of %(data_type)s")
    data_type_singular = _("Service Chain Spec")
    data_type_plural = _("Service Chain Specs")


class ServiceChainSpecTable(tables.DataTable):
    name = tables.Column("name",
                     verbose_name=_("Name"),
                     link="horizon:project:network_services:sc_spec_details")
    description = tables.Column("description",
                                verbose_name=_("Description"))
    nodes = tables.Column("nodes", verbose_name=_("Nodes"))

    class Meta(object):
        name = "service_chain_spec_table"
        verbose_name = _("Service Chain Specs")
        table_actions = (CreateServiceChainSpecLink,
                            DeleteServiceChainSpecLink,)
        row_actions = (EditServiceChainSpecLink,
                        DeleteServiceChainSpecLink,)


class CreateServiceChainNodeLink(tables.LinkAction):
    name = "create_scnode_link"
    verbose_name = _("Create Service Chain Node")
    url = "horizon:project:network_services:create_sc_node"
    classes = ("ajax-modal", "btn-create_scnode")


class EditServiceChainNodeLink(tables.LinkAction):
    name = "edit_sc_node"
    verbose_name = _("Edit")
    classes = ("ajax-modal", "btn-update",)

    def get_link_url(self, scnode):
        base_url = reverse("horizon:project:network_services:update_sc_node",
                kwargs={'scnode_id': scnode.id})
        return base_url


class DeleteServiceChainNodeLink(tables.DeleteAction):
    name = "deletescnode"
    action_present = _("Delete")
    action_past = _("Scheduled deletion of %(data_type)s")
    data_type_singular = _("Service Chain Node")
    data_type_plural = _("Service Chain Nodes")


class ServiceChainNodeTable(tables.DataTable):
    name = tables.Column("name",
                     verbose_name=_("Name"),
                     link="horizon:project:network_services:sc_node_details")
    description = tables.Column("description",
                                verbose_name=_("Description"))
    service_profile = tables.Column("service_profile",
                                 verbose_name=_("Service Profile"))

    class Meta(object):
        name = "service_chain_node_table"
        verbose_name = _("Service Chain Node")
        table_actions = (CreateServiceChainNodeLink,
                DeleteServiceChainNodeLink,)
        row_actions = (EditServiceChainNodeLink,
                DeleteServiceChainNodeLink,)


class CreateServiceChainInstanceLink(tables.LinkAction):
    name = "create_scinstance_link"
    verbose_name = _("Create Service Chain Instance")
    url = "horizon:project:network_services:create_sc_instance"
    classes = ("ajax-modal", "btn-create_scinstance")


class EditServiceChainInstanceLink(tables.LinkAction):
    name = "edit_sc_instance"
    verbose_name = _("Edit")
    classes = ("ajax-modal", "btn-update",)

    def get_link_url(self, scinstance):
        urlstring = "horizon:project:network_services:update_sc_instance"
        base_url = reverse(urlstring, kwargs={'scinstance_id': scinstance.id})
        return base_url


class DeleteServiceChainInstanceLink(tables.DeleteAction):
    name = "deletescinstance"
    action_present = _("Delete")
    action_past = _("Scheduled deletion of %(data_type)s")
    data_type_singular = _("ServiceChainInstance")
    data_type_plural = _("ServiceChainInstances")


class ServiceChainInstanceTable(tables.DataTable):
    name = tables.Column("name",
            verbose_name=_("Name"),
            link="horizon:project:network_services:sc_instance_details")
    description = tables.Column("description",
                                verbose_name=_("Description"))
    provider_ptg = tables.Column(
        "provider_ptg", verbose_name=_("Provider"))
    servicechain = tables.Column(
        "servicechain", verbose_name=_("Service Chain"))
    # consumer_ptg = tables.Column(
    #    "consumer_ptg", verbose_name=_("Consumer"))
    servicechain_spec = tables.Column(
        "servicechain_spec", verbose_name=_("Service Chain Spec"))
    classifier = tables.Column("classifier", verbose_name=_("Classifier"))

    class Meta(object):
        name = "service_chain_instance_table"
        verbose_name = _("Service Chain Instance")


class CreateServiceProfileLink(tables.LinkAction):
    name = "create_service_profile_link"
    verbose_name = _("Create Service Profile")
    url = "horizon:project:network_services:create_service_profile"
    classes = ("ajax-modal", "btn-create_service_profile")


class DeleteServiceProfileLink(tables.DeleteAction):
    name = "deleteserviceprofile"
    action_present = _("Delete")
    action_past = _("Scheduled deletion of %(data_type)s")
    data_type_singular = _("ServiceProfile")
    data_type_plural = _("ServiceProfiles")


class ServiceProfileTable(tables.DataTable):
    name = tables.Column("name", verbose_name=_("Name"),
        link="horizon:project:network_services:service_profile_details")
    description = tables.Column("description",
        verbose_name=_("Description"))
    service_type = tables.Column("service_type",
        verbose_name=_("Service Type"))
    insertion_mode = tables.Column("insertion_mode",
        verbose_name=_("Insertion Mode"))
    vendor = tables.Column("vendor", verbose_name=_("Vendor"))

    class Meta(object):
        name = "service_profile_table"
        verbose_name = _("Service Profile")
        table_actions = (CreateServiceProfileLink,
                DeleteServiceProfileLink,)
        row_actions = (DeleteServiceProfileLink,)
