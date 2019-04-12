import os.path

import markdown2
from django.conf import settings
from django.http import Http404
from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = 'index.html'


class PrivacyPolicyView(TemplateView):
    template_name = 'privacy.html'


class HelpView(TemplateView):
    template_name = 'help.html'

    def get_context_data(self, **kwargs):
        context = super(HelpView, self).get_context_data(**kwargs)
        page = self.kwargs.get('page', 'index')
        page_path = os.path.join(settings.BASE_DIR, 'help', page) + '.md'
        try:
            with open(page_path) as f:
                context['page'] = markdown2.markdown(f.read())
        except IOError:
            raise Http404()

        return context
