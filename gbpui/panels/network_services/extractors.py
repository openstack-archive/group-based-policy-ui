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

import os

from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe


# todo: The HTML construction here is less than desirable
#       ...a template solution might be preferable
def get_node_content(datum):
    static_url = getattr(settings, 'STATIC_URL', "/static/")
    img_path = static_url + "dashboard/img/"

    ds_path = "/opt/stack/horizon/static/dashboard/img/"
    local_img_path = ds_path if os.path.exists(ds_path) \
        else "/usr/share/openstack-dashboard/openstack_dashboard/" \
             "static/dashboard/img/"

    provider = "default"
    if os.path.exists(local_img_path):
        providers = os.listdir(local_img_path)
        for p in providers:
            if p in datum.description:
                provider = p
                break

    img_src = img_path + provider + "/"

    table = ["<table class='table table-condensed' style='margin-bottom:0px'>"]
    table.append("<tr><td>")
    table.append("<span class='glyphicon glyphicon-remove-circle'></span>")

    for node in datum.loaded_nodes:
        table.append(
            "<td><span class='glyphicon glyphicon-arrow-right'></span></td>"
        )
        table.append("<td>")
        table.append("<img src='")
        table.append(img_src)
        table.append(node.service_profile.service_type)
        table.append(".png'>")
        table.append("<br>")

        if not node.can_access:
            table.append("<span style='font-size: 9px;'>")
            table.append(node.name)
            table.append(" (")
            table.append(node.service_profile.service_type)
            table.append(")")
            table.append("</span>")
        else:
            url = reverse(
                "horizon:project:network_services:sc_node_details",
                kwargs={'scnode_id': node.id}
            )

            table.append("<a href='")
            table.append(url)
            table.append("' style='font-size: 9px;'>")
            table.append(node.name)
            table.append(" (")
            table.append(node.service_profile.service_type)
            table.append(")")
            table.append("</a>")

        table.append("</td>")
    table.append("</tr>")
    table.append("</table>")
    return mark_safe("".join(table))


def get_profile_link(datum):
    return reverse("horizon:project:network_services:service_profile_details",
                   kwargs={'sp_id': datum.service_profile_id})


def get_profile_name(datum):
    return datum.service_profile.name + ": " + \
        datum.service_profile.service_type


def get_profile_policy_target(datum):
    return {"project_id": datum.service_profile.tenant_id}
