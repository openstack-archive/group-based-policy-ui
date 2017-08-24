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
from horizon import tables

from openstack_dashboard import policy

from django.utils.safestring import mark_safe


class LinkColumn(tables.Column):
    def __init__(self, transform, get_policy_target="tenant_id", link_rules=(),
                 **kwargs):
        super(LinkColumn, self).__init__(transform, **kwargs)
        self.link_rules = link_rules
        self.get_policy_target = get_policy_target

    def _get_policy_target(self, datum):
        if callable(self.get_policy_target):
            return self.get_policy_target(datum)
        else:
            return {'project_id': datum[self.get_policy_target]}

    def get_link_url(self, datum):
        policy_target = self._get_policy_target(datum)
        if not policy.check(self.link_rules, self.table.request,
                            policy_target):
            return None
        return super(LinkColumn, self).get_link_url(datum)


class ListColumn(tables.Column):
    def __init__(self, transform, source_list=None, list_rules=(),
                 get_policy_target="tenant_id", empty_value=None, **kwargs):
        if 'link' in kwargs:
            self._link = kwargs.pop("link")
        else:
            self._link = None

        if 'wrap_list' in kwargs:
            kwargs.pop('wrap_list')

        super(ListColumn, self).__init__(transform, wrap_list=True, **kwargs)

        self.source_list = source_list
        self.list_rules = list_rules
        self.get_policy_target = get_policy_target
        self.empty_value = empty_value

    # This is a hacky way to simply reuse the Column link construction
    # mechanism and maintain the Column __init__ API while circumventing the
    # HTML renderer, which would just slap a link around the entire table
    # cell contents; again, the proper way would be to customize the
    # rendering itself
    def get_link_url(self, datum):
        self.link = self._link
        result = super(ListColumn, self).get_link_url(datum)
        self.link = None
        return result

    def _get_policy_target(self, datum):
        if callable(self.get_policy_target):
            return self.get_policy_target(datum)
        else:
            return {'project_id': datum[self.get_policy_target]}

    def get_data(self, datum):
        if (self.source_list is None or not datum[
                self.source_list]) and self.empty_value is not None:
            return self.empty_value
        elif self.source_list is not None:
            result = []
            sub_data = datum[self.source_list] or []
            for sub_datum in sub_data:
                policy_target = self._get_policy_target(sub_datum)
                is_link = self._link is not None and policy.check(
                    self.list_rules, self.table.request, policy_target)

                result.append("<li>")

                if is_link:
                    link = self.get_link_url(sub_datum)
                    result.append("<a href=\"")
                    result.append(link)
                    result.append("\">")

                result.append(super(ListColumn, self).get_data(sub_datum))

                if is_link:
                    result.append("</a>")

                result.append("</li>")
            return mark_safe("".join(result))
        else:
            return super(ListColumn, self).get_data(datum)


class GBPDeleteAction(tables.DeleteAction):
    def _allowed(self, request, datum):
        if datum is None:
            return True
        else:
            return super(GBPDeleteAction, self)._allowed(request, datum)

    def get_policy_target(self, request, datum):
        project_id = None
        if datum:
            project_id = getattr(datum, 'tenant_id', None)
        return {"project_id": project_id}
