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

from django.conf.urls import url  # noqa

import views

import restApi

urlpatterns = [
    url(r'^$',
        views.IndexView.as_view(),
        name='index'),
    url(r'^addpolicy_target$',
        views.AddPTGView.as_view(),
        name='addpolicy_target'),
    url(r'^addexternal_policy_target$',
        views.AddExternalPTGView.as_view(),
        name='addexternal_policy_target'),
    url(r'^updatepolicy_target/(?P<policy_target_id>[^/]+)/$',
        views.UpdatePTGView.as_view(),
        name='updatepolicy_target'),
    url(r'^update_ext_policy_target/(?P<ext_policy_target_id>[^/]+)/$',
        views.UpdateExternalPTGView.as_view(),
        name='update_ext_policy_target'),
    url(r'^policy_target/(?P<policy_target_id>[^/]+)/$',
        views.PTGDetailsView.as_view(),
        name='policy_targetdetails'),
    url(r'^ext_policy_target/(?P<ext_policy_target_id>[^/]+)/$',
        views.ExternalPTGDetailsView.as_view(),
        name='ext_policy_targetdetails'),
    url(r'^ext_add_policy_rule_set/(?P<ext_policy_target_id>[^/]+)/$',
        views.ExtAddProvidedPRSView.as_view(),
        name='ext_add_provided_prs'),
    url(r'^add_policy_rule_set/(?P<policy_target_id>[^/]+)/$',
        views.AddProvidedPRSView.as_view(),
        name='add_provided_prs'),
    url(r'^ext_remove_policy_rule_set/(?P<ext_policy_target_id>[^/]+)/$',
        views.ExtRemoveProvidedPRSView.as_view(),
        name='ext_remove_provided_prs'),
    url(r'^remove_policy_rule_set/(?P<policy_target_id>[^/]+)/$',
        views.RemoveProvidedPRSView.as_view(),
        name='remove_provided_prs'),
    url(r'^add_consumed/(?P<policy_target_id>[^/]+)/$',
        views.AddConsumedPRSView.as_view(),
        name='add_consumed_prs'),
    url(r'^ext_add_consumed/(?P<ext_policy_target_id>[^/]+)/$',
        views.ExtAddConsumedPRSView.as_view(),
        name='ext_add_consumed_prs'),
    url(r'^remove_consumed/(?P<policy_target_id>[^/]+)/$',
        views.RemoveConsumedPRSView.as_view(),
        name='remove_consumed_prs'),
    url(r'^ext_remove_consumed/(?P<ext_policy_target_id>[^/]+)/$',
        views.ExtRemoveConsumedPRSView.as_view(),
        name='ext_remove_consumed_prs'),
    url(r'/check_ip_availability',
        views.check_ip_availability,
        name='check_ip_availability'),
    # Rest APIs for use with AJAX/ANGULARJS calls
    url(r'policy_target_groups/$',
        restApi.PolicyTargets.as_view(),
        name='policy_target_groups'),
    url(r'launch_instance/$',
        restApi.Members.as_view(),
        name='launch_instance'),
]
