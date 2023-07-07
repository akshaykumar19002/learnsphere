from django.shortcuts import render
# from .forms import FeedbackForm
from django.contrib.auth.models import User
from recommender.hybrid_recommender import HybridRecommender
from dashboard.models import Course, Feedback
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse as JSONResponse

from .models import *
import openai
import json
import re

openai.api_key = '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'


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

    return render(request, 'dashboard/home.html', {'courses': course_list})


@login_required(login_url='user:login')
def course_detail(request, course_id):
    course = Course().get_by_id(course_id)[0]
    user = User.objects.get(pk=request.user.id)
    feedback = Feedback.objects.filter(user=user, course_id=course_id)
    if len(feedback) > 0:
        feedback = feedback[0]
    else:
        feedback = None
    if request.method == 'POST':
        user_rating = int(request.POST.get('rating'))
        if feedback is None:
            feedback = Feedback(user=user, course_id=course_id, rating=user_rating)
            feedback.save()
            Course().update_rating(course_id, user_rating, 0)
        else:
            Course().update_rating(course_id, user_rating, feedback.rating)
            feedback.rating = user_rating
            feedback.save()
        return render(request, 'dashboard/course_detail.html', {'course': course, 'feedback': feedback})
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
            return JSONResponse({"message": 'Please provide a valid prompt.'})
        # get course details from bot response
        if 'recommend' in query or 'suggest' in query:
            response = parse_bot_response(bot_response)
            print(response)
            return JSONResponse({"courses": response})
        
        return JSONResponse({"message": bot_response})


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
