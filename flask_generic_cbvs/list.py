from .base import BaseView, TemplateResponseMixin
from .exceptions import ImproperlyConfigured
from .utils import camelcase_to_underscore


class MultipleObjectMixin(object):
    query_object = None
    model = None
    context_object_name = None

    def get_query_object(self):
        if self.query_object is not None:
            query_object = self.query_object
        elif self.model:
            query_object = getattr(self.model, "query")
        else:
            raise ImproperlyConfigured("Either a model or query_object must be defined.")

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
        context_object_name = self.get_context_object_name(query_object)

        context = {
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