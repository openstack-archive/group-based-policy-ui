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
                   url(r'^$', views.IndexView.as_view(), name='index'),
                   url(r'^addl3policy$',
                       views.AddL3policyView.as_view(),
                          name='addl3policy'),
                   url(r'^addservicepolicy$',
                          views.CreateServicePolicyView.as_view(),
                       name='create_servicepolicy'),
                   url(r'^addnetworkserviceparam$',
                          views.AddNetworkServiceParamView.as_view(),
                       name='add_network_service_param'),
                   url(r'^addexternalrouteparam$',
                          views.AddExternalRouteParamView.as_view(),
                       name='add_external_route_param'),
                   url(r'^createexternalconnectivity$',
                          views.CreateExternalConnectivityView.as_view(),
                       name='create_external_connectivity'),
                   url(r'^update_servicepolicy/(?P<service_policy_id>[^/]+)/$',
                       views.UpdateServicePolicyView.as_view(),
                       name='update_service_policy'),
                   url(r'^update_externalconnectivity/'
                       '(?P<external_connectivity_id>[^/]+)/$',
                       views.UpdateExternalConnectivityView.as_view(),
                       name='update_externalconnectivity'),
                   url(r'^servicepolicy/(?P<service_policy_id>[^/]+)/$',
                       views.ServicePolicyDetailsView.as_view(),
                       name='service_policy_details'),
                   url(r'^externalconnectivity/'
                       '(?P<external_connectivity_id>[^/]+)/$',
                       views.ExternalConnectivityDetailsView.as_view(),
                       name='external_connectivity_details'),
                   url(r'^addl2policy$',
                       views.AddL2policyView.as_view(),
                                               name='addl2policy'),
                   url(r'^l3policy_details/(?P<l3policy_id>[^/]+)/$',
                       views.L3PolicyDetailsView.as_view(),
                                               name='l3policy_details'),
                   url(r'^l3policy_update/(?P<l3policy_id>[^/]+)/$',
                       views.L3PolicyUpdateView.as_view(),
                                               name='update_l3policy'),
                   url(r'^l2policy_details/(?P<l2policy_id>[^/]+)/$',
                       views.L2PolicyDetailsView.as_view(),
                                               name='l2policy_details'),
                   url(r'^l2policy_update/(?P<l2policy_id>[^/]+)/$',
                       views.L2PolicyUpdateView.as_view(),
                                               name='update_l2policy'),
                       )
