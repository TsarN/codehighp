import re

from django.conf import settings

import requests


def replace_math(x):
    for group in set(re.findall(r'\$\$(.*?)\$\$', x, re.S)):
        data = requests.post(settings.MATHOID_URL, data=dict(q=group, type='tex')).json()
        if not data['success']:
            x = x.replace('$${}$$'.format(group), 'TeX error: {}'.format(data.get('log')))
        else:
            x = x.replace('$${}$$'.format(group), data.get('svg'))

    for group in set(re.findall(r'\$(.*?)\$', x, re.S)):
        data = requests.post(settings.MATHOID_URL, data=dict(q=group, type='inline-tex')).json()
        if not data['success']:
            x = x.replace('${}$'.format(group), 'TeX error: {}'.format(data.get('log')))
        else:
            x = x.replace('${}$'.format(group), data.get('svg'))

    return x
