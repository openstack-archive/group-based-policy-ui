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
import re

from django.conf import settings
from django.core.urlresolvers import reverse
from django import shortcuts
from django.utils import html
from django.utils.text import normalize_newlines  # noqa
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_variables  # noqa

from horizon import exceptions
from horizon import forms
from horizon.utils import validators
from horizon import workflows

from openstack_dashboard import api

from openstack_dashboard.dashboards.project.instances \
    import utils as instance_utils
from openstack_dashboard.dashboards.project.instances.workflows \
    import create_instance as workflows_create_instance

from gbpui import client
from gbpui import fields

from netaddr import IPAddress
from netaddr import IPNetwork


LOG = logging.getLogger(__name__)

POLICY_RULE_SET_URL = "horizon:project:application_policy:addpolicy_rule_set"
ADD_EXTERNAL_CONNECTIVITY = \
    "horizon:project:network_policy:create_external_connectivity"


class SelectPolicyRuleSetAction(workflows.Action):
    provided_policy_rule_set = fields.TransferTableField(
        label=_("Provided Policy Rule Set"),
        help_text=_("Choose a policy rule set for an Group."),
        add_item_link=POLICY_RULE_SET_URL,
        required=False)
    consumed_policy_rule_set = fields.TransferTableField(
        label=_("Consumed Policy Rule Set"),
        help_text=_("Select consumed policy rule set for Group."),
        add_item_link=POLICY_RULE_SET_URL,
        required=False)

    class Meta(object):
        name = _("Application Policy")
        help_text = _("Select Policy Rule Set for Group.")

    def _policy_rule_set_list(self, request):
        policy_rule_sets = client.policy_rule_set_list(
            request,
            tenant_id=request.user.tenant_id
        )
        for c in policy_rule_sets:
            c.set_id_as_name_if_empty()
        policy_rule_sets = sorted(policy_rule_sets,
                                  key=lambda rule: rule.name)
        return [(c.id, c.name) for c in policy_rule_sets]

    def populate_provided_policy_rule_set_choices(self, request, context):
        policy_rule_set_list = []
        try:
            policy_rule_set_list = self._policy_rule_set_list(request)
        except Exception as e:
            msg = _('Unable to retrieve policy rule set. %s.') % (str(e))
            exceptions.handle(request, msg)
        return policy_rule_set_list

    def populate_consumed_policy_rule_set_choices(self, request, context):
        policy_rule_set_list = []
        try:
            policy_rule_set_list = self._policy_rule_set_list(request)
        except Exception as e:
            msg = _('Unable to retrieve policy rule set. %s.') % (str(e))
            exceptions.handle(request, msg)
        return policy_rule_set_list


class SelectL2policyAction(workflows.Action):
    l2policy_id = forms.ChoiceField(
        label=_("Network Policy"),
        help_text=_("Select network policy for Group."))
    network_service_policy_id = forms.ChoiceField(
        label=_("Network Services Policy"),
        help_text=_("Select network services policy for Group."),
        required=False)

    class Meta(object):
        name = _("Network Policy")
        help_text = _(
            "Select network policy for Group."
            "Selecting default will create an Network Policy implicitly.")

    def populate_l2policy_id_choices(self, request, context):
        policies = []
        try:
            policies = client.l2policy_list(request,
                tenant_id=request.user.tenant_id)
            for p in policies:
                p.set_id_as_name_if_empty()
            policies = sorted(policies, key=lambda rule: rule.name)
            policies = [(p.id, p.name + ":" + p.id) for p in policies]
            policies.insert(0, ('default', 'Default'))
        except Exception as e:
            exceptions.handle(request,
                              _("Unable to retrieve policies (%(error)s).")
                              % {'error': str(e)})
        return policies

    def populate_network_service_policy_id_choices(self, request, context):
        policies = []
        try:
            policies = client.networkservicepolicy_list(request,
                tenant_id=request.user.tenant_id)
            for p in policies:
                p.set_id_as_name_if_empty()
            policies = [(p.id, p.name + ":" + p.id) for p in policies]
            policies.insert(0, ('None', 'No Network Service Policy'))
        except Exception as e:
            msg = _("Unable to retrieve service policies. %s).") % (str(e))
            exceptions.handle(request, msg)
        return policies


