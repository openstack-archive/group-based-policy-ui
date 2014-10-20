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
 
class CreateL3PolicyLink(tables.LinkAction):
	name = "create_l3policy"
	verbose_name = _("Create L3 Policy")
	url = "horizon:project:network_policy:addl3policy"
	classes = ("ajax-modal","btn-addl3policy")

class EditL3PolicyLink(tables.LinkAction):
    name = "update_l3policy"
    verbose_name = _("Edit L3Policy")
    classes = ("ajax-modal", "btn-update",)

    def get_link_url(self, l3policy):
        base_url = reverse("horizon:project:network_policy:update_l3policy", kwargs={'l3policy_id': l3policy.id})
        return base_url

class DeleteL3PolicyLink(tables.DeleteAction):
    name = "delete_l3policy"
    action_present = _("Delete")
    action_past = _("Scheduled deletion of %(data_type)s")
    data_type_singular = _("L3Policy")
    data_type_plural = _("L3Policies")
 
class L3PolicyTable(tables.DataTable):
	name = tables.Column("name",
						verbose_name=_("Name"),
						link="horizon:project:network_policy:l3policy_details")
	description = tables.Column("description", verbose_name=_("Description"))
	id = tables.Column("id", verbose_name=_("ID"))
	ip_version = tables.Column("ip_version",verbose_name=_("IP Version"))
	ip_pool = tables.Column("ip_pool",verbose_name=_("IP Pool"))
	subnet_prefix_length = tables.Column("subnet_prefix_length",verbose_name=_("Subnet Prefix Length"))

	class Meta:
		name = "l3policy_table"
		verbose_name = _("L3 Policy")
		table_actions = (CreateL3PolicyLink,DeleteL3PolicyLink,)
		row_actions = (EditL3PolicyLink,DeleteL3PolicyLink,)
 
