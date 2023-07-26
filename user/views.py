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
from dashboard.tasks import generate_recommendations_for_user_prefs
from .models import Topic, Job, UserPreference
from . import scrap

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

            return redirect('email-verification-sent')
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
        return redirect('email-verification-success')
    else:
        return redirect('email-verification-failed')

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

    return redirect('login')


@login_required(login_url='login')
def delete_user(request):
    user = User.objects.get(id=request.user.id)
    
    if request.method == 'POST':
        user.delete()
        messages.error(request, 'Your user has been deleted successfully.')
        return redirect('dashboard:dashboard')
    
    return render(request, 'user/delete-user.html')


@login_required(login_url='login')
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


@login_required(login_url='login')
def user_preferences(request):
    unused_topics = Topic.objects.exclude(userpreference__isnull=False)
    try:
        user_pref = UserPreference.objects.get(user=request.user)
    except UserPreference.DoesNotExist:
        user_pref = None

    if request.method == 'POST':
        form = UserPreferencesForm(request.POST)
        if form.is_valid():
            topics = form.cleaned_data['topics']
            dream_job = form.cleaned_data['dream_job']
            if user_pref is None:
                user_pref = UserPreference(user=request.user)
                user_pref.save()
            user_pref.topics.set(topics)
            user_pref.dream_job = dream_job
            user_pref.save()
            generate_recommendations_for_user_prefs.delay()
            messages.success(request, 'Your preferences have been saved successfully.')
            return redirect('dashboard:dashboard')
        else:
            return render(request, 'user/registration/preferences.html', {'form': form, 'topics': unused_topics})
    else:
        if user_pref is not None:
            form = UserPreferencesForm(initial={'topics': user_pref.topics.all(), 'dream_job': user_pref.dream_job})
        else:
            form = UserPreferencesForm()
    return render(request, 'user/registration/preferences.html', {'form': form, 'topics': unused_topics})


def get_skills(request, job):
    # Call the function from your scrap.py script and pass the job name
    elements_list = scrap.scrape_indeed(job)
    job = Job.objects.filter(name__icontains=job).first()
    for element in elements_list:
        if len(element.split(' ')) < 3:
            if element.find('/') != -1:
                element.replace('/', ' ')
            topic, created = Topic.objects.get_or_create(name=element)
            topic.save()
            job.topics.add(topic)
    return redirect('dashboard:dashboard')
