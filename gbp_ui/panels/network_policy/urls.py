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
#
# @author: Ronak Shah


from django.conf.urls import patterns  # noqa
from django.conf.urls import url  # noqa

import views

urlpatterns = patterns( '',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^addl3policy$', views.AddL3policyView.as_view(), name='addl3policy'),
    url(r'^l3policy_details/(?P<l3policy_id>[^/]+)/$', views.L3PolicyDetailsView.as_view(), name='l3policy_details'),
    url(r'^l3policy_update/(?P<l3policy_id>[^/]+)/$', views.L3PolicyUpdateView.as_view(), name='update_l3policy'),
    url(r'^addl2policy$', views.AddL2policyView.as_view(), name='addl2policy'),
    url(r'^l2policy_details/(?P<l2policy_id>[^/]+)/$', views.L2PolicyDetailsView.as_view(), name='l2policy_details'),
    url(r'^l2policy_update/(?P<l2policy_id>[^/]+)/$', views.L2PolicyUpdateView.as_view(), name='update_l2policy'), 
) 
