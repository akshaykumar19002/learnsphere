from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import User
from django.views import View

from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import *
from .token import user_tokenizer_generate

class Register(View):
    
    def get(self, request):
        form = UserRegisterForm()
        return render(request, 'user/registration/register.html', {'form': form})
    
    def post(self, request):
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            mail_subject = 'user verification email'
            message = render_to_string('user/registration/email-verification.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.id)),
                'token': user_tokenizer_generate.make_token(user),
            })
            user.email_user(mail_subject, message)

            return redirect('user:email-verification-sent')
        return render(request, 'user/registration/register.html', {'form': form})
        

class Login(View):
    
    def get(self, request):
        form = LoginForm()
        return render(request, 'user/login.html', {'form': form})
    
    def post(self, request):
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user:
                login(request, user)
                return redirect('dashboard:dashboard')
        return render(request, 'user/login.html', {'form': form})

def email_verification(request, uidb64, token):

    uid = force_str(urlsafe_base64_decode(uidb64))
    user = User.objects.get(pk=uid)

    if user is not None and user_tokenizer_generate.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('user:email-verification-success')
    else:
        return redirect('user:email-verification-failed')

def email_verification_sent(request):
    return render(request, 'user/registration/email-verification-sent.html')

def email_verification_success(request):
    return render(request, 'user/registration/email-verification-success.html')

def email_verification_failed(request):
    return render(request, 'user/registration/email-verification-failed.html')

def user_logout(request):
    try:
        for key in list(request.session.keys()):
            if key == 'session_key':
                continue
            del request.session[key]
    except KeyError:
        pass

    messages.success(request, 'You have been logged out successfully.')

    return redirect('user:login')


@login_required(login_url='user:login')
def delete_user(request):
    user = User.objects.get(id=request.user.id)
    
    if request.method == 'POST':
        user.delete()
        messages.error(request, 'Your user has been deleted successfully.')
        return redirect('dashboard:dashboard')
    
    return render(request, 'user/delete-user.html')


@login_required(login_url='user:login')
def user_profile(request):
    user = User.objects.get(id=request.user.id)

    username_form = UpdateUsernameForm(request.POST or None, instance=user)
    password_form = ChangePasswordForm(request.POST or None)

    print(request.POST)
    if request.method == 'POST':
        # Update username form
        if 'username_form' in request.POST and username_form.is_valid():
            username_form.save()

        # Change password form
        elif 'password_form' in request.POST and password_form.is_valid():
            current_password = password_form.cleaned_data['currentPassword']
            if user.check_password(current_password):
                new_password = password_form.cleaned_data['newPassword']
                user.set_password(new_password)
                user.save()
                user_logout(request)
            else:
                password_form.add_error('currentPassword', 'Current password is not correct')

    context = {
        'username_form': username_form,
        'password_form': password_form,
    }

    return render(request, 'user/profile.html', context)


@login_required(login_url='user:login')
def user_preferences(request):
    if request.method == 'POST':
        form = UserPreferencesForm(request.POST)
        if form.is_valid():
            user_pref = form.save(commit=False)
            user_pref.user = request.user
            user_pref.save()
            form.save_m2m()
            return redirect('success_page')
    else:
        form = UserPreferencesForm()
    return render(request, 'user/preferences.html', {'form': form})