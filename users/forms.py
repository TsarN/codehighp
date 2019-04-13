from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder, HTML, Field
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from crispy_forms.helper import FormHelper
from django.forms import Textarea

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


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(CustomAuthenticationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Log in'))
