from flask import render_template
from flask.views import MethodView

from .exceptions import ImproperlyConfigured


class BaseView(MethodView):
    methods = ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS", "TRACE"]


class TemplateResponseMixin(object):
    template_name = None

    def get_template_name(self):
        """
        Returns a template name.
        """
        if not self.template_name:
            raise ImproperlyConfigured("""TemplateResponseMixin requires either a
                    template_name or an implementation of get_template_name""")
        else:
            return self.template_name

    def render_to_response(self, context):
        """
        Renders a template with the provided context
        """
        return render_template(self.get_template_name(), **context)


class TemplateView(TemplateResponseMixin, BaseView):
    def get_context_data(self, **kwargs):
        return {"params": kwargs}

    def get(self, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)