class SelectL2policyStep(workflows.Step):
    action_class = SelectL2policyAction
    name = _("L2 Policy")
    contributes = ("l2policy_id", "network_services_policy_id",)

    def contribute(self, data, context):
        if data['l2policy_id'] != 'default':
            context['l2_policy_id'] = data['l2policy_id']
        if data['network_service_policy_id'] != 'None':
            context['network_service_policy_id'] = \
                data['network_service_policy_id']
        return context


class SelectPolicyRuleSetStep(workflows.Step):
    action_class = SelectPolicyRuleSetAction
    name = _("Provided Policy Rule Set")
    contributes = ("provided_policy_rule_sets", "consumed_policy_rule_sets",)

    def contribute(self, data, context):
        if data:
            policy_rule_sets = self.workflow.request.POST.getlist(
                "provided_policy_rule_set")
            if policy_rule_sets:
                policy_rule_set_dict = {}
                for policy_rule_set in policy_rule_sets:
                    if policy_rule_set != 'None':
                        policy_rule_set_dict[policy_rule_set] = None
                context['provided_policy_rule_sets'] = policy_rule_set_dict
            policy_rule_sets = self.workflow.request.POST.getlist(
                "consumed_policy_rule_set")
            if policy_rule_sets:
                policy_rule_set_dict = {}
                for policy_rule_set in policy_rule_sets:
                    if policy_rule_set != 'None':
                        policy_rule_set_dict[policy_rule_set] = None
                context['consumed_policy_rule_sets'] = policy_rule_set_dict
            return context


class AddPTGAction(workflows.Action):
    name = forms.CharField(max_length=80,
                           label=_("Name"))
    description = forms.CharField(max_length=80,
                                  label=_("Description"),
                                  required=False)
    shared = forms.BooleanField(label=_("Shared"),
                                initial=False, required=False)

    def __init__(self, request, *args, **kwargs):
        super(AddPTGAction, self).__init__(request, *args, **kwargs)

    class Meta(object):
        name = _("Group")
        help_text = _("Create Internal Group")


class AddPTGStep(workflows.Step):
    action_class = AddPTGAction
    contributes = ("name", "description", "shared")

    def contribute(self, data, context):
        context = super(AddPTGStep, self).contribute(data, context)
        return context


class AddPTG(workflows.Workflow):
    slug = "addpolicy_target"
    name = _("Create Internal Group")
    finalize_button_name = _("Create")
    success_message = _('Create Group "%s".')
    failure_message = _('Unable to create Group "%s".')
    success_url = "horizon:project:policytargets:index"
    default_steps = (AddPTGStep,
                     SelectPolicyRuleSetStep,
                     SelectL2policyStep,)
    wizard = True

    def format_status_message(self, message):
        return message % self.context.get('name')

    def handle(self, request, context):
        try:
            if context.get('name'):
                context['name'] = html.escape(context['name'])
            if context.get('description'):
                context['description'] = html.escape(context['description'])
            group = client.policy_target_create(request, **context)
            return group
        except Exception as e:
            msg = self.format_status_message(self.failure_message) + str(e)
            exceptions.handle(request, msg)
            return False


class ExternalConnectivityAction(workflows.Action):
    external_segments = fields.DynamicMultiChoiceField(
        label=_("External Connectivity"),
        required=True,
        add_item_link=ADD_EXTERNAL_CONNECTIVITY,
        help_text=_("Select external segment(s) for Group."))

    class Meta(object):
        name = _("External Connectivity")
        help_text = _(
            "Select External Connectivity for Group.")

    def populate_external_segments_choices(self, request, context):
        external_connectivities = []
        try:
            external_connectivities = client.externalconnectivity_list(
                request, tenant_id=request.user.tenant_id)
            for p in external_connectivities:
                p.set_id_as_name_if_empty()
            ext_conn_list = sorted(external_connectivities,
                key=lambda segment: segment.name)
            ext_conn_list = \
                [(p.id, p.name + ":" + p.id) for p in ext_conn_list]
        except Exception as e:
            exceptions.handle(request,
                              _("Unable to retrieve policies (%(error)s).")
                              % {'error': str(e)})
        return ext_conn_list


