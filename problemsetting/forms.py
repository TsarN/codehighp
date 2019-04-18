from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from compete.models import ProblemPermission
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
