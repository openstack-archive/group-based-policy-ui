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

from django.core.urlresolvers import reverse


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


class HelpTextModalMixin(object):
    def get_context_data(self, **kwargs):
        context = super(HelpTextModalMixin, self).get_context_data(**kwargs)
        context["help_text"] = self.help_text
        return context
