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

from gbpui import client

LOG = logging.getLogger(__name__)


def list_column_filter(items):
    if len(items) == 0:
        return ""
    return items


def update_pruleset_attributes(request, prset):
    rules = prset.policy_rules
    url = "horizon:project:application_policy:policyruledetails"
    value = ["<ul>"]
    li = lambda x: "<li><a href='" + \
        reverse(url, kwargs={'policyrule_id': x.id}) + \
        "'>" + x.name + "</a></li>"
    for rule in rules:
        r = client.policyrule_get(request, rule)
        value.append(li(r))
    value.append("</ul>")
    value = "".join(value)
    setattr(prset, 'policy_rules', mark_safe(value))
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
    url = "horizon:project:application_policy:policy_rule_set_details"
    provided = pt.provided_policy_rule_sets
    consumed = pt.consumed_policy_rule_sets
    provided = [client.policy_rule_set_get(request, item) for item in provided]
    consumed = [client.policy_rule_set_get(request, item) for item in consumed]
    p = ["<ul>"]
    li = lambda x: "<li><a href='" + \
        reverse(url, kwargs={'policy_rule_set_id': x.id}) + \
        "'>" + x.name + "</a></li>"
    for item in provided:
        p.append(li(item))
    p.append("</ul>")
    p = "".join(p)
    c = ["<ul>"]
    for item in consumed:
        c.append(li(item))
    c.append("</ul>")
    c = "".join(c)
    consumed = [item.name for item in consumed]
    setattr(pt, 'provided_policy_rule_sets', mark_safe(p))
    setattr(pt, 'consumed_policy_rule_sets', mark_safe(c))
    l2url = "horizon:project:network_policy:l2policy_details"
    if hasattr(pt, 'l2_policy_id') and pt.l2_policy_id is not None:
        policy = client.l2policy_get(request, pt.l2_policy_id)
        u = reverse(l2url, kwargs={'l2policy_id': policy.id})
        atag = mark_safe(
            "<a href='" + u + "'>" + policy.name + "</a>")
        setattr(pt, 'l2_policy_id', atag)
    if hasattr(pt, 'external_segments'):
        exturl = "horizon:project:network_policy:external_connectivity_details"
        value = ["<ul>"]
        li = lambda x: "<li><a href='" + \
            reverse(exturl, kwargs={'external_connectivity_id': x.id}) + \
            "'>" + x.name + "</a></li>"
        for external_segment in pt.external_segments:
            ext_policy = client.get_externalconnectivity(request,
                external_segment)
            value.append(li(ext_policy))
        value.append("</ul>")
        value = "".join(value)
        setattr(pt, 'external_segments', mark_safe(value))
    return pt


def update_policyrule_attributes(request, prule):
    url = "horizon:project:application_policy:policyclassifierdetails"
    classifier_id = prule.policy_classifier_id
    classifier = client.policyclassifier_get(request, classifier_id)
    u = reverse(url, kwargs={'policyclassifier_id': classifier.id})
    tag = mark_safe("<a href='" + u + "'>" + classifier.name + "</a>")
    setattr(prule, 'policy_classifier_id', tag)
    actions = prule.policy_actions
    action_url = "horizon:project:application_policy:policyactiondetails"
    ul = ["<ul>"]
    for a in actions:
        action = client.policyaction_get(request, a)
        u = reverse(action_url, kwargs={'policyaction_id': a})
        if action.action_type == 'redirect':
            spec = client.get_servicechain_spec(request, action.action_value)
            spec_details = "%s:%s" % (spec.name, str(spec.id))
            li = "<li><a href='%s'>%s</a></li>" % (u, spec_details)
        else:
            li = "<li><a href='%s'>%s</a></li>" % (u, action.name)
        ul.append(li)
    ul.append("</ul>")
    ultag = "".join(ul)
    setattr(prule, 'policy_actions', mark_safe(ultag))
    return prule


def update_policyaction_attributes(request, paction):
    if paction.action_type == 'redirect':
        spec = client.get_servicechain_spec(request,
                paction.action_value)
        url = "horizon:project:network_services:sc_spec_details"
        url = reverse(url, kwargs={'scspec_id': spec.id})
        tag_content = (url, spec.name + ":" + spec.id)
        tag = "<a href='%s'>%s</a>" % tag_content
        setattr(paction, 'action_value', mark_safe(tag))
    return paction


