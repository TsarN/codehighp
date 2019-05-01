import os

import markdown2
from django.conf import settings
from django.core.management import BaseCommand

from main.math import replace_math


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

    s = s.replace('`RATING_TABLE`', rating_table)
    s = markdown2.markdown(s)
    s = replace_math(s)
    return s


class Command(BaseCommand):
    help = 'Rebuild help files'

    def handle(self, *args, **options):
        build_dir = os.path.join(settings.BASE_DIR, 'help', 'build')
        help_dir = os.path.join(settings.BASE_DIR, 'help')
        for root, dirs, files in os.walk(help_dir):
            rel_dir = os.path.relpath(root, help_dir)
            for file in files:
                if not file.endswith(".md"):
                    continue
                html_path = os.path.join(rel_dir, file[:-3] + ".html")
                print("Building", html_path)
                os.makedirs(os.path.dirname(os.path.join(build_dir, html_path)), exist_ok=True)
                with open(os.path.join(root, file)) as f:
                    with open(os.path.join(build_dir, html_path), 'w') as fw:
                        fw.write(preprocess(f.read()))
