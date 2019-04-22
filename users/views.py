import json

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordChangeDoneView, PasswordResetView, \
    PasswordResetDoneView, PasswordResetCompleteView, PasswordResetConfirmView
from django.core.serializers.json import DjangoJSONEncoder
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView

from compete.models import RatingChange
from compete.rating import get_rank
from users.forms import CustomAuthenticationForm, CustomUserCreationForm, CustomPasswordChangeForm, \
    CustomPasswordResetForm, CustomSetPasswordForm, CustomUserEditForm
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

        ratings = list(RatingChange.objects
                       .filter(user_id=self.object.id)
                       .select_related('contest'))

        contest_names = []
        data = []
        color = []

        for rating in ratings:
            contest_names.append(rating.contest.name)
            data.append(dict(x=rating.contest.start_date + rating.contest.duration, y=rating.new_rating))
            color.append(get_rank(rating.new_rating)[2])

        context['contest_names'] = json.dumps(contest_names)
        context['data'] = json.dumps(data, cls=DjangoJSONEncoder)
        context['color'] = json.dumps(color, cls=DjangoJSONEncoder)
        context['ranks'] = json.dumps(settings.RANKS)
        context['min'] = min([1500] + [r.new_rating for r in ratings]) - 100
        context['max'] = max([1500] + [r.new_rating for r in ratings]) + 100

        return context


class UserProfileEditView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserEditForm
    template_name = 'users/profile_edit.html'

    def get_object(self, queryset=None):
        return self.request.user


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
