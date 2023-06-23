from django.shortcuts import render
# from .forms import FeedbackForm
from django.contrib.auth.models import User
from recommender.hybrid_recommender import HybridRecommender
from dashboard.models import Course, Feedback
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse as JSONResponse

# Create your views here.
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


# def feedback(request, pk):
#     course_name = Course().get_by_id(pk)[0]['course_name']
#     if request.method == 'POST':
#         form = FeedbackForm(request.POST)
#         if form.is_valid():
#             form.save()

#     else:
#         form = FeedbackForm()
#     return render(request, 'dashboard/feedback/feedback.html', {'form': form, 'id': pk, 'name': course_name})

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
