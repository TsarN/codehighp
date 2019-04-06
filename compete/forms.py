from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError

from compete.models import Problem, Run, ContestRegistration, Contest
from compete.tasks import do_invoke_run


class RunSubmitForm(forms.Form):
    prob_id = forms.IntegerField(widget=forms.HiddenInput())
    lang_id = forms.CharField(widget=forms.Select(choices=settings.COMPILERS_ENUM), label='Language')
    src_file = forms.FileField(label='Source file')

    def __init__(self, *args, **kwargs):
        super(RunSubmitForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))

    def clean_prob_id(self):
        prob_id = self.cleaned_data['prob_id']
        if not Problem.objects.filter(pk=prob_id).exists():
            raise ValidationError("Problem does not exist")
        return prob_id

    def clean(self):
        form_data = self.cleaned_data
        prob_id = form_data['prob_id']
        lang_id = form_data['lang_id']

        prob = Problem.objects.get(pk=prob_id)
        if prob.config['flavor'] != settings.COMPILERS[lang_id]['flavor']:
            self._errors['lang_id'] = ["Unsupported language"]

        return form_data

    def submit_run(self, user):
        if not user.is_authenticated:
            return
        form_data = self.cleaned_data
        prob_id = form_data['prob_id']
        lang_id = form_data['lang_id']
        run = Run(user=user, problem_id=prob_id, lang=lang_id)
        run.save()
        with open(run.src_path, 'wb') as f:
            for chunk in form_data['src_file'].chunks():
                f.write(chunk)
        do_invoke_run(run)


class ContestRegistrationForm(forms.Form):
    contest_id = forms.IntegerField(widget=forms.HiddenInput())
    agree = forms.BooleanField(required=True, label='I have read and agree to these rules')

    def __init__(self, *args, **kwargs):
        super(ContestRegistrationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Register'))

    def clean_contest_id(self):
        contest_id = self.cleaned_data['contest_id']
        if not Contest.objects.filter(pk=contest_id).exists():
            raise ValidationError("Contest does not exist")
        return contest_id

    def register(self, user):
        if not user.is_authenticated:
            return
        form_data = self.cleaned_data
        reg = ContestRegistration(user_id=user.id, contest_id=form_data['contest_id'], official=True)
        reg.save()
