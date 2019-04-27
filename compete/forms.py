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

    def __init__(self, flavor=None, *args, **kwargs):
        super(RunSubmitForm, self).__init__(*args, **kwargs)
        self.fields['lang_id'].widget.choices = [(k, v['name']) for k, v in settings.COMPILERS.items() if v['flavor'] == flavor]
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
        if run.problem.contest_id and run.problem.contest == Contest.RUNNING:
            run.legit = Run.DURING_CONTEST
        run.save()
        with open(run.src_path, 'wb') as f:
            for chunk in form_data['src_file'].chunks():
                f.write(chunk)
        do_invoke_run(run)


class ContestRegistrationForm(forms.Form):
    contest_id = forms.IntegerField(widget=forms.HiddenInput())
    agree = forms.BooleanField(required=True, label='I have read and agree to these rules')

    def __init__(self, reg=None, user=None, *args, **kwargs):
        super(ContestRegistrationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Register' if reg == Contest.OPEN_REGISTRATION else 'Send request to register'))
        self.reg = reg
        self.user = user

    def clean_contest_id(self):
        contest_id = self.cleaned_data['contest_id']
        contest = list(Contest.objects.filter(pk=contest_id))
        if not contest:
            raise ValidationError("Contest does not exist")
        contest = contest[0]
        if not contest.can_register(self.user.id):
            raise ValidationError("Cannot register for this contest")
        return contest_id

    def register(self):
        if not self.user.is_authenticated:
            return
        form_data = self.cleaned_data
        if self.reg == Contest.OPEN_REGISTRATION:
            status = ContestRegistration.REGISTERED
        else:
            status = ContestRegistration.PENDING
        reg = ContestRegistration(user_id=self.user.id, contest_id=form_data['contest_id'], official=True, status=status)
        reg.save()


class CancelRegistrationForm(forms.Form):
    registration_id = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, user, *args, **kwargs):
        super(CancelRegistrationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Cancel registration'))
        self.user = user

    def clean_registration_id(self):
        reg_id = self.cleaned_data['registration_id']
        reg = list(ContestRegistration.objects.filter(
            id=reg_id,
            user_id=self.user.id,
            status__in=[ContestRegistration.PENDING, ContestRegistration.REGISTERED]
        ))
        if not reg:
            raise ValidationError("Registration ID is invalid")
        reg = reg[0]
        if not reg.contest.registration_open:
            raise ValidationError("Cannot cancel registration because registration is closed")
        return reg_id

    def cancel_registration(self):
        reg_id = self.cleaned_data['registration_id']
        try:
            ContestRegistration.objects.get(id=reg_id).delete()
        except ContestRegistration.DoesNotExist:
            pass