class ExternalConnectivityStep(workflows.Step):
    action_class = ExternalConnectivityAction
    name = _("External Connectivity")
    contributes = ("external_segments",)

    def contribute(self, data, context):
        context['external_segments'] = data.get('external_segments', [])
        return context


class ExtAddPTGAction(workflows.Action):
    name = forms.CharField(max_length=80,
                           label=_("Name"))
    description = forms.CharField(max_length=80,
                                  label=_("Description"),
                                  required=False)
    shared = forms.BooleanField(label=_("Shared"),
                                initial=False, required=False)

    def __init__(self, request, *args, **kwargs):
        super(ExtAddPTGAction, self).__init__(request, *args, **kwargs)

    class Meta(object):
        name = _("Group")
        help_text = _("Create External Group")


class ExtAddPTGStep(workflows.Step):
    action_class = ExtAddPTGAction
    contributes = ("name", "description", "shared")

    def contribute(self, data, context):
        context = super(ExtAddPTGStep, self).contribute(data, context)
        return context


class AddExternalPTG(workflows.Workflow):
    slug = "addexternal_policy_target"
    name = _("Create External Group")
    finalize_button_name = _("Create")
    success_message = _('Create External Group "%s".')
    failure_message = _('Unable to create External Group "%s".')
    success_url = "horizon:project:policytargets:index"
    default_steps = (ExtAddPTGStep,
                     SelectPolicyRuleSetStep,
                     ExternalConnectivityStep,)
    wizard = True

    def format_status_message(self, message):
        return message % self.context.get('name')

    def handle(self, request, context):
        try:
            if context.get('name'):
                context['name'] = html.escape(context['name'])
            if context.get('description'):
                context['description'] = html.escape(context['description'])
            group = client.ext_policy_target_create(request, **context)
            return group
        except Exception as e:
            msg = self.format_status_message(self.failure_message) + str(e)
            exceptions.handle(request, msg)
            return False


KEYPAIR_IMPORT_URL = "horizon:project:access_and_security:keypairs:import"


class SetAccessControlsAction(workflows.Action):
    keypair = forms.DynamicChoiceField(label=_("Key Pair"),
                                       required=False,
                                       help_text=_("Key pair to use for "
                                                   "authentication."),
                                       add_item_link=KEYPAIR_IMPORT_URL)

    admin_pass = forms.RegexField(
        label=_("Admin Password"),
        required=False,
        widget=forms.PasswordInput(render_value=False),
        regex=validators.password_validator(),
        error_messages={'invalid': validators.password_validator_msg()})
    confirm_admin_pass = forms.CharField(
        label=_("Confirm Admin Password"),
        required=False,
        widget=forms.PasswordInput(render_value=False))

    class Meta(object):
        name = _("Access & Security")
        help_text = _("Control access to your instance via key pairs "
                      "and other mechanisms.")

    def __init__(self, request, *args, **kwargs):
        super(SetAccessControlsAction, self).__init__(request, *args, **kwargs)
        self.fields['keypair'].choices = instance_utils.keypair_field_data(
            request, True)
        if not api.nova.can_set_server_password():
            del self.fields['admin_pass']
            del self.fields['confirm_admin_pass']

    def clean(self):
        '''Check to make sure password fields match.'''
        cleaned_data = super(SetAccessControlsAction, self).clean()
        if 'admin_pass' in cleaned_data:
            if cleaned_data['admin_pass'] != cleaned_data.get(
                    'confirm_admin_pass', None):
                raise forms.ValidationError(_('Passwords do not match.'))
        return cleaned_data


class SetAccessControls(workflows.Step):
    action_class = SetAccessControlsAction
    depends_on = ("project_id", "user_id")
    contributes = ("keypair_id", "security_group_ids",
                   "admin_pass", "confirm_admin_pass")

    def contribute(self, data, context):
        if data:
            post = self.workflow.request.POST
            context['security_group_ids'] = post.getlist("groups")
            context['keypair_id'] = data.get("keypair", "")
            context['admin_pass'] = data.get("admin_pass", "")
            context['confirm_admin_pass'] = data.get("confirm_admin_pass", "")
        return context


