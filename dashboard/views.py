from django.shortcuts import render, get_object_or_404, redirect
from .forms import FeedbackForm
from django.contrib.auth.models import User
from recommender.hybrid_recommender import HybridRecommender
from dashboard.models import Course, Feedback
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import *
import openai
import json
import re
import environ

# Initialize environment variables
env = environ.Env()
environ.Env.read_env()

openai.api_key = env('OPENAI_API_KEY')

def dashboard(request):
    courses = HybridRecommender().get_base_recommendations('programming')
    # Assuming df is your DataFrame
    course_list = []
    for index, row in courses.iterrows():
        course = Course()
        course.set(
            id = row['id'],
            course_name=row['course_name'],
            description=row['description'],
            course_url=row['course_url'],
            rating=row['rating'],
            review_count=row['review_count'],
            website=row['website'],
            topics=row['topics']
        )
        course_list.append(course)
    if request.user.is_authenticated:
        user = User.objects.get(pk=request.user.id)
        wishlist = Wishlist.objects.filter(user=user)
        if len(wishlist) > 0:
            wishlist = wishlist[0]
        else:
            wishlist = None
    else:
        wishlist = None
    return render(request, 'dashboard/home.html', {'courses': course_list, 'wishlist': wishlist})


@login_required(login_url='user:login')
def course_detail(request, course_id):
    course = Course().get_by_id(course_id)[0]
    user = User.objects.get(pk=request.user.id)
    feedbacks = Feedback.objects.filter(user=user, course_id=course_id)
    if request.method == 'POST':
        feedback = FeedbackForm(request.POST)
        if not feedback.is_valid():
            user_rating = 0
        user_rating = int(feedback.cleaned_data['rating'])
        if len(feedbacks) == 0:
            feedback = Feedback(user=user, course_id=course_id, rating=user_rating)
            feedback.save()
            Course().update_rating(course_id, user_rating, 0)
        else:
            feedbacks[0].rating = user_rating
            Course().update_rating(course_id, feedbacks[0].rating, user_rating)
            feedbacks[0].save()
        return render(request, 'dashboard/course_detail.html', {'course': course, 'feedback': feedback})
    if len(feedbacks) > 0:
        feedback = FeedbackForm()
        feedback.ratings = feedbacks[0].rating
    else:
        feedback = FeedbackForm()
    return render(request, 'dashboard/course_detail.html', {'course': course, 'feedback': feedback})


def chat_view(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        query = data.get('message').lower().strip()
        print(query)

        # get current session
        session_id = request.session.get('chat_session')
        if session_id is None:
            # if the user is logged in, link the session to their account
            if request.user.is_authenticated:
                chat_session = Session.objects.create(user=request.user)
            else:
                chat_session = Session.objects.create()
            request.session['chat_session'] = str(chat_session.id)
        else:
            chat_session = Session.objects.get(id=session_id)

        # get previous chats
        previous_chats = Chat.objects.filter(session=chat_session).order_by('timestamp')
        previous_messages = [
            {"role": "user" if chat.user_message else "assistant", "content": chat.user_message or chat.bot_message}
            for chat in previous_chats
        ]

        # prepend the system message and append the current user message
        messages = [
            {"role": "system", "content": "You are a helpful assistant who will recommend courses to users."},
            {"role": "system", "content": "Only provide the course name and link to the course. Do not provide any other information."},
            {"role": "system", "content": "If you do not have a course to recommend, just say 'no'."},
            {"role": "system", "content": "Also, only provide responses in bullet points and also no lead-in text."},
        ]
        
        if 'recommend' not in query and 'suggest' not in query:
            messages.append({"role": "user", "content": "Response should be less than 200 characters."})
        else:
            messages.append({"role": "user", "content": "Response should be in the format ```Course Name $ Course Link```"})
            
        # messages += previous_messages
        messages.append({"role": "user", "content": query})

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        bot_response = response['choices'][0]['message']['content']
        print(response)
        
        # create a new chat message
        chat = Chat(session=chat_session, user_message=query, bot_message=bot_response)
        chat.save()
        
        if 'NO' in bot_response.upper():
            return JsonResponse({"message": 'Please provide a valid prompt.'})
        # get course details from bot response
        if 'recommend' in query or 'suggest' in query:
            response = parse_bot_response(bot_response)
            print(response)
            return JsonResponse({"courses": response})
        
        return JsonResponse({"message": bot_response})


def parse_bot_response(content):
    lines = content.split("\n")
    courses = []

    for line in lines:
        if line.strip() != '':
            parts = line.split("$")  # split the line into parts
            if len(parts) == 2:  # if the line has the correct format
                course = {
                    "name": parts[0].split('-')[1].strip(),
                    "link": parts[1].strip()
                }
                courses.append(course)

    return courses  


@login_required(login_url='user:login')
def toggle_course_in_wishlist(request, course_id):
    if request.method == 'POST':
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)

        if wishlist.has_course(course_id):
            wishlist.remove_course(course_id)
            response = {'status': 'removed'}
        else:
            wishlist.add_course(course_id)
            response = {'status': 'added'}

        return JsonResponse(response)

    else:
        return JsonResponse({'status': 'bad request'}, status=400)


@login_required(login_url='user:login')
def wishlist(request):
    wishlist = Wishlist.objects.filter(user=request.user)
    if len(wishlist) > 0:
        wishlist = wishlist[0]
        courses = []
        for course_id in wishlist.course_ids:
            courses.append(Course().get_by_id(course_id)[0])
    else:
        wishlist = None
        courses = []
    return render(request, 'dashboard/wishlist.html', {'wishlist': wishlist, 'courses': courses})
