# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

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


class PT(neutron.NeutronAPIDictWrapper):

    """Wrapper for neutron endpoint group."""

    def get_dict(self):
        pt_dict = self._apidict
        pt_dict['ep_id'] = pt_dict['id']
        return pt_dict


class PTG(neutron.NeutronAPIDictWrapper):

    """Wrapper for neutron endpoint group."""

    def get_dict(self):
        epg_dict = self._apidict
        epg_dict['epg_id'] = epg_dict['id']
        return epg_dict


class Contract(neutron.NeutronAPIDictWrapper):

    """Wrapper for neutron policy_rule_set."""

    def get_dict(self):
        policy_rule_set_dict = self._apidict
        policy_rule_set_dict['policy_rule_set_id'] = policy_rule_set_dict['id']
        return policy_rule_set_dict


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

    """Wrapper for neutron l2policy."""

    def get_dict(self):
        policy_dict = self._apidict
        policy_dict['policy_id'] = policy_dict['id']
        return policy_dict


class NetworkServicePolicy(neutron.NeutronAPIDictWrapper):

    """Wrapper for neutron network service policy."""

    def get_dict(self):
        policy_dict = self._apidict
        return policy_dict


class ServiceChainSpec(neutron.NeutronAPIDictWrapper):

    """Wrapper for neutron service chain spec."""

    def get_dict(self):
        sc_spec_dict = self._apidict
        return sc_spec_dict


class ServiceChainNode(neutron.NeutronAPIDictWrapper):

    """Wrapper for neutron service chain spec."""

    def get_dict(self):
        sc_node_dict = self._apidict
        return sc_node_dict


class ServiceChainInstance(neutron.NeutronAPIDictWrapper):

    """Wrapper for neutron service chain spec."""

    def get_dict(self):
        sc_instance_dict = self._apidict
        return sc_instance_dict


def policy_target_create(request, **kwargs):
    body = {'policy_target_group': kwargs}
    policy_target = gbpclient(request).create_policy_target_group(
        body).get('endpoint_group')
    return PTG(policy_target)


def pt_create(request, **kwargs):
    body = {'policy_target': kwargs}
    pt = gbpclient(request).create_policy_target(body).get('policy_target')
    return PTG(pt)


def pt_list(request, **kwargs):
    policy_targets = gbpclient(request).list_policy_targets(
        **kwargs).get('policy_targets')
    return [PT(pt) for pt in policy_targets]


def policy_target_list(request, **kwargs):
    policy_targets = gbpclient(request).list_policy_target_groups(
        **kwargs).get('policy_target_groups')
    return [PTG(policy_target) for policy_target in policy_targets]


def policy_target_get(request, policy_target_id):
    policy_target = gbpclient(request).show_policy_target_group(
        policy_target_id).get('policy_target_group')
    return PTG(policy_target)


def policy_target_delete(request, policy_target_id):
    gbpclient(request).delete_policy_target_group(policy_target_id)


def policy_target_update(request, policy_target_id, **kwargs):
    body = {'policy_target_group': kwargs}
    policy_target = gbpclient(request).update_policy_target_group(
        policy_target_id, body).get('policy_target_group')
    return PTG(policy_target)


def policy_rule_set_create(request, **kwargs):
    body = {'policy_rule_set': kwargs}
    policy_rule_set = gbpclient(request).create_policy_rule_set(
        body).get('policy_rule_set')
    return Contract(policy_rule_set)


def policy_rule_set_list(request, **kwargs):
    policy_rule_sets = gbpclient(request).list_policy_rule_sets(
        **kwargs).get('policy_rule_sets')
    return [Contract(policy_rule_set) for policy_rule_set in policy_rule_sets]


def policy_rule_set_get(request, policy_rule_set_id):
    policy_rule_set = gbpclient(request).show_policy_rule_set(
        policy_rule_set_id).get('policy_rule_set')
    return Contract(policy_rule_set)


def policy_rule_set_delete(request, policy_rule_set_id):
    gbpclient(request).delete_policy_rule_set(policy_rule_set_id)


def policy_rule_set_update(request, policy_rule_set_id, **kwargs):
    body = {'policy_rule_set': kwargs}
    policy_rule_set = gbpclient(request).update_policy_rule_set(
        policy_rule_set_id, body).get('policy_rule_set')
    return Contract(policy_rule_set)


def policyrule_create(request, **kwargs):
    body = {'policy_rule': kwargs}
    policy_rule = gbpclient(request).create_policy_rule(
        body).get('policy_rule')
    return PolicyRule(policy_rule)


