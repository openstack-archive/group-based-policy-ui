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
from django.utils import html
from django.utils.text import normalize_newlines  # noqa
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_variables  # noqa

from horizon import exceptions
from horizon import forms
from horizon.utils import validators
from horizon import workflows

from openstack_dashboard import api

from openstack_dashboard.dashboards.project.instances.workflows \
    import create_instance as workflows_create_instance

from gbpui import client
from gbpui import fields

LOG = logging.getLogger(__name__)

POLICY_RULE_SET_URL = "horizon:project:application_policy:addpolicy_rule_set"


class SelectPolicyRuleSetAction(workflows.Action):
    provided_policy_rule_set = fields.DynamicMultiChoiceField(
        label=_("Provided Policy Rule Set"),
        help_text=_("Choose a policy rule set for an Group."),
        add_item_link=POLICY_RULE_SET_URL,
        required=False)
    consumed_policy_rule_set = fields.DynamicMultiChoiceField(
        label=_("Consumed Policy Rule Set"),
        help_text=_("Select consumed policy rule set for Group."),
        add_item_link=POLICY_RULE_SET_URL,
        required=False)

    class Meta:
        name = _("Application Policy")
        help_text = _("Select Policy Rule Set for Group.")

    def _policy_rule_set_list(self, request):
        policy_rule_sets = client.policy_rule_set_list(request,
            tenant_id=request.user.tenant_id)
        for c in policy_rule_sets:
            c.set_id_as_name_if_empty()
        policy_rule_sets = sorted(policy_rule_sets,
                                  key=lambda rule: rule.name)
        return [(c.id, c.name) for c in policy_rule_sets]

    def populate_provided_policy_rule_set_choices(self, request, context):
        policy_rule_set_list = []
        try:
            rsets = self._policy_rule_set_list(request)
            if len(rsets) == 0:
                rsets.extend([('None', 'No Provided Policy Rule Sets')])
            policy_rule_set_list = rsets
        except Exception as e:
            policy_rule_set_list = []
            msg = _('Unable to retrieve policy rule set. %s.') % (str(e))
            exceptions.handle(request, msg)
        return policy_rule_set_list

    def populate_consumed_policy_rule_set_choices(self, request, context):
        policy_rule_set_list = []
        try:
            policy_rule_set_list = [('None', 'No Consumed Policy Rule Sets')]
            policy_rule_set_list =\
                self._policy_rule_set_list(request)
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

    class Meta:
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
    external_segments = forms.ChoiceField(
        label=_("External Connectivity"),
        help_text=_("Select external segment for Group."))

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
        ext_seg_list = []
        ext_seg_list.append(data['external_segments'])
        context['external_segments'] = ext_seg_list
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
        if not api.nova.can_set_server_password():
            del self.fields['admin_pass']
            del self.fields['confirm_admin_pass']

    def populate_keypair_choices(self, request, context):
        try:
            keypairs = api.nova.keypair_list(request)
            keypair_list = [(kp.name, kp.name) for kp in keypairs]
        except Exception:
            keypair_list = []
            exceptions.handle(request,
                              _('Unable to retrieve key pairs.'))
        if keypair_list:
            if len(keypair_list) == 1:
                self.fields['keypair'].initial = keypair_list[0][0]
            keypair_list.insert(0, ("", _("Select a key pair")))
        else:
            keypair_list = (("", _("No key pairs available")),)
        return keypair_list

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


class LaunchInstance(workflows.Workflow):
    slug = "create_member"
    name = _("Create Member")
    finalize_button_name = _("Launch")
    success_message = _('Launched %(count)s.')
    multipart = True
    default_steps = (workflows_create_instance.SelectProjectUser,
                     workflows_create_instance.SetInstanceDetails,
                     SetAccessControls,
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
                    dev_mapping_2 = [
                        {'device_name': device_name,
                         'source_type': 'volume',
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
            policy_target_id = self.request.path.split("/")[-2]
            instance_count = int(context['count'])
            count = 1
            while count <= instance_count:
                if instance_count == 1:
                    instance_name = context['name']
                else:
                    instance_name = context['name'] + str(count)
                ep = client.pt_create(
                    request, policy_target_group_id=policy_target_id,
                    name=instance_name[:41] + "_gbpui")
                api.nova.server_create(request,
                                   instance_name,
                                   image_id,
                                   context['flavor'],
                                   context['keypair_id'],
                                   normalize_newlines(custom_script),
                                   security_groups=None,
                                   block_device_mapping=dev_mapping_1,
                                   block_device_mapping_v2=dev_mapping_2,
                                   nics=[{'port-id': ep.port_id}],
                                   availability_zone=avail_zone,
                                   instance_count=1,
                                   admin_pass=context['admin_pass'],
                                   disk_config=context.get('disk_config'),
                                   config_drive=context.get('config_drive'))
                count += 1
            return True
        except Exception:
            error = _("Unable to launch member %(count)s with name %(name)s")
            msg = error % {'count': count, 'name': instance_name}
            LOG.error(msg)
            u = "horizon:project:policytargets:policy_targetdetails"
            redirect = reverse(u, kwargs={'policy_target_id':
                policy_target_id})
            exceptions.handle(request, msg, redirect=redirect)
            return False
