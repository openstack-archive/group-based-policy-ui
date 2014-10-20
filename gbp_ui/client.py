from __future__ import absolute_import

import logging

from django.conf import settings
from openstack_dashboard.api import base
from openstack_dashboard.api import neutron
from gbpclient.v2_0 import client as gbp_client


LOG = logging.getLogger(__name__)


def gbpclient(request):
    insecure = getattr(settings, 'OPENSTACK_SSL_NO_VERIFY', False)
    cacert = getattr(settings, 'OPENSTACK_SSL_CACERT', None)
    LOG.debug('gbpclient connection created using token "%s" and url "%s"'
              % (request.user.token.id, base.url_for(request, 'network')))
    LOG.debug('user_id=%(user)s, tenant_id=%(tenant)s' %
              {'user': request.user.id, 'tenant': request.user.tenant_id})
    c = gbp_client.Client(token=request.user.token.id,
                          auth_url=base.url_for(request, 'identity'),
                          endpoint_url=base.url_for(request, 'network'),
                          insecure=insecure, ca_cert=cacert)
    return c


class EP(neutron.NeutronAPIDictWrapper):
    """Wrapper for neutron endpoint group."""

    def get_dict(self):
        ep_dict = self._apidict
        ep_dict['ep_id'] = ep_dict['id']
        return ep_dict


class EPG(neutron.NeutronAPIDictWrapper):
    """Wrapper for neutron endpoint group."""

    def get_dict(self):
        epg_dict = self._apidict
        epg_dict['epg_id'] = epg_dict['id']
        return epg_dict


class Contract(neutron.NeutronAPIDictWrapper):
    """Wrapper for neutron contract."""

    def get_dict(self):
        contract_dict = self._apidict
        contract_dict['contract_id'] = contract_dict['id']
        return contract_dict


class PolicyRule(neutron.NeutronAPIDictWrapper):
    """Wrapper for neutron policy rule."""

    def get_dict(self):
        policyrule_dict = self._apidict
        policyrule_dict['policyrule_dict_id'] = policyrule_dict['id']
        return policyrule_dict


class PolicyClassifier(neutron.NeutronAPIDictWrapper):
    """Wrapper for neutron classifier."""

    def get_dict(self):
        classifier_dict = self._apidict
        classifier_dict['classifier_id'] = classifier_dict['id']
        return classifier_dict


class PolicyAction(neutron.NeutronAPIDictWrapper):
    """Wrapper for neutron action."""

    def get_dict(self):
        action_dict = self._apidict
        action_dict['action_id'] = action_dict['id']
        return action_dict

class L2Policy(neutron.NeutronAPIDictWrapper):
	"""Wrapper for neutron action."""

	def get_dict(self):
		policy_dict = self._apidict
		policy_dict['policy_id'] = policy_dict['id']
		return policy_dict
 
 
def epg_create(request, **kwargs):
    body = {'endpoint_group': kwargs}
    epg = gbpclient(request).create_endpoint_group( body).get('endpoint_group')
    return EPG(epg)


def ep_create(request,**kwargs):
	body = {'endpoint': kwargs}
	ep = gbpclient(request).create_endpoint(body).get('endpoint')
	return EPG(ep)


def ep_list(request, **kwargs):
	eps = gbpclient(request).list_endpoints(**kwargs).get('endpoints')
	return [EP(ep) for ep in eps]


def epg_list(request, **kwargs):
	epgs = gbpclient(request).list_endpoint_groups(
	 **kwargs).get('endpoint_groups')
	return [EPG(epg) for epg in epgs]


def epg_get(request, epg_id):
	epg = gbpclient(request).show_endpoint_group(
	 epg_id).get('endpoint_group')
 	return EPG(epg)


def epg_delete(request, epg_id):
	gbpclient(request).delete_endpoint_group(epg_id)


def epg_update(request, epg_id, **kwargs):
 	body = {'endpoint_group': kwargs}
	epg = gbpclient(request).update_endpoint_group(
	 epg_id, body).get('endpoint_group')
	return EPG(epg)


