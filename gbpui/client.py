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


class ExternalPTG(neutron.NeutronAPIDictWrapper):

    """Wrapper for neutron external endpoint group."""

    def get_dict(self):
        eepg_dict = self._apidict
        eepg_dict['eepg_id'] = eepg_dict['id']
        return eepg_dict


class ExternalConnectivity(neutron.NeutronAPIDictWrapper):

    """Wrapper for neutron external segment."""

    def get_dict(self):
        ec_dict = self._apidict
        ec_dict['ec_id'] = ec_dict['id']
        return ec_dict


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


class ServiceProfile(neutron.NeutronAPIDictWrapper):

    """Wrapper for neutron service profile."""

    def get_dict(self):
        sc_profile_dict = self._apidict
        return sc_profile_dict


def policy_target_create(request, **kwargs):
    body = {'policy_target_group': kwargs}
    policy_target = gbpclient(request).create_policy_target_group(
        body).get('endpoint_group')
    return PTG(policy_target)


def pt_create(request, **kwargs):
    body = {'policy_target': kwargs}
    pt = gbpclient(request).create_policy_target(body).get('policy_target')
    return PTG(pt)


def pt_list(request, tenant_id, **kwargs):
    policy_targets = gbpclient(request).list_policy_targets(
        tenant_id=tenant_id, shared=False, **kwargs).get('policy_targets')
    policy_targets.extend(gbpclient(request).list_policy_targets(
        shared=True, **kwargs).get('policy_targets'))
    return [PT(pt) for pt in policy_targets]


def pt_delete(request, pt_id):
    gbpclient(request).delete_policy_target(pt_id)


def policy_target_list(request, tenant_id, **kwargs):
    policy_targets = gbpclient(request).list_policy_target_groups(
        tenant_id=tenant_id, shared=False, **kwargs).get(
            'policy_target_groups')
    policy_targets.extend(gbpclient(request).list_policy_target_groups(
        shared=True, **kwargs).get('policy_target_groups'))
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


def ext_policy_target_create(request, **kwargs):
    body = {'external_policy': kwargs}
    policy_target = gbpclient(request).create_external_policy(
        body).get('endpoint_group')
    return ExternalPTG(policy_target)


def ext_policy_target_list(request, tenant_id, **kwargs):
    policy_targets = gbpclient(request).list_external_policies(
        tenant_id=tenant_id, shared=False, **kwargs).get('external_policies')
    policy_targets.extend(gbpclient(request).list_external_policies(
        shared=True, **kwargs).get('external_policies'))
    return [ExternalPTG(policy_target) for policy_target in policy_targets]


def ext_policy_target_get(request, ext_policy_target_id):
    policy_target = gbpclient(request).show_external_policy(
        ext_policy_target_id).get('external_policy')
    return ExternalPTG(policy_target)


def ext_policy_target_delete(request, ext_policy_target_id):
    gbpclient(request).delete_external_policy(ext_policy_target_id)


def ext_policy_target_update(request, ext_policy_target_id, **kwargs):
    body = {'external_policy': kwargs}
    policy_target = gbpclient(request).update_external_policy(
        ext_policy_target_id, body).get('external_policy')
    return ExternalPTG(policy_target)


def policy_rule_set_create(request, **kwargs):
    body = {'policy_rule_set': kwargs}
    policy_rule_set = gbpclient(request).create_policy_rule_set(
        body).get('policy_rule_set')
    return Contract(policy_rule_set)


def policy_rule_set_list(request, tenant_id, **kwargs):
    policy_rule_sets = gbpclient(request).list_policy_rule_sets(
        tenant_id=tenant_id, shared=False, **kwargs).get('policy_rule_sets')
    policy_rule_sets.extend(gbpclient(request).list_policy_rule_sets(
        shared=True, **kwargs).get('policy_rule_sets'))
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


def policyrule_list(request, tenant_id, **kwargs):
    policyrules = gbpclient(request).list_policy_rules(tenant_id=tenant_id,
        shared=False, **kwargs).get('policy_rules')
    policyrules.extend(gbpclient(request).list_policy_rules(shared=True,
        **kwargs).get('policy_rules'))
    return [PolicyRule(pr) for pr in policyrules]


def policyclassifier_create(request, **kwargs):
    body = {'policy_classifier': kwargs}
    classifier = gbpclient(request).create_policy_classifier(
        body).get('policy_classifier')
    return PolicyClassifier(classifier)


def policyclassifier_list(request, tenant_id, **kwargs):
    classifiers = gbpclient(request).list_policy_classifiers(
        tenant_id=tenant_id, shared=False, **kwargs).get('policy_classifiers')
    classifiers.extend(gbpclient(request).list_policy_classifiers(shared=True,
        **kwargs).get('policy_classifiers'))
    return [PolicyClassifier(pc) for pc in classifiers]


