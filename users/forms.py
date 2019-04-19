from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder, HTML, Field
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm, PasswordChangeForm, \
    PasswordResetForm, SetPasswordForm
from crispy_forms.helper import FormHelper
from django.forms import Textarea, ModelForm

from users.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Sign up'))
        for fieldname in ['username', 'password1', 'password2', 'email']:
            if fieldname in self.fields:
                self.fields[fieldname].help_text = None


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'country', 'bio')
        widgets = {
            'bio': Textarea(attrs={'cols': 40, 'rows': 7})
        }


class CustomUserEditForm(ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'country', 'bio')
        widgets = {
            'bio': Textarea(attrs={'cols': 40, 'rows': 7})
        }

    def __init__(self, *args, **kwargs):
        super(CustomUserEditForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Save'))


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(CustomAuthenticationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Log in'))


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(CustomPasswordChangeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Confirm'))


class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(CustomPasswordResetForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Reset my password'))
        self.helper.form_class = 'form-inline'


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(CustomSetPasswordForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Confirm'))
