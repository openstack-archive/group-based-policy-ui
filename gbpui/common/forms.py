# Copyright 2012 Nebula, Inc.
#
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

from horizon import forms
from openstack_dashboard import policy

from django.core.urlresolvers import reverse


# Allows forms to hide fields based on policy rules
class PolicyHidingMixin(object):
    hide_rules = {}

    def __init__(self, request, *args, **kwargs):
        super(PolicyHidingMixin, self).__init__(request, *args, **kwargs)
        for field, rules in self.hide_rules.iteritems():
            if not policy.check(rules, request):
                self.fields[field].widget = forms.HiddenInput()


class ReversingModalFormView(forms.ModalFormView):
    def get_context_data(self, **kwargs):
        context = super(ReversingModalFormView, self).get_context_data(
            **kwargs)
        context['submit_url'] = self.get_submit_url(**kwargs)
        return context

    def get_submit_url_params(self, **kwargs):
        return {}

    def get_submit_url(self, **kwargs):
        submit_params = self.get_submit_url_params(**kwargs)
        submit_url = reverse(self.submit_url, kwargs=submit_params)
        return submit_url
