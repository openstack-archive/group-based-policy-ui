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

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^create_service_profile$',
        views.CreateServiceProfileView.as_view(),
        name='create_service_profile'),
    url(r'^serviceprofile/(?P<sp_id>[^/]+)/$',
        views.ServiceProfileDetailsView.as_view(),
        name='service_profile_details'),
    url(r'^create_sc_node$',
        views.CreateServiceChainNodeView.as_view(),
        name='create_sc_node'),
    url(r'^update_sc_node/(?P<scnode_id>[^/]+)/$',
        views.UpdateServiceChainNodeView.as_view(),
        name='update_sc_node'),
    url(r'^sc_node/(?P<scnode_id>[^/]+)/$',
        views.ServiceChainNodeDetailsView.as_view(),
        name='sc_node_details'),
    url(r'^create_sc_spec$',
        views.CreateServiceChainSpecView.as_view(),
        name='create_sc_spec'),
    url(r'^update_sc_spec/(?P<scspec_id>[^/]+)/$',
        views.UpdateServiceChainSpecView.as_view(),
        name='update_sc_spec'),
    url(r'^sc_spec/(?P<scspec_id>[^/]+)/$',
        views.ServiceChainSpecDetailsView.as_view(),
        name='sc_spec_details'),
    url(r'^sc_instance/(?P<scinstance_id>[^/]+)/$',
        views.ServiceChainInstanceDetailsView.as_view(),
        name='sc_instance_details'),
]
