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
from django.utils.translation import ugettext_lazy as _

import extractors

from horizon import exceptions
from horizon import tables

from openstack_dashboard import api
from openstack_dashboard.dashboards.project.instances import tables as itables
from openstack_dashboard.dashboards.project.instances import tabs

from gbpui import client
from gbpui.common import tables as gbtables

from gbpui import GBP_POLICY_FILE

LOG = logging.getLogger(__name__)


class UpdatePTGLink(tables.LinkAction):
    name = "updatepolicy_target"
    verbose_name = _("Edit")
    classes = ("ajax-modal", "btn-update",)
    policy_rules = ((GBP_POLICY_FILE, "update_policy_target_group"),)

    def get_link_url(self, policy_target):
        u = "horizon:project:policytargets:updatepolicy_target"
        base_url = reverse(u, kwargs={'policy_target_id': policy_target.id})
        return base_url


class DeletePTGLink(gbtables.GBPDeleteAction):
    name = "deletepolicytarget"
    action_present = _("Delete")
    action_past = _("Deleted %(data_type)s")
    data_type_singular = _("Group")
    data_type_plural = _("Groups")
    policy_rules = ((GBP_POLICY_FILE, "delete_policy_target_group"),)

    def action(self, request, object_id):
        client.policy_target_delete(request, object_id)


class AddPTGLink(tables.LinkAction):
    name = "addpolicy_target"
    verbose_name = _("Create Internal Group")
    url = "horizon:project:policytargets:addpolicy_target"
    classes = ("ajax-modal", "btn-addpolicy_target",)
    policy_rules = ((GBP_POLICY_FILE, "create_policy_target_group"),)


class PTGsTable(tables.DataTable):
    name = gbtables.LinkColumn(
        transform="name",
        verbose_name=_("Name"),
        link="horizon:project:policytargets:policy_targetdetails",
        link_rules=((GBP_POLICY_FILE, "get_policy_target_group"),)
    )
    description = tables.Column("description", verbose_name=_("Description"))
    provided_policy_rule_sets = gbtables.ListColumn(
        transform="name",
        source_list="provided_policy_rule_sets",
        link="horizon:project:application_policy:policy_rule_set_details",
        sortable=False,
        verbose_name=_("Provided Rule Sets"),
        list_rules=((GBP_POLICY_FILE, "get_policy_rule_set"),)
    )

    consumed_policy_rule_sets = gbtables.ListColumn(
        transform="name",
        source_list="consumed_policy_rule_sets",
        link="horizon:project:application_policy:policy_rule_set_details",
        sortable=False,
        verbose_name=_("Consumed Rule Sets"),
        list_rules=((GBP_POLICY_FILE, "get_policy_rule_set"),)
    )
    l2_policy = gbtables.LinkColumn(
        "l2_policy_name",
        verbose_name=_("L2 Policy"),
        link=extractors.get_l2_link,
        link_rules=((GBP_POLICY_FILE, "get_l2_policy"),)
    )
    status = tables.Column("status", verbose_name=_("Status"))

    class Meta(object):
        name = "policy_targetstable"
        verbose_name = _("Internal Groups")
        table_actions = (AddPTGLink, DeletePTGLink)
        row_actions = (UpdatePTGLink, DeletePTGLink)


class UpdateExternalPTGLink(tables.LinkAction):
    name = "updateexternal_policy_target"
    verbose_name = _("Edit")
    classes = ("ajax-modal", "btn-update",)
    policy_rules = ((GBP_POLICY_FILE, "update_external_policy"),)

    def get_link_url(self, ext_policy_target):
        u = "horizon:project:policytargets:update_ext_policy_target"
        base_url = reverse(u, kwargs={'ext_policy_target_id':
                                          ext_policy_target.id})
        return base_url


class AddExternalPTGLink(tables.LinkAction):
    name = "addexternal_policy_target"
    verbose_name = _("Create External Group")
    url = "horizon:project:policytargets:addexternal_policy_target"
    classes = ("ajax-modal", "btn-addexternal_policy_target",)
    policy_rules = ((GBP_POLICY_FILE, "create_external_policy"),)


class DeleteExternalPTGLink(tables.DeleteAction):
    name = "deleteexternalpolicytarget"
    action_present = _("Delete")
    action_past = _("Deleted %(data_type)s")
    data_type_singular = _("External Group")
    data_type_plural = _("External Groups")
    policy_rules = ((GBP_POLICY_FILE, "delete_external_policy"),)

    def action(self, request, object_id):
        client.ext_policy_target_delete(request, object_id)


