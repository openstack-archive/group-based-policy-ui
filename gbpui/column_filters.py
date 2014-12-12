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
    if pt.l2_policy_id is not None:
        policy = client.l2policy_get(request, pt.l2_policy_id)
        u = reverse(l2url, kwargs={'l2policy_id': policy.id})
        atag = mark_safe(
            "<a href='" + u + "'>" + policy.name + "</a>")
        setattr(pt, 'l2_policy_id', atag)
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
    nodes = scspec.nodes
    nodes = [client.get_servicechain_node(request, item) for item in nodes]
    t = "<table class='table table-condensed'><tr><td>"
    val = [t + "<span class='glyphicon glyphicon-remove-circle'></span></td>"]
    for n in nodes:
        val.append(
            "<td><span class='glyphicon glyphicon-arrow-right'></span></td>")
        val.append("<td>" + n.name + "(" + n.service_type + ")</td>")
    val.append("</tr></table>")
    setattr(scspec, 'nodes', mark_safe("".join(val)))
    return scspec


def update_sc_instance_attributes(request, scinstance):
    ptg_url = "horizon:project:policytargets:policy_targetdetails"
    clsurl = "horizon:project:application_policy:policyclassifierdetails"
    scspec_url = "horizon:project:network_services:sc_spec_details"
    consumer_ptg = scinstance.consumer_ptg
    provider_ptg = scinstance.provider_ptg
    scspec = scinstance.servicechain_spec
    classifier = scinstance.classifier
    if consumer_ptg is not None:
        ptg = client.policy_target_get(request, consumer_ptg)
        u = reverse(ptg_url, kwargs={'policy_target_id': ptg.id})
        atag = "<a href='%s'>%s</a>" % (u, ptg.name)
        setattr(scinstance, 'consumer_ptg', mark_safe(atag))
    if provider_ptg is not None:
        ptg = client.policy_target_get(request, consumer_ptg)
        u = reverse(ptg_url, kwargs={'policy_target_id': ptg.id})
        atag = "<a href='%s'>%s</a>" % (u, ptg.name)
        setattr(scinstance, 'provider_ptg', mark_safe(atag))
    if classifier is not None:
        cls = client.policyclassifier_get(request, classifier)
        u = reverse(clsurl, kwargs={'policyclassifier_id': cls.id})
        atag = "<a href='%s'>%s</a>" % (u, cls.name)
        setattr(scinstance, 'classifier', mark_safe(atag))
    if scspec is not None:
        sc = client.get_servicechain_spec(request, scspec)
        u = reverse(scspec_url, kwargs={'scspec_id': sc.id})
        atag = "<a href='%s'>%s</a>" % (u, sc.name)
        setattr(scinstance, 'servicechain_spec', mark_safe(atag))
    return scinstance
