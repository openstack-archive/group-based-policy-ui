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

import logging
import os

from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from common import policy

from gbpui import client
from gbpui import GBP_POLICY_FILE

LOG = logging.getLogger(__name__)


def list_column_filter(items):
    if len(items) == 0:
        return ""
    return items


def update_pruleset_attributes(request, prset):
    setattr(prset, 'policy_rules',
        [client.policyrule_get(request, rule) for rule in prset.policy_rules]
    )
    return prset


def update_service_policy_attributes(policy):
    np = policy.network_service_params
    params = ""
    if len(np) > 0:
        tags = []
        for item in np:
            dl = ["<dl class='dl-horizontal'>"]
            dl.extend(["<dt>%s<dt><dd>%s</dd>" %
                       (k, v) for k, v in item.items()])
            dl.append("</dl>")
            tags.append("".join(dl))
        params = mark_safe("".join(tags))
    setattr(policy, 'network_service_params', params)
    return policy


def update_policy_target_attributes(request, pt):
    # gets policy rule set objects from ids and sets them into the datum object
    # for displaying in tables
    setattr(pt, 'provided_policy_rule_sets',
        [client.policy_rule_set_get(request, item) for item in
         pt.provided_policy_rule_sets])
    setattr(pt, 'consumed_policy_rule_sets',
        [client.policy_rule_set_get(request, item) for item in
         pt.consumed_policy_rule_sets])

    # sets l2 policy information for the table
    if hasattr(pt, 'l2_policy_id') and pt.l2_policy_id is not None:
        # We could/should probably pass the entire policy object
        policy = client.l2policy_get(request, pt.l2_policy_id)
        setattr(pt, 'l2_policy_name', policy.name)

    # external segments for linking
    if hasattr(pt, 'external_segments'):
        setattr(pt, 'external_segments',
            [client.get_externalconnectivity(request, external_segment)
             for external_segment in pt.external_segments])
    return pt


def update_policyrule_attributes(request, prule):
    classifier_id = prule.policy_classifier_id
    classifier = client.policyclassifier_get(request, classifier_id)
    setattr(prule, 'policy_classifier', classifier)

    policy_actions = []
    for a in prule.policy_actions:
        action = client.policyaction_get(request, a)

        if action.action_type == 'redirect':
            spec = client.get_servicechain_spec(request, action.action_value)
            spec_details = "%s:%s" % (spec.name, str(spec.id))
            action.name = spec_details

        policy_actions.append(action)
    setattr(prule, 'policy_actions', policy_actions)

    return prule


def update_policyaction_attributes(request, paction):
    if paction.action_type == 'redirect':
        spec = client.get_servicechain_spec(request, paction.action_value)
        setattr(paction, 'spec', spec)

    return paction


def update_sc_spec_attributes(request, scspec):
    loaded_nodes = []
    for node_id in scspec.nodes:
        node = client.get_servicechain_node(request, node_id)
        node.service_profile = client.get_service_profile(
            request, node.service_profile_id
        )
        node.can_access = policy.check((
            (GBP_POLICY_FILE, "get_servicechain_node"),), request,
            {"project_id": node.tenant_id}
        )
        loaded_nodes.append(node)

    setattr(scspec, 'loaded_nodes', loaded_nodes)
    return scspec


def update_sc_node_attributes(request, scnode):
    try:
        service_profile = client.get_service_profile(request,
                                                     scnode.service_profile_id)
        setattr(scnode, 'service_profile', service_profile)
    except Exception:
        return scnode
    return scnode


def update_scn_instance_attributes(request, scspec):
    static_url = getattr(settings, 'STATIC_URL', "/static/")
    img_path = static_url + "dashboard/img/"
    provider = "default"
    nodes = scspec.nodes
    nodes = [client.get_servicechain_node(request, item) for item in nodes]
    sc = ["<div>"]
    ds_path = "/opt/stack/horizon/static/dashboard/img/"
    if os.path.exists(ds_path):
        local_img_path = ds_path
    else:
        local_img_path = "/usr/share/openstack-dashboard/" \
                         + "openstack_dashboard/static/dashboard/img/"
    if os.path.exists(local_img_path):
        providers = os.listdir(local_img_path)
        for p in providers:
            if p in scspec.description:
                provider = p
                break

    img_src = img_path + provider + "/"
    for n in nodes:
        service_profile_id = n.service_profile_id
        try:
            service_profile = client.get_service_profile(request,
                                                         service_profile_id)
            service_type = service_profile.service_type
        except Exception:
            pass
        sc.append(
            "<span class='glyphicon glyphicon-arrow-right' "
            "style='margin: auto 10px'></span>")
        scnode = "<img src='" + img_src + service_type + ".png'>"
        sc.append(scnode)
    sc.append("</div>")
    setattr(scspec, 'chain', mark_safe("".join(sc)))
    return scspec


