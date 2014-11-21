import logging
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from gbp_ui import client

LOG = logging.getLogger(__name__)


def list_column_filter(items):
	if len(items) == 0:
		return ""
	return items

def update_pruleset_attributes(request,prset):
	rules = prset.policy_rules
	url = "horizon:project:application_policy:policyruledetails"
	value = ["<ul>"]
	li = lambda x: "<li><a href='"+reverse(url,kwargs={'policyrule_id':x.id})+"'>"+x.name+"</a></li>"
	for rule in rules:
		r = client.policyrule_get(request,rule)
		value.append(li(r))
	value.append("</ul>")
	value = "".join(value)
	setattr(prset,'policy_rules',mark_safe(value))
	return prset

def update_policy_target_attributes(request,pt):
 	url = "horizon:project:application_policy:policy_rule_set_details"
	provided = pt.provided_policy_rule_sets
	consumed = pt.consumed_policy_rule_sets
	provided = [client.policy_rule_set_get(request,item) for item in provided]
	consumed = [client.policy_rule_set_get(request,item) for item in consumed]
	p = ["<ul>"]
	li = lambda x: "<li><a href='"+reverse(url,kwargs={'policy_rule_set_id':x.id})+"'>"+x.name+"</a></li>"
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
	setattr(pt,'provided_policy_rule_sets',mark_safe(p))
	setattr(pt,'consumed_policy_rule_sets',mark_safe(c))
	l2url = "horizon:project:network_policy:l2policy_details"
	if pt.l2_policy_id is not None:
		policy = client.l2policy_get(request,pt.l2_policy_id)
		atag  = mark_safe("<a href='"+reverse(l2url,kwargs={'l2policy_id':policy.id})+"'>"+policy.name+"</a>")
		setattr(pt,'l2_policy_id',atag)
	return pt

def update_policyrule_attributes(request,prule):
	url = "horizon:project:application_policy:policyclassifierdetails"
	classifier_id = prule.policy_classifier_id
	classifier = client. policyclassifier_get(request,classifier_id)
	tag = mark_safe("<a href='"+reverse(url,kwargs={'policyclassifier_id':classifier.id})+"'>"+classifier.name+"</a>")
	setattr(prule,'policy_classifier_id',tag)
	return prule

def update_sc_spec_attributes(request,scspec):
	nodes = scspec.nodes
	nodes = [client.get_servicechain_node(request,item) for item in nodes]
	value = ["<table class='table table-condensed'><tr><td><span class='glyphicon glyphicon-remove-circle'></span></td>"]
	for n in nodes:
		value.append("<td><span class='glyphicon glyphicon-arrow-right'></span></td>")
		value.append("<td>"+n.name+"("+n.service_type+")</td>")
	value.append("</tr></table>")
	setattr(scspec,'nodes',mark_safe("".join(value)))
	return scspec                                                

def update_sc_instance_attributes(request,scinstance):
	ptg_url = "horizon:project:policytargets:policy_targetdetails"
	clsurl = "horizon:project:application_policy:policyclassifierdetails"
	scspec_url = "horizon:project:network_services:sc_spec_details"
	consumer_ptg = scinstance.consumer_ptg
	provider_ptg = scinstance.provider_ptg
	scspec = scinstance.servicechain_spec
	classifier = scinstance.classifier
	if consumer_ptg is not None:
		ptg = client.policy_target_get(request,consumer_ptg)
		atag = "<a href='%s'>%s</a>" % (reverse(ptg_url,kwargs={'policy_target_id':ptg.id}),ptg.name)
		setattr(scinstance,'consumer_ptg',mark_safe(atag))
	if provider_ptg is not None:
		ptg = client.policy_target_get(request,consumer_ptg)
		atag = "<a href='%s'>%s</a>" % (reverse(ptg_url,kwargs={'policy_target_id':ptg.id}),ptg.name)
		setattr(scinstance,'provider_ptg',mark_safe(atag))
	if classifier is not None:
		cls = client.policyclassifier_get(request,classifier)
		atag = "<a href='%s'>%s</a>" % (reverse(clsurl,kwargs={'policyclassifier_id':cls.id}),cls.name)
		setattr(scinstance,'classifier',mark_safe(atag))
	if scspec is not None:
		sc = client.get_servicechain_spec(request,scspec)
		atag = "<a href='%s'>%s</a>" % (reverse(scspec_url,kwargs={'scspec_id':sc.id}),sc.name)
		setattr(scinstance,'servicechain_spec',mark_safe(atag))
	return scinstance
