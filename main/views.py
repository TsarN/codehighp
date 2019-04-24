import os.path

import markdown2
from django.conf import settings
from django.http import Http404
from django.views.generic import TemplateView


class PrivacyPolicyView(TemplateView):
    template_name = 'privacy.html'


class DonateView(TemplateView):
    template_name = 'donate.html'


class DonateThanksView(TemplateView):
    template_name = 'donate_thanks.html'


class HelpView(TemplateView):
    template_name = 'help.html'

    @staticmethod
    def preprocess(s):
        rating_table = '''
<table>
    <thead>
        <tr>
            <th>Rank</th>
            <th>Rating</th>
        </tr>
    </thead>
    <tbody>
'''
        last_rating = None
        for name, rating, color in settings.RANKS:
            if not last_rating:
                hrating = '{} and less'.format(rating)
            elif rating == 99999:
                hrating = '{} and more'.format(last_rating)
            else:
                hrating = '{}&ndash;{}'.format(last_rating, rating - 1)
            rating_table += '''
        <tr>
            <td><b style="color: {color}">{name}</b></td>
            <td><b style="color: {color}">{rating}</b></td>
        </tr>
'''.format(color=color, name=name, rating=hrating)
            last_rating = rating

        rating_table += '''
    </tbody>
</table>
'''

        return s.replace('`RATING_TABLE`', rating_table)

    def get_context_data(self, **kwargs):
        context = super(HelpView, self).get_context_data(**kwargs)
        page = self.kwargs.get('page', 'index')
        page_path = os.path.join(settings.BASE_DIR, 'help', page) + '.md'
        try:
            with open(page_path) as f:
                context['page'] = markdown2.markdown(HelpView.preprocess(f.read()))
        except IOError:
            raise Http404()

        return context
