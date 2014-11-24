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
from django.template.defaultfilters import filesizeformat  # noqa
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon import workflows

from openstack_dashboard import api
from openstack_dashboard.dashboards.project.images import utils as imageutils
from openstack_dashboard.dashboards.project.instances import utils

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

    def _policy_rule_set_list(self, request, tenant_id):
        policy_rule_sets = client.policy_rule_set_list(request,
                                                       tenant_id=tenant_id)
        for c in policy_rule_sets:
            c.set_id_as_name_if_empty()
        policy_rule_sets = sorted(policy_rule_sets,
                                  key=lambda rule: rule.name)
        return [(c.id, c.name) for c in policy_rule_sets]

    def populate_provided_policy_rule_set_choices(self, request, context):
        policy_rule_set_list = []
        try:
            tenant_id = self.request.user.tenant_id
            rsets = self._policy_rule_set_list(request, tenant_id)
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
            tenant_id = self.request.user.tenant_id
            policy_rule_set_list = [('None', 'No Consumed Policy Rule Sets')]
            policy_rule_set_list =\
                self._policy_rule_set_list(request, tenant_id)
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
            policies = client.l2policy_list(request)
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
            policies = client.networkservicepolicy_list(
                request, tenant_id=request.user.tenant_id)
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

    def __init__(self, request, *args, **kwargs):
        super(AddPTGAction, self).__init__(request, *args, **kwargs)

    class Meta:
        name = _("Create Group")
        help_text = _("Create a new Group")


class AddPTGStep(workflows.Step):
    action_class = AddPTGAction
    contributes = ("name", "description")

    def contribute(self, data, context):
        context = super(AddPTGStep, self).contribute(data, context)
        return context


class AddPTG(workflows.Workflow):
    slug = "addpolicy_target"
    name = _("Create Group")
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
            group = client.policy_target_create(request, **context)
            return group
        except Exception as e:
            msg = self.format_status_message(self.failure_message) + str(e)
            exceptions.handle(request, msg)
            return False


def _image_choice_title(img):
    gb = filesizeformat(img.size)
    return '%s (%s)' % (img.name or img.id, gb)


class LaunchInstance(workflows.Action):
    availability_zone = forms.ChoiceField(
        label=_("Availability Zone"), required=False)
    name = forms.CharField(label=_("Instance Name"), max_length=255)
    flavor = forms.ChoiceField(
        label=_("Flavor"), help_text=_("Size of image to launch."))
    count = forms.IntegerField(label=_(
        "Instance Count"),
        min_value=1,
        initial=1,
        help_text=_("Number of instances to launch."))
    image = forms.ChoiceField(label=_("Select Image"),
                              widget=forms.SelectWidget(
                                  attrs={'class': 'image-selector'},
                                  data_attrs=('size', 'display-name'),
                                  transform=_image_choice_title))

    def __init__(self, request, *args, **kwargs):
        super(LaunchInstance, self).__init__(request, *args, **kwargs)
        images = imageutils.get_available_images(
            request, request.user.tenant_id)
        choices = [(image.id, image) for image in images]
        if choices:
            choices.insert(0, ("", _("Select Image")))
        else:
            choices.insert(0, ("", _("No images available")))
        zones = self._availability_zone_choices(request)
        self.fields['image'].choices = choices
        self.fields['availability_zone'].choices = zones
        self.fields['flavor'].choices = self._flavor_choices(request)

    def _flavor_choices(self, request):
        flavors = utils.flavor_list(request)
        if flavors:
            return utils.sort_flavor_list(request, flavors)
        return []

    def _availability_zone_choices(self, request):
        try:
            zones = api.nova.availability_zone_list(request)
        except Exception:
            zones = []
            exceptions.handle(
                request, _('Unable to retrieve availability zones.'))
        zone_list = [(zone.zoneName, zone.zoneName)
                     for zone in zones if zone.zoneState['available']]
        zone_list.sort()
        if not zone_list:
            zone_list.insert(0, ("", _("No availability zones found")))
        elif len(zone_list) > 1:
            zone_list.insert(0, ("", _("Any Availability Zone")))
        return zone_list

    def handle(self, request, context):
        policy_target_id = self.request.path.split("/")[-2]
        try:
            msg = _('Member was successfully created.')
            ep = client.pt_create(
                request, policy_target_group_id=policy_target_id)
            api.nova.server_create(request,
                                   context['name'],
                                   context['image'],
                                   context['flavor'],
                                   key_name=None,
                                   user_data=None,
                                   security_groups=None,
                                   instance_count=context['count'],
                                   nics=[{'port-id': ep.port_id}])
            LOG.debug(msg)
            messages.success(request, msg)
        except Exception:
            msg = _('Failed to launch VM')
            LOG.error(msg)
            u = "horizon:project:policytargets:policy_targetdetails"
            redirect = reverse(u, kwargs={'policy_target_id':
                policy_target_id})
            exceptions.handle(request, msg, redirect=redirect)


class LaunchVMStep(workflows.Step):
    action_class = LaunchInstance
    contributes = ("name", "availability_zone", "flavor", "count", "image")

    def contribute(self, data, context):
        context = super(LaunchVMStep, self).contribute(data, context)
        return context


class CreateVM(workflows.Workflow):
    slug = "launch VM"
    name = _("Create Member")

    finalize_button_name = _("Launch")
    success_message = _('Create Member "%s".')
    failure_message = _('Unable to create Member "%s".')
    default_steps = (LaunchVMStep,)
    wizard = True

    def format_status_message(self, message):
        return message % self.context.get('name')

    def get_success_url(self):
        policy_targetid = self.request.path.split("/")[-2]
        u = "horizon:project:policytargets:policy_targetdetails"
        success_url = reverse(u, kwargs={'policy_target_id': policy_targetid})
        return success_url
