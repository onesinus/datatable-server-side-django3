# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import six


class ColumnOrderError(Exception):
    pass


class Column(object):
    def __init__(self, model_field, allow_choices_lookup=True):
        self.name = model_field.name
        choices = model_field.choices

        if allow_choices_lookup and choices:
            self._choices_lookup = self.parse_choices(choices)
            self._search_choices_lookup =\
                {v: k for k, v in six.iteritems(self._choices_lookup)}
            self._allow_choices_lookup = True
        else:
            self._allow_choices_lookup = False

    @property
    def has_choices_available(self):
        return self._allow_choices_lookup

    def get_field_search_path(self):
        return self.name

    def parse_choices(self, choices):
        choices_dict = {}

        for choice in choices:
            try:
                choices_dict[choice[0]] = choice[1]
            except IndexError:
                choices_dict[choice[0]] = choice[0]
            except UnicodeDecodeError:
                choices_dict[choice[0]] = choice[1].decode('utf-8')

        return choices_dict

    def render_column(self, obj):
        value = getattr(obj, self.name)

        if self._allow_choices_lookup:
            return self._choices_lookup[value]

        return value

    def search_in_choices(self, value):
        if not self._allow_choices_lookup:
            return []
        return [matching_value for key, matching_value in six.iteritems(
            self._search_choices_lookup) if key.startswith(value)]


class ForeignColumn(Column):
    def __init__(self, name, model, path_to_column,
                 allow_choices_lookup=True):

        self._field_search_path = path_to_column
        self._field_path = path_to_column.split('__')
        foreign_field = self.get_foreign_field(model)

        super(ForeignColumn, self).__init__(
            foreign_field, allow_choices_lookup)

    def get_field_search_path(self):
        return self._field_search_path

    def get_foreign_field(self, model):
        path_items = self._field_path
        path_item_count = len(path_items)
        current_model = model

        for idx, cur_field_name in enumerate(path_items):
            fields = {f.name: f for f in current_model._meta.get_fields()}

            if idx < path_item_count-1:
                try:
                    current_field = fields[cur_field_name]
                except KeyError:
                    six.reraise(
                        KeyError,
                        "Field %s doesn't exists (model %s, path: %s)"
                        % (cur_field_name, current_model.__name__,
                           '__'.join(path_items[0:idx])))

                try:
                    current_model = current_field.related_model
                except AttributeError:
                    six.reraise(
                        AttributeError,
                        "Field %s is not a foreign key (model %s, path %s)" %
                        (cur_field_name, current_model.__name__,
                         '__'.join(path_items[0:idx])))
            else:
                foreign_field = fields[cur_field_name]

        return foreign_field

    def get_foreign_value(self, obj):
        current_value = obj

        for current_path_item in self._field_path:
            current_value = getattr(current_value, current_path_item)

            if current_value is None:
                return None

        return current_value

    def render_column(self, obj):
        value = self.get_foreign_value(obj)
        if self._allow_choices_lookup:
            return self._choices_lookup[value]
        return value


class ColumnLink(object):
    def __init__(self, name, model_column, searchable='true', orderable='true',
                 placeholder=False):
        self.name = name
        self._model_column = model_column
        self.searchable = True if searchable == "true" else False
        self.orderable = True if orderable == "true" else False
        self.placeholder = placeholder or (name == '')

    def __repr__(self):
        return '%s (searchable: %s, orderable: %s)' %\
            (self.name or '<placeholder>', self.searchable, self.orderable)

    def get_field_search_path(self):
        return self._model_column.get_field_search_path()

    def get_value(self, object_instance):
        return self._model_column.render_column(object_instance)


class PlaceholderColumnLink(ColumnLink):
    def __init__(self):
        super(PlaceholderColumnLink, self).__init__(
            None, None, False, False, True)

    def get_value(self, object_instance):
        return None


class Order(object):
    def __init__(self, column_index, direction, column_links_list):
        try:
            self.ascending = True if direction == 'asc' else False
            self.column_link = column_links_list[int(column_index)]
            if self.column_link.placeholder:
                raise ColumnOrderError(
                    'Requested to order a placeholder column (index %s)'
                    % column_index)
        except KeyError:
            raise ColumnOrderError(
                'Requested to order a non-existing column (index %s)'
                % column_index)

    def __repr__(self):
        return '%s: %s' % (
            self.column_link.name, 'ASC' if self.ascending else 'DESC')

    def get_order_mode(self):
        if not self.ascending:
            return '-' + self.column_link.get_field_search_path()
        return self.column_link.get_field_search_path()
