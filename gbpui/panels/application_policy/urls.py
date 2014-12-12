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


from django.conf.urls import patterns  # noqa
from django.conf.urls import url  # noqa

import views

urlpatterns = patterns(
    '',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^addpolicy_rule_set$', views.AddPolicyRuleSetView.as_view(),
        name='addpolicy_rule_set'),
    url(r'^addpolicyrule$', views.AddPolicyRuleView.as_view(),
        name='addpolicyrule'),
    url(r'^addpolicyclassifier$', views.AddPolicyClassifierView.as_view(),
        name='addpolicyclassifier'),
    url(r'^addpolicyaction$', views.AddPolicyActionView.as_view(),
        name='addpolicyaction'),
    url(r'^updatepolicy_rule_set/(?P<policy_rule_set_id>[^/]+)/$',
        views.UpdatePolicyRuleSetView.as_view(), name='updatepolicy_rule_set'),
    url(r'^updatepolicyrule/(?P<policyrule_id>[^/]+)/$',
        views.UpdatePolicyRuleView.as_view(), name='updatepolicyrule'),
    url(r'^updatepolicyclassifier/(?P<policyclassifier_id>[^/]+)/$',
        views.UpdatePolicyClassifierView.as_view(),
        name='updatepolicyclassifier'),
    url(r'^updatepolicyaction/(?P<policyaction_id>[^/]+)/$',
        views.UpdatePolicyActionView.as_view(),
        name='updatepolicyaction'),
    url(r'^policyrule/(?P<policyrule_id>[^/]+)/$',
        views.PolicyRuleDetailsView.as_view(), name='policyruledetails'),
    url(r'^policyclassifier/(?P<policyclassifier_id>[^/]+)/$',
        views.PolicyClassifierDetailsView.as_view(),
        name='policyclassifierdetails'),
    url(r'^policyaction/(?P<policyaction_id>[^/]+)/$',
        views.PolicyActionDetailsView.as_view(),
        name='policyactiondetails'),
    url(r'^policy_rule_set/(?P<policy_rule_set_id>[^/]+)/$',
        views.PolicyRuleSetDetailsView.as_view(),
        name='policy_rule_set_details'),
)
