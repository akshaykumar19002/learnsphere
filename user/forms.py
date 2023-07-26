from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from django.forms.widgets import PasswordInput, TextInput
from .models import UserPreference, Topic, Job

from recommender.utils import *

class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs) -> None:
        super(UserRegisterForm, self).__init__(*args, **kwargs)

        self.fields['email'].required = True

    # email validation
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already exists')
        if len(email) > 350:
            raise forms.ValidationError('Email is too long')
        return email


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput(attrs={'class': 'validate', 'placeholder': 'Username'}))
    password = forms.CharField(widget=PasswordInput(attrs={'placeholder': 'Password'}))
    

class UpdateUsernameForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']
        widgets = {
            'username': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username',
                'aria-describedBy': 'usernameHelpBlock'
            }),
        }
        labels = {
            'username': 'Username',
        }
        help_texts = {
            'usernameHelpBlock': 'Enter your new username.',
        }


class ChangePasswordForm(forms.Form):
    currentPassword = forms.CharField(label='Current Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Current Password',
                'aria-describedBy': 'currentPasswordHelpBlock'}),
        help_text='Enter your current password to confirm your identity.')
    newPassword = forms.CharField(label='New Password', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'New Password',
                'aria-describedBy': 'newPasswordHelpBlock'}),
        help_text='Enter your new password.')
    confirmPassword = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Confirm Password',
                'aria-describedBy': 'confirmPasswordHelpBlock'}),
        help_text='Enter your new password again to confirm it.')

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password != confirm_password:
            raise forms.ValidationError("New password and confirm password must match.")


class UserPreferencesForm(forms.Form):
    dream_job = forms.ModelChoiceField(
        queryset=Job.objects.all(),
    )
    topics = forms.ModelMultipleChoiceField(
        queryset=Topic.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )
    
    def __init__(self, *args, **kwargs):
        dream_job = kwargs.pop('dream_job', None)
        super().__init__(*args, **kwargs)
        if dream_job is not None:
            self.fields['topics'].queryset = Topic.objects.filter(jobtopic__job=dream_job)

    def clean_topics(self):
        print(self.cleaned_data )
        topics = self.cleaned_data.get('topics')
        print(topics)
        if topics is None or len(topics) < 1:
            raise forms.ValidationError("You must select at least 1 topics.")
        if topics is not None and len(topics) > 3:
            raise forms.ValidationError("You must select at most 3 topics.")
        return topics