def policyaction_create(request, **kwargs):
    body = {'policy_action': kwargs}
    action = gbpclient(request).create_policy_action(
        body).get('policy_action')
    return PolicyAction(action)


def policyaction_list(request, tenant_id, **kwargs):
    actions = gbpclient(request).list_policy_actions(tenant_id=tenant_id,
        shared=False, **kwargs).get('policy_actions')
    actions.extend(gbpclient(request).list_policy_actions(shared=True,
        **kwargs).get('policy_actions'))
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


def l3policy_list(request, tenant_id, **kwargs):
    policies = gbpclient(request).list_l3_policies(tenant_id=tenant_id,
        shared=False, **kwargs).get('l3_policies')
    policies.extend(gbpclient(request).list_l3_policies(shared=True,
        **kwargs).get('l3_policies'))
    return [L2Policy(item) for item in policies]


def l2policy_list(request, tenant_id, **kwargs):
    policies = gbpclient(request).list_l2_policies(tenant_id=tenant_id,
        shared=False, **kwargs).get('l2_policies')
    policies.extend(gbpclient(request).list_l2_policies(shared=True,
        **kwargs).get('l2_policies'))
    return [L2Policy(item) for item in policies]


def networkservicepolicy_list(request, tenant_id, **kwargs):
    policies = gbpclient(request).list_network_service_policies(
        tenant_id=tenant_id, shared=False, **kwargs).get(
            'network_service_policies')
    policies.extend(gbpclient(request).list_network_service_policies(
        shared=True, **kwargs).get('network_service_policies'))
    return [NetworkServicePolicy(item) for item in policies]


def externalconnectivity_list(request, tenant_id, **kwargs):
    external_connectivities = gbpclient(request).list_external_segments(
        tenant_id=tenant_id, shared=False, **kwargs).get('external_segments')
    external_connectivities.extend(gbpclient(request).list_external_segments(
        shared=True, **kwargs).get('external_segments'))
    return [ExternalConnectivity(external_connectivity)
        for external_connectivity in external_connectivities]


def create_externalconnectivity(request, **kwargs):
    body = {'external_segment': kwargs}
    es = gbpclient(request).create_external_segment(
        body).get('external_segment')
    return ExternalConnectivity(es)


def get_externalconnectivity(request, external_connectivity_id):
    es = gbpclient(request).show_external_segment(
        external_connectivity_id).get('external_segment')
    return ExternalConnectivity(es)


def delete_externalconnectivity(request, external_connectivity_id, **kwargs):
    gbpclient(request).delete_external_segment(external_connectivity_id)


def update_externalconnectivity(request, external_connectivity_id, **kwargs):
    body = {'external_segment': kwargs}
    ec = gbpclient(request).update_external_segment(
        external_connectivity_id, body).get('external_segment')
    return ExternalConnectivity(ec)


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


def l3policy_update(request, pc_id, **kwargs):
    body = {'l3_policy': kwargs}
    return gbpclient(request).update_l3_policy(pc_id, body).get('l3_policy')


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


def servicechainnode_list(request, tenant_id, **kwargs):
    sc_nodes = gbpclient(request).list_servicechain_nodes(tenant_id=tenant_id,
        shared=False, **kwargs).get('servicechain_nodes')
    sc_nodes.extend(gbpclient(request).list_servicechain_nodes(shared=True,
        **kwargs).get('servicechain_nodes'))
    return [ServiceChainNode(item) for item in sc_nodes]


def servicechainspec_list(request, tenant_id, **kwargs):
    sc_specs = gbpclient(request).list_servicechain_specs(tenant_id=tenant_id,
        shared=False, **kwargs).get('servicechain_specs')
    sc_specs.extend(gbpclient(request).list_servicechain_specs(shared=True,
        **kwargs).get('servicechain_specs'))
    return [ServiceChainSpec(item) for item in sc_specs]


def servicechaininstance_list(request, tenant_id, **kwargs):
    sc_instances = gbpclient(request).list_servicechain_instances(
        tenant_id=tenant_id, shared=False, **kwargs).get(
        'servicechain_instances')
    sc_instances.extend(gbpclient(request).list_servicechain_instances(
        shared=True, **kwargs).get('servicechain_instances'))
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


def serviceprofile_list(request, **kwargs):
    sc_profile = gbpclient(request).list_service_profiles(True,
        **kwargs).get('service_profiles')
    return [ServiceProfile(item) for item in sc_profile]


def get_service_profile(request, service_profile_id):
    service_profile = gbpclient(request).show_service_profile(
        service_profile_id).get('service_profile')
    return ServiceProfile(service_profile)


def create_service_profile(request, **kwargs):
    body = {'service_profile': kwargs}
    service_profile = gbpclient(request).create_service_profile(
        body).get('service_profile')
    return ServiceProfile(service_profile)


def delete_service_profile(request, service_profile_id):
    gbpclient(request).delete_service_profile(service_profile_id)
