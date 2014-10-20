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

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django import http

from horizon import tables
from horizon.utils import filters

from openstack_dashboard.dashboards.project.instances.tables import *
import pdb

class UpdateEPGLink(tables.LinkAction):
    name = "updateepg"
    verbose_name = _("Edit EPG")
    classes = ("ajax-modal", "btn-update",)

    def get_link_url(self, epg):
        base_url = reverse("horizon:project:endpoint_groups:updateepg", kwargs={'epg_id': epg.id})
        return base_url


class DeleteEPGLink(tables.DeleteAction):
    name = "deleteepg"
    action_present = _("Delete")
    action_past = _("Scheduled deletion of %(data_type)s")
    data_type_singular = _("Group")
    data_type_plural = _("Groups")


class AddEPGLink(tables.LinkAction):
    name = "addepg"
    verbose_name = _("Create Group")
    url = "horizon:project:endpoint_groups:addepg"
    classes = ("ajax-modal", "btn-addepg",)


class EPGsTable(tables.DataTable):
    name = tables.Column("name",
                         verbose_name=_("Name"),
                         link="horizon:project:endpoint_groups:epgdetails")

    class Meta:
        name = "epgstable"
        verbose_name = _("Groups")
        table_actions = (AddEPGLink, DeleteEPGLink)
        row_actions = (UpdateEPGLink, DeleteEPGLink)

	pass

class CreateL2PolicyLink(tables.LinkAction):
	name = "add_l2policy"
	verbose_name = _("Create L2 Policy")
	url = "horizon:project:endpoint_groups:addl2policy"
	classes = ("ajax-modal","btn-addl2policy")


class EditL2PolicyLink(tables.LinkAction):
    name = "update_l2policy"
    verbose_name = _("Edit L2Policy")
    classes = ("ajax-modal", "btn-update",)

    def get_link_url(self, l2policy):
        base_url = reverse("horizon:project:endpoint_groups:update_l2policy", kwargs={'l2policy_id': l2policy.id})
        return base_url

class DeleteL2PolicyLink(tables.DeleteAction):
    name = "delete_l2policy"
    action_present = _("Delete")
    action_past = _("Scheduled deletion of %(data_type)s")
    data_type_singular = _("L2Policy")
    data_type_plural = _("L2Policies")
 

class L2PolicyTable(tables.DataTable):
	name = tables.Column("name",
						verbose_name=_("Name"),
						link="horizon:project:endpoint_groups:l2policy_details")
	description = tables.Column("description", verbose_name=_("Description"))
	id = tables.Column("id", verbose_name=_("ID"))
	l3_policy_id = tables.Column("l3_policy_id", verbose_name=_("L3 Policy ID"))

	class Meta:
		name = "l2policy_table"
		verbose_name = _("L2 Policy")
		table_actions = (CreateL2PolicyLink,DeleteL2PolicyLink)
		row_actions = (EditL2PolicyLink,DeleteL2PolicyLink)

class LaunchVMLink(tables.LinkAction):
    name = "launch_vm"
    verbose_name = _("Create Member")
    classes = ("ajax-modal", "btn-addvm",)
    
    def get_link_url(self):
        return reverse("horizon:project:endpoint_groups:addvm", kwargs={'epg_id': self.table.kwargs['epg_id']})

class RemoveVMLink(tables.DeleteAction):
    data_type_singular = _("Instance")
    data_type_plural = _("Instances")
 
    
    def delete(self, request, instance_id):
        url = reverse("horizon:project:endpoint_groups:epgdetails", kwargs={'epg_id': self.table.kwargs['epg_id']}) 
        try:
            api.nova.server_delete(request, instance_id)
            LOG.debug('Deleted instance %s successfully' % instance_id)
            return http.HttpResponseRedirect(url)
        except Exception:
            msg = _('Failed to delete instance %s') % instance_id
            LOG.info(msg)
            exceptions.handle(request, msg, redirect=redirect) 
        redirect = url

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
        #return bool(getattr(settings, 'CONSOLE_TYPE', True)) and instance.status in ACTIVE_STATES and not is_deleting(instance)
        return True

    def get_link_url(self, datum):
        base_url = super(ConsoleLink, self).get_link_url(datum)
        tab_query_string = tabs.ConsoleTab(
            tabs.InstanceDetailTabs).get_query_string()
        return "?".join([base_url, tab_query_string])
 


class InstancesTable(tables.DataTable):
    name = tables.Column("name", link="horizon:project:instances:detail", verbose_name=_("Instance Name"))
    image_name = tables.Column("image_name", verbose_name=_("Image Name"))
    status = tables.Column("status", verbose_name=_("Status"))
    ip = tables.Column(get_ips, verbose_name=_("IP Address"), attrs={'data-type': "ip"})


    class Meta:
        name = "instances"
        verbose_name = _("Members")
        table_actions = (LaunchVMLink,)
        row_actions = (ConsoleLink,RemoveVMLink,)

class AddContractLink(tables.LinkAction):
     name = "add_contract"
     verbose_name = _("Add Contract")
     classes = ("ajax-modal", "btn-addvm",)
     
     def get_link_url(self):
        return reverse("horizon:project:endpoint_groups:add_contract", kwargs={'epg_id': self.table.kwargs['epg_id']}) 

class RemoveContractLink(tables.LinkAction):
     name = "remove_contract"
     verbose_name = _("Remove Contract")
     classes = ("ajax-modal", "btn-addvm",)
     
     def get_link_url(self):
        return reverse("horizon:project:endpoint_groups:remove_contract", kwargs={'epg_id': self.table.kwargs['epg_id']}) 
 
class ProvidedContractsTable(tables.DataTable):
    name = tables.Column("name", link="horizon:project:contracts:contractdetails", verbose_name=_("Contract Name"))
    
    class Meta:
        name = 'provided_contracts'
        verbose_name = _("Provided Contracts")
        table_actions = (AddContractLink,RemoveContractLink,) 


class AddConsumedLink(tables.LinkAction):
     name = "add_consumed"
     verbose_name = _("Add Contract")
     classes = ("ajax-modal", "btn-addvm",)
     
     def get_link_url(self):
        return reverse("horizon:project:endpoint_groups:add_consumed", kwargs={'epg_id': self.table.kwargs['epg_id']})

class RemoveConsumedLink(tables.LinkAction):
     name = "remove_consumed"
     verbose_name = _("Remove Contract")
     classes = ("ajax-modal", "btn-addvm",)
     
     def get_link_url(self):
        return reverse("horizon:project:endpoint_groups:remove_consumed", kwargs={'epg_id': self.table.kwargs['epg_id']})

class ConsumedContractsTable(tables.DataTable):
    name = tables.Column("name",
            link="horizon:project:contracts:contractdetails", verbose_name=_("Contract Name"))
    description = tables.Column("description",verbose_name=_("Description"))

    class Meta:
        name = 'consumed_contracts'
        verbose_name = _("Consumed Contracts")
        table_actions = (AddConsumedLink,RemoveConsumedLink,)