class ExternalPTGsTable(tables.DataTable):
    name = gbtables.LinkColumn(
        "name",
        verbose_name=_("Name"),
        link="horizon:project:policytargets:ext_policy_targetdetails",
        link_rules=((GBP_POLICY_FILE, "get_external_policy"),)
    )
    description = tables.Column("description", verbose_name=_("Description"))

    provided_policy_rule_sets = gbtables.ListColumn(
        transform="name",
        source_list="provided_policy_rule_sets",
        sortable=False,
        verbose_name=_("Provided Rule Sets")
    )
    consumed_policy_rule_sets = gbtables.ListColumn(
        transform="name",
        source_list="consumed_policy_rule_sets",
        sortable=False,

        verbose_name=_("Consumed Rule Sets")
    )
    external_segments = gbtables.ListColumn(
        "name",
        verbose_name=_("External Connectivity"),
        link="horizon:project:network_policy:external_connectivity_details",
        source_list="external_segments",
        sortable=False,
        list_rules=((GBP_POLICY_FILE, "get_external_segment"),)
    )
    status = tables.Column("status", verbose_name=_("Status"))

    class Meta(object):
        name = "external_policy_targetstable"
        verbose_name = _("External Group")
        table_actions = (AddExternalPTGLink, DeleteExternalPTGLink)
        row_actions = (UpdateExternalPTGLink, DeleteExternalPTGLink,)


class LaunchVMLink(tables.LinkAction):
    name = "launch_vm-ng"
    verbose_name = _("Create Member")
    url = "horizon:project:policytargets:policy_targetdetails"
    ajax = False
    classes = ("btn-launch", )

    def get_link_url(self):
        return reverse("horizon:project:policytargets:addvm",
                       kwargs={'policy_target_id':
                                   self.table.kwargs['policy_target_id']})
    def get_default_attrs(self):
        url_kwargs = {
            'policy_target_id': self.table.kwargs['policy_target_id']
        }
        url = reverse(self.url, kwargs=url_kwargs)
        ngclick = "modal.openLaunchInstanceWizard(" \
                  "{ successUrl: '%s'," \
                  " defaults: ['%s'] }" \
                  ")" % (url, self.table.kwargs['policy_target_id'])

        self.attrs.update({
            'ng-controller': 'LaunchInstanceModalController as modal',
            'ng-click': ngclick
        })
        return super(LaunchVMLink, self).get_default_attrs()

    def get_link_url(self, datum=None):
        return ""


class RemoveVMLink(tables.DeleteAction):
    data_type_singular = _("Member")
    data_type_plural = _("Members")

    def delete(self, request, instance_id):
        url = reverse("horizon:project:policytargets:policy_targetdetails",
                      kwargs={'policy_target_id':
                                  self.table.kwargs['policy_target_id']})
        try:
            pts = []
            instance = api.nova.server_get(request, instance_id)
            metadata_pts = instance.metadata.get('pts', None)
            if metadata_pts:
                pts = metadata_pts.split(",")
                for pt in pts:
                    client.pt_delete(request, pt)
            api.nova.server_delete(request, instance_id)
            LOG.debug('Deleted instance %s successfully' % instance_id)
            return http.HttpResponseRedirect(url)
        except Exception:
            msg = _('Failed to delete instance %s') % instance_id
            LOG.info(msg)
            exceptions.handle(request, msg, redirect=shortcuts.redirect)


class ConsoleLink(tables.LinkAction):
    name = "console"
    verbose_name = _("Console")
    url = "horizon:project:instances:detail"
    classes = ("btn-console",)
    policy_rules = (("compute", "compute_extension:consoles"),)

    def get_policy_target(self, request, datum=None):
        project_id = None
        if datum:
            project_id = getattr(datum, 'tenant_id', None)
        return {"project_id": project_id}

    def allowed(self, request, instance=None):
        # We check if ConsoleLink is allowed only if settings.CONSOLE_TYPE is
        # not set at all, or if it's set to any value other than None or False.
        # return bool(getattr(settings, 'CONSOLE_TYPE', True)) and
        # instance.status in ACTIVE_STATES and not is_deleting(instance)
        return True

    def get_link_url(self, datum):
        base_url = super(ConsoleLink, self).get_link_url(datum)
        tab_query_string = tabs.ConsoleTab(
            tabs.InstanceDetailTabs).get_query_string()
        return "?".join([base_url, tab_query_string])


class InstancesTable(tables.DataTable):
    name = tables.Column("name",
                         link="horizon:project:instances:detail",
                         verbose_name=_("Instance Name"))
    image_name = tables.Column("image_name", verbose_name=_("Image Name"))
    status = tables.Column("status", verbose_name=_("Status"))
    ip = tables.Column(
        itables.get_ips, verbose_name=_("IP Address"),
        attrs={'data-type': "ip"})

    def get_empty_message(self, *args, **kwargs):
        return "No members in this group, create one"

    class Meta(object):
        name = "instances"
        verbose_name = _("Members")
        table_actions = (LaunchVMLink, RemoveVMLink,)
        row_actions = (ConsoleLink, RemoveVMLink,)


