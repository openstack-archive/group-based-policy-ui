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

from django.core.urlresolvers import reverse


def get_classifier_link(datum):
    return reverse(
        "horizon:project:application_policy:policyclassifierdetails",
        kwargs={"policyclassifier_id": datum.policy_classifier.id}
    )


def get_classifier_name(datum):
    return datum.policy_classifier.name


def get_classifier_target(datum):
    return {"project_id": datum.policy_classifier.tenant_id}


def get_action_value_name(action):
    if action.action_type == 'redirect':
        return action.spec.name + ":" + action.spec.id
    return '-'


def get_action_value_link(action):
    if action.action_type == 'redirect':
        url = "horizon:project:network_services:sc_spec_details"
        url = reverse(url, kwargs={'scspec_id': action.spec.id})
        return url
    return None
