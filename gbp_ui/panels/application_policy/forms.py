from django.core.urlresolvers import reverse
from django.template.defaultfilters import filesizeformat  # noqa
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_variables  # noqa
from django import http

from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon.utils import validators

from gbp_ui import client

PROTOCOLS = [('tcp', _('TCP')), ('udp', _('UDP')), ('icmp', _('ICMP')), ('any', _('ANY'))]
DIRECTIONS = [('in', _('IN')), ('out', _('OUT')), ('bi', _('BI'))]

class UpdateContractForm(forms.SelfHandlingForm):
    name = forms.CharField(label=_("Name"))
    description = forms.CharField(label=_("Description"),required=False)
    rules = forms.MultipleChoiceField(label=_("Policy Rules"),)

    def __init__(self, request, *args, **kwargs):
        super(UpdateContractForm, self).__init__(request, *args, **kwargs)
        rules = []
        try:
            items = client.policyrule_list(request)
            rules = [(p.id,p.name) for p in items]
            contract = client.contract_get(request, self.initial['contract_id'])
            if contract:
                self.fields['name'].initial = contract.name
                self.fields['description'].initial = contract.description
                existing = [item for item in contract.policy_rules]
                self.fields['rules'].initial = existing
        except Exception as e:
            exceptions.handle(request, _('Unable to retrieve policy rules'))
        self.fields['rules'].choices = rules
    
    def handle(self,request,context):
        try:
            contract_id = self.initial['contract_id']
            con = client.contract_update(request, 
                                                  contract_id,
                                                  name=context['name'],
                                                  description=context['description'],
                                                  policy_rules=context['rules'],
                                                  )
            messages.success(request, _('Contract successfully updated.'))
            url = reverse('horizon:project:application_policy:index')
            return http.HttpResponseRedirect(url)
        except Exception as e:
            redirect = reverse('horizon:project:contracts:index')
            exceptions.handle(request, _("Unable to update contract."), redirect=redirect)

class UpdatePolicyActionForm(forms.SelfHandlingForm):
    name = forms.CharField(label=_("Name"))
    description = forms.CharField(label=_("Description"),required=False)
    action_type = forms.ChoiceField(label=_("Action"))
    action_value = forms.CharField(label=_("Action Value"),required=False)

    def __init__(self, request, *args, **kwargs):
        super(UpdatePolicyActionForm, self).__init__(request, *args, **kwargs)

        try:
            policyaction_id = self.initial['policyaction_id']
            pa = client.policyaction_get(request, policyaction_id)
            self.fields['name'].initial = pa.name
            self.fields['action_value'].initial = pa.action_value
            self.fields['action_type'].initial = pa.action_type
        except Exception as e:
            pass
        self.fields['action_type'].choices = [('allow', _('ALLOW')), ('redirect', _('REDIRECT'))]
    
    def handle(self,request,context):
        url = reverse('horizon:project:application_policy:index')
        try:
            policyaction_id = self.initial['policyaction_id']
            messages.success(request, _('Policy Action successfully updated.'))
            return http.HttpResponseRedirect(url)
        except Exception as e:
            exceptions.handle(request, _("Unable to update policy action."), redirect=url)

class UpdatePolicyClassifierForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=80, label=_("Name"), required=False)
    description = forms.CharField(label=_("Description"), required=False)
    protocol = forms.ChoiceField(label=_("Protocol"),choices=PROTOCOLS)
    port_range = forms.CharField(max_length=80, label=_("Port/Range(min:max)"), required=False)
    direction = forms.ChoiceField(label=_("Direction"), choices=DIRECTIONS)

    def __init__(self, request, *args, **kwargs):
        super(UpdatePolicyClassifierForm, self).__init__(request, *args, **kwargs)
        try:
            policyclassifier_id = self.initial['policyclassifier_id']
            classifier = client.policyclassifier_get(request, policyclassifier_id)
            for item in ['name','description','protocol','port_range','direction']:
                self.fields[item].initial = getattr(classifier,item)
        except Exception as e:
           exceptions.handle(request, _("Unable to retrive policy classifier details."))
    
    def handle(self,request,context):
       url = reverse('horizon:project:application_policy:index')
       try:
           policyclassifier_id = self.initial['policyclassifier_id']
           #TODO call the API method
           messages.success(request, _('Policy classifier successfully updated.'))
           return http.HttpResponseRedirect(url)
       except Exception as e:
           exceptions.handle(request, _("Unable to update policy classifier."), redirect=url)

class UpdatePolicyRuleForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=80, label=_("Name"), required=False)
    description = forms.CharField(label=_("Description"), required=False)
    policy_classifier_id = forms.ChoiceField(label=_("Policy Classifier"))
    policy_actions = forms.MultipleChoiceField(label=_("Policy Actions"))

    def __init__(self, request, *args, **kwargs):
        super(UpdatePolicyRuleForm, self).__init__(request, *args, **kwargs)
        try:
            tenant_id = request.user.tenant_id
            policyrule_id = self.initial['policyrule_id']
            rule = client.policyrule_get(request, policyrule_id)
            for item in ['name','description','policy_classifier_id','policy_actions']:
               self.fields[item].initial = getattr(rule,item)
            actions = client.policyaction_list(request, tenant_id=tenant_id)
            action_list = [a.id for a in actions]
            for action in actions:
                action.set_id_as_name_if_empty()
            actions = sorted(actions, key=lambda action: action.name)
            action_list = [(a.id, a.name) for a in actions]
            self.fields['policy_actions'].choices = action_list
        except Exception as e:
           exceptions.handle(request, _("Unable to retrive policy rule details."))
    
    def handle(self,request,context):
       url = reverse('horizon:project:application_policy:index')
       try:
           policyrule_id = self.initial['policyrule_id']
           #TODO call the API method
           messages.success(request, _('Policy rule successfully updated.'))
           return http.HttpResponseRedirect(url)
       except Exception as e:
           exceptions.handle(request, _("Unable to update policy rule."), redirect=url) 
