from django.shortcuts import render
from .forms import FeedbackForm
from recommender.hybrid_recommender import HybridRecommender
from dashboard.models import Course

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


def feedback(request, pk):
    course_name = Course().get_by_id(pk)[0]['course_name']
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()

    else:
        form = FeedbackForm()
    return render(request, 'dashboard/feedback/feedback.html', {'form': form, 'id': pk, 'name': course_name})