def policyrule_update(request, prid, **kwargs):
    body = {'policy_rule': kwargs}
    policy_rule = gbpclient(request).update_policy_rule(prid,
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


def policyaction_update(request, pc_id, **kwargs):
    body = {'policy_action': kwargs}
    classifier = gbpclient(request).update_policy_action(pc_id,
            body).get('policy_action')
    return PolicyClassifier(classifier)


def policyrule_get(request, pr_id):
    policyrule = gbpclient(request).show_policy_rule(
        pr_id).get('policy_rule')
    return PolicyRule(policyrule)


def policyrule_delete(request, pr_id):
    return gbpclient(request).delete_policy_rule(pr_id)


def policyclassifier_get(request, pc_id):
    policyclassifier = gbpclient(request).show_policy_classifier(
        pc_id).get('policy_classifier')
    return PolicyClassifier(policyclassifier)


def policyclassifier_delete(request, pc_id):
    gbpclient(request).delete_policy_classifier(pc_id)


def policyclassifier_update(request, pc_id, **kwargs):
    body = {'policy_classifier': kwargs}
    classifier = gbpclient(request).update_policy_classifier(pc_id,
            body).get('policy_classifier')
    return PolicyClassifier(classifier)


def l3policy_list(request, **kwargs):
    policies = gbpclient(request).list_l3_policies(**kwargs).get('l3_policies')
    return [L2Policy(item) for item in policies]


def l2policy_list(request, **kwargs):
    policies = gbpclient(request).list_l2_policies(**kwargs).get('l2_policies')
    return [L2Policy(item) for item in policies]


def networkservicepolicy_list(request, **kwargs):
    policies = gbpclient(request).list_network_service_policies(
        **kwargs).get('network_service_policies')
    return [NetworkServicePolicy(item) for item in policies]


def create_networkservice_policy(request, **kwargs):
    body = {'network_service_policy': kwargs}
    spolicy = gbpclient(request).create_network_service_policy(
        body).get('network_service_policy')
    return NetworkServicePolicy(spolicy)


def update_networkservice_policy(request, policy_id, **kwargs):
    body = {'network_service_policy': kwargs}
    spolicy = gbpclient(request).update_network_service_policy(
        policy_id, body).get('network_service_policy')
    return NetworkServicePolicy(spolicy)


def delete_networkservice_policy(request, policy_id, **kwargs):
    gbpclient(request).delete_network_service_policy(policy_id)


def get_networkservice_policy(request, policy_id):
    spolicy = gbpclient(request).show_network_service_policy(
        policy_id).get('network_service_policy')
    return NetworkServicePolicy(spolicy)


def l3policy_get(request, pc_id, **kwargs):
    return gbpclient(request).show_l3_policy(pc_id).get('l3_policy')


def l3policy_create(request, **kwargs):
    body = {'l3_policy': kwargs}
    return gbpclient(request).create_l3_policy(body).get('l3_policy')


def l3policy_delete(request, policy_id):
    gbpclient(request).delete_l3_policy(policy_id)


def l2policy_get(request, pc_id, **kwargs):
    return L2Policy(gbpclient(request).show_l2_policy(pc_id).get('l2_policy'))


def l2policy_create(request, **kwargs):
    body = {'l2_policy': kwargs}
    policy = gbpclient(request).create_l2_policy(body).get('l2_policy')
    return L2Policy(policy)


def l2policy_update(request, pc_id, **kwargs):
    body = {'l2_policy': kwargs}
    policy = gbpclient(request).update_l2_policy(pc_id, body).get('l2_policy')
    return L2Policy(policy)


def l2policy_delete(request, policy_id):
    gbpclient(request).delete_l2_policy(policy_id)


def servicechainnode_list(request, **kwargs):
    sc_nodes = gbpclient(request).list_servicechain_nodes(
        **kwargs).get('servicechain_nodes')
    return [ServiceChainNode(item) for item in sc_nodes]


def servicechainspec_list(request, **kwargs):
    sc_specs = gbpclient(request).list_servicechain_specs(
        **kwargs).get('servicechain_specs')
    return [ServiceChainSpec(item) for item in sc_specs]


def servicechaininstance_list(request, **kwargs):
    sc_instances = gbpclient(request).list_servicechain_instances(
        **kwargs).get('servicechain_instances')
    return [ServiceChainInstance(item) for item in sc_instances]


def get_servicechain_node(request, scnode_id):
    scnode = gbpclient(request).show_servicechain_node(
        scnode_id).get('servicechain_node')
    return ServiceChainNode(scnode)


def create_servicechain_node(request, **kwargs):
    body = {'servicechain_node': kwargs}
    sc_node = gbpclient(request).create_servicechain_node(
        body).get('servicechain_node')
    return ServiceChainNode(sc_node)


def update_servicechain_node(request, scnode_id, **kwargs):
    body = {'servicechain_node': kwargs}
    sc_node = gbpclient(request).update_servicechain_node(
        scnode_id, body).get('servicechain_node')
    return ServiceChainNode(sc_node)


def delete_servicechain_node(request, scnode_id):
    gbpclient(request).delete_servicechain_node(scnode_id)


def get_servicechain_spec(request, scspec_id):
    sc_spec = gbpclient(request).show_servicechain_spec(
        scspec_id).get('servicechain_spec')
    return ServiceChainSpec(sc_spec)


def create_servicechain_spec(request, **kwargs):
    body = {'servicechain_spec': kwargs}
    sc_spec = gbpclient(request).create_servicechain_spec(
        body).get('servicechain_spec')
    return ServiceChainSpec(sc_spec)


def update_servicechain_spec(request, scspec_id, **kwargs):
    body = {'servicechain_spec': kwargs}
    sc_spec = gbpclient(request).update_servicechain_spec(
        scspec_id, body).get('servicechain_spec')
    return ServiceChainSpec(sc_spec)


def delete_servicechain_spec(request, scspec_id):
    gbpclient(request).delete_servicechain_spec(scspec_id)


def get_servicechain_instance(request, scinstance_id):
    sc_instance = gbpclient(request).show_servicechain_instance(
        scinstance_id).get('servicechain_instance')
    return ServiceChainInstance(sc_instance)


def create_servicechain_instance(request, **kwargs):
    body = {'servicechain_instance': kwargs}
    sc_instance = gbpclient(request).create_servicechain_instance(
        body).get('servicechain_instance')
    return ServiceChainInstance(sc_instance)


def update_servicechain_instance(request, scinstance_id, **kwargs):
    body = {'servicechain_instance': kwargs}
    sc_instance = gbpclient(request).update_servicechain_instance(
        scinstance_id, body).get('servicechain_instance')
    return ServiceChainInstance(sc_instance)


def delete_servicechain_instance(request, scinstance_id):
    gbpclient(request).delete_servicechain_instance(scinstance_id)
