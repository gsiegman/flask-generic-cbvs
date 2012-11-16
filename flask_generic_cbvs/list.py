from flask import abort, request

from .base import BaseView, TemplateResponseMixin
from .exceptions import ImproperlyConfigured
from .utils import camelcase_to_underscore


class MultipleObjectMixin(object):
    query_object = None
    model = None
    context_object_name = None
    paginate_by = None
    sort_by = None

    def get_query_object(self):
        if self.query_object is not None:
            query_object = self.query_object
        elif self.model:
            query_object = getattr(self.model, "query")
        else:
            raise ImproperlyConfigured("Either a model or query_object must be defined.")

        return query_object

    def get_paginate_by(self):
        return self.paginate_by

    def paginate_query_object(self, query_object, page_size):
        page = request.args.get("page") or 1
        try:
            page_number = int(page)
        except ValueError:
            abort(404)

        paginator = query_object.paginate(page_number, page_size)

        return (paginator, paginator.items, paginator.has_prev or paginator.has_next)

    def get_sort_by(self):
        return self.sort_by

    def sort_query_object(self, query_object):
        sort_by = request.args.get("sort_by", self.get_sort_by())

        if sort_by:
            if sort_by[0] == "-":
                query_object = query_object.order_by(
                    getattr(query_object._entities[0].entity_zero.class_, sort_by[1:]).desc())
            else:
                query_object = query_object.order_by(
                    getattr(query_object._entities[0].entity_zero.class_, sort_by))

        return query_object

    def get_context_object_name(self, object_list):
        if self.context_object_name:
            return self.context_object_name
        elif hasattr(object_list, "column_descriptions"):
            return str("%s_list" % camelcase_to_underscore(
                object_list.column_descriptions[0]["name"]))
        else:
            return None

    def get_context_data(self, **kwargs):
        query_object = kwargs.pop("object_list")
        page_size = self.get_paginate_by()
        context_object_name = self.get_context_object_name(query_object)

        if self.sort_by:
            query_object = self.sort_query_object(query_object)

        if page_size:
            paginator, query_object, is_paginated = self.paginate_query_object(query_object, page_size)
            context = {
                "paginator": paginator,
                "is_paginated": is_paginated,
                "object_list": query_object
            }
        else:
            context = {
                "paginator": None,
                "is_paginated": False,
                "object_list": query_object
            }

        context.update(kwargs)
        if context_object_name is not None:
            context[context_object_name] = query_object
        return context


class BaseListView(MultipleObjectMixin, BaseView):
    def get(self, **kwargs):
        self.object_list = self.get_query_object()
        context = self.get_context_data(object_list=self.object_list)
        return self.render_to_response(context)


class ListView(TemplateResponseMixin, BaseListView):
    """
    """