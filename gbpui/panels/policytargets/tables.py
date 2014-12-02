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

from horizon import exceptions
from horizon import tables

from openstack_dashboard import api
from openstack_dashboard.dashboards.project.instances import tables as itables
from openstack_dashboard.dashboards.project.instances import tabs

LOG = logging.getLogger(__name__)


class UpdatePTGLink(tables.LinkAction):
    name = "updatepolicy_target"
    verbose_name = _("Edit")
    classes = ("ajax-modal", "btn-update",)

    def get_link_url(self, policy_target):
        u = "horizon:project:policytargets:updatepolicy_target"
        base_url = reverse(u, kwargs={'policy_target_id': policy_target.id})
        return base_url


class DeletePTGLink(tables.DeleteAction):
    name = "deletepolicy_target"
    action_present = _("Delete")
    action_past = _("Scheduled deletion of %(data_type)s")
    data_type_singular = _("Group")
    data_type_plural = _("Groups")


class AddPTGLink(tables.LinkAction):
    name = "addpolicy_target"
    verbose_name = _("Create Group")
    url = "horizon:project:policytargets:addpolicy_target"
    classes = ("ajax-modal", "btn-addpolicy_target",)


class PTGsTable(tables.DataTable):
    name = tables.Column("name",
                    verbose_name=_("Name"),
                    link="horizon:project:policytargets:policy_targetdetails")
    description = tables.Column("description", verbose_name=_("Description"))
    provided_policy_rule_sets = tables.Column("provided_policy_rule_sets",
                                         sortable=False,
                                         verbose_name=_("Provided Rule Sets"))
    consumed_policy_rule_sets = tables.Column("consumed_policy_rule_sets",
                                         sortable=False,
                                         verbose_name=_("Consumed Rule Sets"))
    l2_policy_id = tables.Column("l2_policy_id",
                                 verbose_name=_("L2 Policy"))

    class Meta:
        name = "policy_targetstable"
        verbose_name = _("Groups")
        table_actions = (AddPTGLink, DeletePTGLink)
        row_actions = (UpdatePTGLink, DeletePTGLink)


class LaunchVMLink(tables.LinkAction):
    name = "launch_vm"
    verbose_name = _("Create Member")
    classes = ("ajax-modal", "btn-addvm",)

    def get_link_url(self):
        return reverse("horizon:project:policytargets:addvm",
               kwargs={'policy_target_id':
                   self.table.kwargs['policy_target_id']})


class RemoveVMLink(tables.DeleteAction):
    data_type_singular = _("Instance")
    data_type_plural = _("Instances")

    def delete(self, request, instance_id):
        url = reverse("horizon:project:policytargets:policy_targetdetails",
                      kwargs={'policy_target_id':
                          self.table.kwargs['policy_target_id']})
        try:
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

    class Meta:
        name = "instances"
        verbose_name = _("Members")
        table_actions = (LaunchVMLink,)
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
    name = tables.Column("name",
             link="horizon:project:application_policy:policy_rule_set_details",
             verbose_name=_("Name"))
    description = tables.Column("description", verbose_name=_("Description"))
    policy_rules = tables.Column("policy_rules",
                                 sortable=False,
                                 verbose_name=_("Policy Rules"))

    class Meta:
        name = 'provided_policy_rule_sets'
        verbose_name = _("Provided Policy Rule Set")
        table_actions = (AddProvidedLink, RemoveProvidedLink,)


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
    name = tables.Column("name",
             link="horizon:project:application_policy:policy_rule_set_details",
             verbose_name=_("Name"))
    description = tables.Column("description",
                                verbose_name=_("Description"))
    policy_rules = tables.Column("policy_rules",
                                 sortable=False,
                                 verbose_name=_("Policy Rules"))

    class Meta:
        name = 'consumed_policy_rule_sets'
        verbose_name = _("Consumed Policy Rule Set")
        table_actions = (AddConsumedLink, RemoveConsumedLink,)