def contract_create(request, **kwargs):
	body = {'contract': kwargs}
	contract = gbpclient(request).create_contract(
	 body).get('contract')
	return Contract(contract)


def contract_list(request, **kwargs):
	contracts = gbpclient(request).list_contracts(
	 **kwargs).get('contracts')
 	return [Contract(contract) for contract in contracts]


def contract_get(request, contract_id):
	contract = gbpclient(request).show_contract(
	 contract_id).get('contract')
	return Contract(contract)


def contract_delete(request, contract_id):
	gbpclient(request).delete_contract(contract_id)


def contract_update(request, contract_id, **kwargs):
	body = {'contract': kwargs}
	contract = gbpclient(request).update_contract(
	 contract_id, body).get('contract')
	return Contract(contract)


def policyrule_create(request, **kwargs):
	body = {'policy_rule': kwargs}
	policy_rule = gbpclient(request).create_policy_rule(
		body).get('policy_rule')
	return PolicyRule(policy_rule)


def policyrule_list(request, **kwargs):
	policyrules = gbpclient(request).list_policy_rules(
	 **kwargs).get('policy_rules')
	return [PolicyRule(pr) for pr in policyrules]


def policyclassifier_create(request, **kwargs):
	body = {'policy_classifier': kwargs}
	classifier = gbpclient(request).create_policy_classifier(
	 body).get('policy_classifier')
	return PolicyClassifier(classifier)


def policyclassifier_list(request, **kwargs):
	classifiers = gbpclient(request).list_policy_classifiers(
	 **kwargs).get('policy_classifiers')
	return [PolicyClassifier(pc) for pc in classifiers]


def policyaction_create(request, **kwargs):
	body = {'policy_action': kwargs}
	action = gbpclient(request).create_policy_action(
	 body).get('policy_action')
	return PolicyAction(action)


def policyaction_list(request, **kwargs):
	actions = gbpclient(request).list_policy_actions(
	 **kwargs).get('policy_actions')
	return [PolicyAction(pa) for pa in actions]


def policyaction_delete(request, pa_id):
	gbpclient(request).delete_policy_action(pa_id)


def policyaction_get(request, pa_id):
	policyaction = gbpclient(request).show_policy_action(
	 pa_id).get('policy_action')
	return PolicyAction(policyaction)


def policyrule_get(request, pr_id):
	policyrule = gbpclient(request).show_policy_rule(
	 pr_id).get('policy_rule')
	return PolicyRule(policyrule)


def policyrule_delete(request, pr_id):
	gbpclient(request).delete_policy_rule(pr_id)


def policyrule_update(request, pr_id, **kwargs):
	gbpclient(request).update_policy_rule(pr_id,kwargs)


def policyclassifier_get(request, pc_id):
	policyclassifier = gbpclient(request).show_policy_classifier(
	 pc_id).get('policy_classifier')
 	return PolicyClassifier(policyclassifier)


def policyclassifier_delete(request, pc_id):
	gbpclient(request).delete_policy_classifier(pc_id)


def policyclassifier_update(request, pc_id, **kwargs):
	return {}

def l3policy_list(request,**kwargs):
	policies = gbpclient(request).list_l3_policies(**kwargs).get('l3_policies')
	return [L2Policy(item) for item in policies]

def l2policy_list(request,**kwargs):
	policies =  gbpclient(request).list_l2_policies(**kwargs).get('l2_policies')
	return [L2Policy(item) for item in policies]

def l3policy_get(request,pc_id,**kwargs):
	return gbpclient(request).show_l3_policy(pc_id).get('l3_policy')

def l2policy_get(request,pc_id,**kwargs):
	return gbpclient(request).show_l2_policy(pc_id).get('l2_policy')

def l2policy_create(request,**kwargs):
 	body = {'l2_policy': kwargs}
	return gbpclient(request).create_l2_policy(body).get('l2_policy')

def l3policy_create(request,**kwargs):
	body = {'l3_policy':kwargs}
	return gbpclient(request).create_l3_policy(body).get('l3_policy')  