class AddProvidedLink(tables.LinkAction):
    name = "add_policy_rule_set"
    verbose_name = _("Add Policy Rule Set")
    classes = ("ajax-modal", "btn-addvm",)

    def get_link_url(self):
        return reverse("horizon:project:policytargets:add_provided_prs",
                       kwargs={'policy_target_id':
                                   self.table.kwargs['policy_target_id']})


class RemoveProvidedLink(tables.LinkAction):
    name = "remove_policy_rule_set"
    verbose_name = _("Remove Policy Rule Set")
    classes = ("ajax-modal", "btn-addvm",)

    def get_link_url(self):
        return reverse("horizon:project:policytargets:remove_provided_prs",
                       kwargs={'policy_target_id':
                                   self.table.kwargs['policy_target_id']})


class ProvidedContractsTable(tables.DataTable):
    name = gbtables.LinkColumn(
        "name",
        link="horizon:project:application_policy:policy_rule_set_details",
        verbose_name=_("Name"),
        link_rules=((GBP_POLICY_FILE, "get_policy_rule_set"),)
    )
    description = tables.Column("description", verbose_name=_("Description"))
    policy_rules = gbtables.ListColumn(
        "name",
        source_list="policy_rules",
        verbose_name=_("Policy Rules"),
        link="horizon:project:application_policy:policyruledetails",
        list_rules=((GBP_POLICY_FILE, "get_policy_rule"),)
    )

    class Meta(object):
        name = 'provided_policy_rule_sets'
        verbose_name = _("Provided Policy Rule Set")
        table_actions = (AddProvidedLink, RemoveProvidedLink,)


class ExtAddProvidedLink(AddProvidedLink):
    def get_link_url(self):
        return reverse("horizon:project:policytargets:ext_add_provided_prs",
                       kwargs={'ext_policy_target_id':
                                   self.table.kwargs['ext_policy_target_id']})


class ExtRemoveProvidedLink(RemoveProvidedLink):
    def get_link_url(self):
        return reverse("horizon:project:policytargets:ext_remove_provided_prs",
                       kwargs={'ext_policy_target_id':
                                   self.table.kwargs['ext_policy_target_id']})


class ExtProvidedContractsTable(ProvidedContractsTable):
    class Meta(ProvidedContractsTable.Meta):
        table_actions = (ExtAddProvidedLink, ExtRemoveProvidedLink,)


class AddConsumedLink(tables.LinkAction):
    name = "add_consumed"
    verbose_name = _("Add Consumed Policy Rule Set")
    classes = ("ajax-modal", "btn-addvm",)

    def get_link_url(self):
        return reverse("horizon:project:policytargets:add_consumed_prs",
                       kwargs={'policy_target_id':
                                   self.table.kwargs['policy_target_id']})


class RemoveConsumedLink(tables.LinkAction):
    name = "remove_consumed"
    verbose_name = _("Remove Consumed Policy Rule Set")
    classes = ("ajax-modal", "btn-addvm",)

    def get_link_url(self):
        return reverse("horizon:project:policytargets:remove_consumed_prs",
                       kwargs={'policy_target_id':
                                   self.table.kwargs['policy_target_id']})


class ConsumedContractsTable(tables.DataTable):
    name = gbtables.LinkColumn(
        "name",
        link="horizon:project:application_policy:policy_rule_set_details",
        verbose_name=_("Name"),
        link_rules=((GBP_POLICY_FILE, "get_policy_rule_set"),)
    )
    description = tables.Column("description",
                                verbose_name=_("Description"))
    policy_rules = gbtables.ListColumn(
        "name",
        source_list="policy_rules",
        verbose_name=_("Policy Rules"),
        link="horizon:project:application_policy:policyruledetails",
        list_rules=((GBP_POLICY_FILE, "get_policy_rule"),)
    )

    class Meta(object):
        name = 'consumed_policy_rule_sets'
        verbose_name = _("Consumed Policy Rule Set")
        table_actions = (AddConsumedLink, RemoveConsumedLink,)


class ExtAddConsumedLink(AddConsumedLink):
    def get_link_url(self):
        return reverse("horizon:project:policytargets:ext_add_consumed_prs",
                       kwargs={'ext_policy_target_id':
                                   self.table.kwargs['ext_policy_target_id']})


class ExtRemoveConsumedLink(RemoveConsumedLink):
    def get_link_url(self):
        return reverse("horizon:project:policytargets:ext_remove_consumed_prs",
                       kwargs={'ext_policy_target_id':
                                   self.table.kwargs['ext_policy_target_id']})


class ExtConsumedContractsTable(ConsumedContractsTable):
    class Meta(ConsumedContractsTable.Meta):
        table_actions = (ExtAddConsumedLink, ExtRemoveConsumedLink,)
