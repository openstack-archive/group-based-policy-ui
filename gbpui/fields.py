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

from django.core import urlresolvers
from django.forms import fields
from django.forms import TextInput
from django.forms import widgets
from django.utils.safestring import mark_safe

from django.forms.utils import flatatt
from django.utils.html import format_html

from django.utils.translation import ugettext_lazy as _


class DynamicMultiSelectWidget(widgets.SelectMultiple):

    """A subclass of the ``Select`` widget which renders extra attributes for
    use in callbacks to handle dynamic changes to the available choices.
    """
    _data_add_url_attr = "data-add-item-url"

    def render(self, *args, **kwargs):
        add_item_url = self.get_add_item_url()
        if add_item_url is not None:
            self.attrs[self._data_add_url_attr] = add_item_url
        return super(DynamicMultiSelectWidget, self).render(*args, **kwargs)

    def get_add_item_url(self):
        if callable(self.add_item_link):
            return self.add_item_link()
        try:
            if self.add_item_link_args:
                return urlresolvers.reverse(self.add_item_link,
                                            args=self.add_item_link_args)
            else:
                return urlresolvers.reverse(self.add_item_link)
        except urlresolvers.NoReverseMatch:
            return self.add_item_link


class DynamicMultiChoiceField(fields.MultipleChoiceField):

    """A subclass of ``ChoiceField`` with additional properties that make
    dynamically updating its elements easier.

    Notably, the field declaration takes an extra argument, ``add_item_link``
    which may be a string or callable defining the URL that should be used
    for the "add" link associated with the field.
    """
    widget = DynamicMultiSelectWidget

    def __init__(self,
                 add_item_link=None,
                 add_item_link_args=None,
                 *args,
                 **kwargs):
        super(DynamicMultiChoiceField, self).__init__(*args, **kwargs)
        self.widget.add_item_link = add_item_link
        self.widget.add_item_link_args = add_item_link_args


class CustomMultiChoiceField(DynamicMultiChoiceField):
    def validate(self, *args, **kwargs):
        return True


class DropdownEditWidget(TextInput):
    def __init__(self, data_list, name, *args, **kwargs):
        super(DropdownEditWidget, self).__init__(*args, **kwargs)
        self._name = name
        self._list = data_list
        self.attrs.update({'list': 'list__%s' % self._name})

    def render(self, name, value, attrs=None):
        text_html = super(DropdownEditWidget, self).render(
            name, value, attrs=attrs)
        data_list = '<datalist id="list__%s">' % self._name
        for item in self._list:
            data_list += '<option value="%s">' % item
        data_list += '</datalist>'
        return mark_safe(text_html + data_list)


class TransferTableWidget(widgets.SelectMultiple):
    actions_list = []
    add_item_link = None
    max_items = None
    allocated_filter = False

    allocated_help_text = None
    available_help_text = None
    no_allocated_text = None
    no_available_text = None

    def render(self, name, value, attrs=None, choices=()):
        # css class currently breaks the layout for some reason,
        self.attrs.pop('class', None)

        final_attrs = self.build_attrs(attrs, name=name)

        selected = [] if value is None else value

        options = self.render_options(choices, selected)

        if self.add_item_link is not None:
            final_attrs['add_item_link'] = urlresolvers.reverse(
                self.add_item_link
            )

        if self.max_items is not None:
            final_attrs['max_items'] = self.max_items

        if self.allocated_filter:
            final_attrs['allocated_filter'] = "True"

        final_attrs['allocated_help_text'] = self.allocated_help_text
        final_attrs['available_help_text'] = self.available_help_text
        final_attrs['no_allocated_text'] = self.no_allocated_text
        final_attrs['no_available_text'] = self.no_available_text

        open_tag = format_html('<d-table {}>', flatatt(final_attrs))

        output = [open_tag, options, '</d-table>']

        return mark_safe('\n'.join(output))

    # ...this adds the 'add item button' just by existing and returning a
    # true-y value
    def get_add_item_url(self):
        return None


class TransferTableField(fields.MultipleChoiceField):
    widget = TransferTableWidget

    def __init__(self, add_item_link=None, max_items=-1,
                 allocated_filter=False,
                 allocated_help_text="",
                 available_help_text="",
                 no_allocated_text=_("Select items from bellow"),
                 no_available_text=_("No available items"),
                 *args, **kwargs):
        super(TransferTableField, self).__init__(*args, **kwargs)

        self.widget.add_item_link = add_item_link
        self.widget.max_items = max_items
        self.widget.allocated_filter = allocated_filter

        self.widget.allocated_help_text = allocated_help_text
        self.widget.available_help_text = available_help_text

        self.widget.no_allocated_text = no_allocated_text
        self.widget.no_available_text = no_available_text

    def validate(self, *args, **kwargs):
        return True