def update_sc_instance_attributes(request, scinstance):
    ptg_url = "horizon:project:policytargets:policy_targetdetails"
    clsurl = "horizon:project:application_policy:policyclassifierdetails"
    scspec_url = "horizon:project:network_services:sc_spec_details"
    consumer_ptg = scinstance.consumer_ptg_id
    provider_ptg = scinstance.provider_ptg_id
    scspec = scinstance.servicechain_specs
    classifier = scinstance.classifier_id
    if consumer_ptg is not None and consumer_ptg != "N/A":
        ptg = client.policy_target_get(request, consumer_ptg)
        u = reverse(ptg_url, kwargs={'policy_target_id': ptg.id})
        atag = "<a href='%s'>%s</a>" % (u, ptg.name)
        setattr(scinstance, 'consumer_ptg', mark_safe(atag))
    if provider_ptg is not None:
        ptg = client.policy_target_get(request, provider_ptg)
        u = reverse(ptg_url, kwargs={'policy_target_id': ptg.id})
        atag = "<a href='%s'>%s</a>" % (u, ptg.name)
        setattr(scinstance, 'provider_ptg', mark_safe(atag))
    if classifier is not None:
        cls = client.policyclassifier_get(request, classifier)
        u = reverse(clsurl, kwargs={'policyclassifier_id': cls.id})
        atag = "<a href='%s'>%s</a>" % (u, cls.name)
        setattr(scinstance, 'classifier', mark_safe(atag))
    if scspec is not None:
        scs = client.get_servicechain_spec(request, scspec[0])
        url = reverse(scspec_url, kwargs={'scspec_id': scs.id})
        atag = "<a href='%s'>%s</a>" % (url, scs.name)
        setattr(scinstance, 'servicechain_spec', mark_safe(atag))
        scni = update_scn_instance_attributes(request, scs)
        setattr(scinstance, 'servicechain', scni.chain)
    return scinstance


def update_classifier_attributes(classifiers):
    port_protocol_map = {'21': 'ftp', '25': 'smtp', '53': 'dns',
                         '80': 'http', '443': 'https'}
    if type(classifiers) == list:
        for classifier in classifiers:
            classifier.set_id_as_name_if_empty()
            if classifier.protocol in ['tcp', 'udp'] and classifier.port_range\
                    in port_protocol_map:
                classifier.protocol = port_protocol_map[classifier.port_range]
    else:
        if classifiers.protocol in ['tcp', 'udp'] and classifiers.port_range \
                in port_protocol_map:
            classifiers.protocol = port_protocol_map[classifiers.port_range]
    return classifiers


def update_l3_policy_attributes(request, l3_policy):
    _segments = []
    if "external_segments" in l3_policy:
        for seg_id, addresses in l3_policy.external_segments.iteritems():
            segment = client.get_externalconnectivity(request, seg_id)
            segment.addresses = addresses

            # this is a bit of a hack, where the policy is checked here for use
            # with complex transform in the table matching column; the
            # transform function has no access to a request
            segment.can_access = policy.check(
                ((GBP_POLICY_FILE, "get_external_segment"),), request,
                {'project_id': segment.tenant_id}
            )
            _segments.append(segment)
    setattr(l3_policy, 'external_segments', _segments)
    return l3_policy


def update_nat_pool_attributes(request, nat_pool):
    external_connectivity = client.get_externalconnectivity(
        request, nat_pool.external_segment_id
    )
    external_segments = [external_connectivity]
    setattr(nat_pool, 'external_segments', external_segments)
    return nat_pool