def update_sc_spec_attributes(request, scspec):
    img_path = "/static/dashboard/img/"
    provider = "default"
    nodes = scspec.nodes
    nodes = [client.get_servicechain_node(request, item) for item in nodes]
    t = "<table class='table table-condensed' \
        style='margin-bottom:0px'><tr><td>"
    val = [t + "<span class='glyphicon glyphicon-remove-circle'></span></td>"]
    ds_path = "/opt/stack/horizon/static/dashboard/img/"
    if os.path.exists(ds_path):
        local_img_path = ds_path
    else:
        local_img_path = "/usr/share/openstack-dashboard/openstack_dashboard/" \
            + "static/dashboard/img/"
    if os.path.exists(local_img_path):
        providers = os.listdir(local_img_path)
        for p in providers:
            if p in scspec.description:
                provider = p
                break

    img_src = img_path + provider + "/"
    scn_url = "horizon:project:network_services:sc_node_details"
    for n in nodes:
        url = reverse(scn_url, kwargs={'scnode_id': n.id})
        service_profile_id = n.service_profile_id
        try:
            service_profile = client.get_service_profile(request,
                service_profile_id)
            service_type = service_profile.service_type
        except Exception:
            pass
        val.append(
            "<td><span class='glyphicon glyphicon-arrow-right'></span></td>")
        scnode = "<td><a href='" + url + "' style='font-size: 9px;' >" \
            + "<img src='" + img_src + service_type + ".png'>" \
            + "<br>" + n.name + " (" + service_type + ")</a></td>"
        val.append(scnode)
    val.append("</tr></table>")
    setattr(scspec, 'nodes', mark_safe("".join(val)))
    return scspec


def update_sc_node_attributes(request, scnode):
    t = "<p style='margin-bottom:0px'>"
    val = [t]
    sp_url = "horizon:project:network_services:service_profile_details"
    url = reverse(sp_url, kwargs={'sp_id': scnode.service_profile_id})
    try:
        service_profile = client.get_service_profile(request,
            scnode.service_profile_id)
        sp = "<a href='" + url + "'>" + service_profile.name + ' : ' + \
            service_profile.service_type + '</a></p>'
        val.append(sp)
    except Exception:
        return scnode
    setattr(scnode, 'service_profile', mark_safe("".join(val)))
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
            if classifier.protocol in ['tcp', 'udp'] and classifier.port_range \
                    in port_protocol_map:
                classifier.protocol = port_protocol_map[classifier.port_range]
    else:
        if classifiers.protocol in ['tcp', 'udp'] and classifiers.port_range \
                in port_protocol_map:
            classifiers.protocol = port_protocol_map[classifiers.port_range]
    return classifiers


def update_l3_policy_attributes(request, l3_policy):
    url = "horizon:project:network_policy:external_connectivity_details"
    if bool(l3_policy.external_segments):
        value = ["<ul>"]
        li = \
            lambda x: "<li><a href='" + \
            reverse(url, kwargs={'external_connectivity_id': x.id}) + \
             "'>" + x.name + "</a>" + " : " + \
            l3_policy.external_segments[x.id][0] + "</li>"
        for ec in l3_policy.external_segments.keys():
            external_connectivity = client.get_externalconnectivity(request,
                                                                    ec)
            value.append(li(external_connectivity))
        value.append("</ul>")
        tag = mark_safe("".join(value))
    else:
        tag = '-'
    setattr(l3_policy, 'external_segments', tag)
    return l3_policy


def update_nat_pool_attributes(request, nat_pool):
    url = "horizon:project:network_policy:external_connectivity_details"
    id = nat_pool.external_segment_id
    value = ["<ul>"]
    li = \
        lambda x: "<li><a href='" + \
        reverse(url, kwargs={'external_connectivity_id': x.id}) + \
        "'>" + x.name + "</a>" + "</li>"
    external_connectivity = client.get_externalconnectivity(request,
                                                                id)
    value.append(li(external_connectivity))
    value.append("</ul>")
    tag = mark_safe("".join(value))
    setattr(nat_pool, 'external_segment_id', tag)
    return nat_pool
