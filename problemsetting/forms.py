import re

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.db.transaction import atomic

from compete.models import ProblemPermission, Problem
from users.models import CustomUser


class AddProblemDeveloperForm(forms.Form):
    username = forms.CharField(label='Username')
    access = forms.CharField(widget=forms.Select(choices=(
        ('RD', 'Read'),
        ('WR', 'Write')
    )), label='Access')

    def __init__(self, prob_id, *args, **kwargs):
        super(AddProblemDeveloperForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('add_developer', 'Submit'))
        self.prob_id = prob_id
        self.user_id = None

    def clean_username(self):
        username = self.cleaned_data['username']
        user = list(CustomUser.objects.filter(username=username, is_problemsetter=True))
        if not user:
            raise forms.ValidationError('User `{}` does not exist or is not a problemsetter'.format(username))
        self.user_id = user[0].id
        return username

    def clean_access(self):
        access = self.cleaned_data['access']
        if access not in ['RD', 'WR']:
            raise forms.ValidationError('Invalid access mode')
        return self.cleaned_data['access']

    def clean(self):
        if ProblemPermission.objects.filter(problem_id=self.prob_id, user_id=self.user_id).exists():
            raise forms.ValidationError('This user is already a developer')
        return self.cleaned_data

    def add_developer(self):
        access = self.cleaned_data['access']
        ProblemPermission.objects.create(user_id=self.user_id, problem_id=self.prob_id, access=access)


class ProblemNameForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super(ProblemNameForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('rename', 'Submit'))


class ProblemCreateForm(forms.Form):
    internal_name = forms.CharField(label='Problem ID')

    def __init__(self, *args, **kwargs):
        super(ProblemCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('creaate', 'Submit'))

    def clean_internal_name(self):
        id = self.cleaned_data['internal_name']
        if Problem.objects.filter(internal_name=id).exists():
            raise forms.ValidationError('This ID is taken')
        if not re.match(r'^[a-z0-9][a-z0-9\-]*$', id):
            raise forms.ValidationError('Lowercase English letters, numbers and dashes only. Can\'t start with a dash.')
        return id

    def save(self, user_id):
        id = self.cleaned_data['internal_name']
        with atomic():
            prob = Problem(internal_name=id, name='Unnamed problem {}'.format(id))
            prob.error = "Problem is not uploaded"
            prob.save()
            ProblemPermission.objects.create(problem_id=prob.id, user_id=user_id, access=ProblemPermission.OWNER)
        prob.update_git_permissions()