class SetGroupAction(workflows.Action):
    # To reuse horizon instance launch code related to Networking,
    # form filed must be 'network' only
    network = fields.CustomMultiChoiceField(label=_("Groups"),
                                        widget=forms.CheckboxSelectMultiple(),
                                        error_messages={
                                            'required': _(
                                                "At least one group must"
                                                " be specified.")},
                                        help_text=_("Launch member instance in"
                                                    " these groups"))

    widget = forms.HiddenInput()

    def __init__(self, request, *args, **kwargs):
        super(SetGroupAction, self).__init__(request, *args, **kwargs)
        policy_targetid = self.request.path.split("/")[-2]
        ptg = client.policy_target_get(request, policy_targetid)
        for choice in self.fields['network'].choices:
            if choice[0].startswith(ptg.id):
                initial_value = choice[0]
                break
        self.fields['network'].initial = [initial_value]

    class Meta(object):
        name = _("Groups")

    def clean(self):
        cleaned_data = super(SetGroupAction, self).clean()
        if not cleaned_data.get("network", None):
            raise forms.ValidationError(_(
                'At least one group must be selected.'))
        return cleaned_data

    def populate_network_choices(self, request, context):
        try:
            pt_list = []
            pts = client.policy_target_list(request,
                tenant_id=request.user.tenant_id)
            proxy_groups = [pt.get('proxy_group_id') for pt in pts
                            if pt.get('proxy_group_id')]
            for pt in pts:
                if hasattr(settings,
                           'GBPUI_HIDE_PTG_NAMES_FROM_MEMBER_CREATE'):
                    regexs = "(" + ")|(".join(
                        settings.GBPUI_HIDE_PTG_NAMES_FROM_MEMBER_CREATE) \
                        + ")"
                    if re.match(regexs, pt.get('name')):
                        continue
                if pt.id in proxy_groups or pt.get('proxied_group_id'):
                    continue
                pt.set_id_as_name_if_empty()
                subnet_dedails = None
                for subnet_id in pt.subnets:
                    try:
                        subnet = api.neutron.subnet_get(request, subnet_id)
                        subnet_name = subnet.name.split("_")
                        if subnet_name[-1] in proxy_groups:
                            continue
                        if subnet_dedails is None:
                            subnet_dedails = subnet['cidr']
                        else:
                            subnet_dedails += ";" + subnet['cidr']
                        allocation_pools = subnet['allocation_pools']
                        if allocation_pools:
                            start = allocation_pools[0]['start']
                            end = allocation_pools[0]['end']
                            subnet_dedails = subnet_dedails + "," + start
                            subnet_dedails = subnet_dedails + "," + end
                    except Exception as e:
                        LOG.error(str(e))
                        pass
                pt.id = pt.id + ":" + subnet_dedails
                pt_list.append((pt.id, pt.name))
            return sorted(pt_list, key=lambda obj: obj[1])
        except Exception:
            msg = _("Failed to retrieve groups")
            LOG.error(msg)
            exceptions.handle(request, msg, redirect=shortcuts.redirect)


class SetGroup(workflows.Step):
    action_class = SetGroupAction

    template_name = "project/policytargets/_update_groups.html"
    contributes = ("group_id",)

    def contribute(self, data, context):
        if data:
            groups = self.workflow.request.POST.getlist("network")
            groups = [n for n in groups if n != '']
            if groups:
                context['group_id'] = groups

        return context


