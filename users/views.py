import json

from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordChangeDoneView, PasswordResetView, \
    PasswordResetDoneView, PasswordResetCompleteView, PasswordResetConfirmView
from django.core.serializers.json import DjangoJSONEncoder
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView

from compete.models import RatingChange
from users.forms import CustomAuthenticationForm, CustomUserCreationForm, CustomPasswordChangeForm, \
    CustomPasswordResetForm, CustomSetPasswordForm
from users.models import CustomUser


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'users/login.html'


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'users/signup.html'


class UserProfileView(DetailView):
    model = CustomUser
    template_name = 'users/profile.html'
    slug_field = 'username'

    def get_context_data(self, **kwargs):
        context = super(UserProfileView, self).get_context_data(**kwargs)

        ratings = RatingChange.objects\
            .filter(user_id=self.object.id)\
            .select_related('contest')

        contest_names = ['(Joined CodeHighp)']
        data = [dict(x=self.object.date_joined, y=1500)]

        for rating in ratings:
            contest_names.append(rating.contest.name)
            data.append(dict(x=rating.contest.start_date, y=rating.new_rating))

        context['contest_names'] = json.dumps(contest_names)
        context['data'] = json.dumps(data, cls=DjangoJSONEncoder)

        return context


class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'users/password_change.html'


class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'users/password_change_done.html'


class CustomPasswordResetView(PasswordResetView):
    template_name = 'users/password_reset_form.html'
    subject_template_name = 'users/password_reset_subject.txt'
    email_template_name = 'users/password_reset_email.html'
    form_class = CustomPasswordResetForm


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = 'users/password_reset_confirm.html'
