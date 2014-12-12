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


from django.conf.urls import patterns  # noqa
from django.conf.urls import url  # noqa

import views

urlpatterns = patterns('',
                       url(r'^$',
                           views.IndexView.as_view(),
                           name='index'),
                       url(r'^addpolicy_target$',
                           views.AddPTGView.as_view(),
                           name='addpolicy_target'),
                       url(r'^updatepolicy_target/'
                           '(?P<policy_target_id>[^/]+)/$',
                           views.UpdatePTGView.as_view(),
                           name='updatepolicy_target'),
                       url(r'^policy_target/(?P<policy_target_id>[^/]+)/$',
                           views.PTGDetailsView.as_view(),
                           name='policy_targetdetails'),
                       url(r'^addvm/(?P<policy_target_id>[^/]+)/$',
                           views.LaunchVMView.as_view(), name='addvm'),
                       url(r'^add_policy_rule_set/'
                           '(?P<policy_target_id>[^/]+)/$',
                           views.AddProvidedPRSView.as_view(),
                           name='add_provided_prs'),
                       url(r'^remove_policy_rule_set/'
                           '(?P<policy_target_id>[^/]+)/$',
                           views.RemoveProvidedPRSView.as_view(),
                           name='remove_provided_prs'),
                       url(r'^add_consumed/(?P<policy_target_id>[^/]+)/$',
                           views.AddConsumedPRSView.as_view(),
                           name='add_consumed_prs'),
                       url(r'^remove_consumed/(?P<policy_target_id>[^/]+)/$',
                           views.RemoveConsumedPRSView.as_view(),
                           name='remove_consumed_prs'),
                       )