class LaunchInstance(workflows.Workflow):
    slug = "create_member"
    name = _("Create Member")
    finalize_button_name = _("Launch")
    success_message = _('Launched %(count)s.')
    multipart = True
    default_steps = (workflows_create_instance.SelectProjectUser,
                     workflows_create_instance.SetInstanceDetails,
                     SetAccessControls,
                     SetGroup,
                     workflows_create_instance.PostCreationStep,
                     workflows_create_instance.SetAdvanced)

    def format_status_message(self, message):
        count = self.context.get('count', 1)
        if int(count) > 1:
            return message % {"count": _("%s members") % count}
        else:
            return message % {"count": _("member")}

    def get_success_url(self):
        policy_targetid = self.request.path.split("/")[-2]
        u = "horizon:project:policytargets:policy_targetdetails"
        success_url = reverse(u, kwargs={'policy_target_id': policy_targetid})
        return success_url

    @sensitive_variables('context')
    def handle(self, request, context):
        custom_script = context.get('script_data', '')
        dev_mapping_1 = None
        dev_mapping_2 = None

        image_id = ''

        # Determine volume mapping options
        source_type = context.get('source_type', None)
        if source_type in ['image_id', 'instance_snapshot_id']:
            image_id = context['source_id']
        elif source_type in ['volume_id', 'volume_snapshot_id']:
            try:
                if api.nova.extension_supported("BlockDeviceMappingV2Boot",
                                                request):
                    # Volume source id is extracted from the source
                    volume_source_id = context['source_id'].split(':')[0]
                    device_name = context.get('device_name', '') \
                        .strip() or None
                    dev_source_type_mapping = {
                        'volume_id': 'volume',
                        'volume_snapshot_id': 'snapshot'
                    }
                    dev_mapping_2 = [
                        {'device_name': device_name,
                         'source_type': dev_source_type_mapping[source_type],
                         'destination_type': 'volume',
                         'delete_on_termination':
                             int(bool(context['delete_on_terminate'])),
                         'uuid': volume_source_id,
                         'boot_index': '0',
                         'volume_size': context['volume_size']
                         }
                    ]
                else:
                    dev_mapping_1 = {context['device_name']: '%s::%s' %
                                     (context['source_id'],
                                     int(bool(context['delete_on_terminate'])))
                                     }
            except Exception:
                msg = _('Unable to retrieve extensions information')
                exceptions.handle(request, msg)

        elif source_type == 'volume_image_id':
            device_name = context.get('device_name', '').strip() or None
            dev_mapping_2 = [
                {'device_name': device_name,  # None auto-selects device
                 'source_type': 'image',
                 'destination_type': 'volume',
                 'delete_on_termination':
                     int(bool(context['delete_on_terminate'])),
                 'uuid': context['source_id'],
                 'boot_index': '0',
                 'volume_size': context['volume_size']
                 }
            ]
        avail_zone = context.get('availability_zone', None)
        try:
            instance_count = int(context['count'])
            count = 1
            while count <= instance_count:
                if instance_count == 1:
                    instance_name = context['name']
                else:
                    instance_name = context['name'] + str(count)
                nics = []
                pts = []
                for ptg_id in context['group_id']:
                    values = ptg_id.split(":")
                    ptg_id = values[0]
                    args = {'policy_target_group_id': ptg_id,
                            'name': instance_name[:41] + "_gbpui"}
                    if len(values) == 3:
                        ptg = client.policy_target_get(request, ptg_id)
                        fixed_ip = values[2]
                        for subnet_id in ptg.subnets:
                            try:
                                subnet = api.neutron.subnet_get(
                                    request, subnet_id)
                            except Exception:
                                continue
                            if IPAddress(fixed_ip) in \
                                    IPNetwork(subnet['cidr']):
                                args['fixed_ips'] = [
                                    {'subnet_id': subnet['id'],
                                     'ip_address': fixed_ip}]
                                break
                    ep = client.pt_create(request, **args)
                    nics.append({'port-id': ep.port_id})
                    pts.append(ep.id)
                meta_data = {'pts': ','.join(pts)}
                api.nova.server_create(request,
                                   instance_name,
                                   image_id,
                                   context['flavor'],
                                   context['keypair_id'],
                                   normalize_newlines(custom_script),
                                   security_groups=None,
                                   block_device_mapping=dev_mapping_1,
                                   block_device_mapping_v2=dev_mapping_2,
                                   nics=nics,
                                   availability_zone=avail_zone,
                                   instance_count=1,
                                   admin_pass=context['admin_pass'],
                                   disk_config=context.get('disk_config'),
                                   config_drive=context.get('config_drive'),
                                   meta=meta_data)
                count += 1
            return True
        except Exception as e:
            error = _("Unable to launch member %(count)s with name %(name)s")
            msg = error % {'count': count, 'name': instance_name}
            LOG.error(str(e))
            u = "horizon:project:policytargets:policy_targetdetails"
            policy_target_id = self.request.path.split("/")[-2]
            redirect = reverse(u, kwargs={'policy_target_id':
                policy_target_id})
            exceptions.handle(request, msg, redirect=redirect)
            return False
