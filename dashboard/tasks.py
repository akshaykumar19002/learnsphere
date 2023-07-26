from .models import *
from user.models import *
from django.contrib.auth.models import User
from recommender.hybrid_recommender import HybridRecommender
import logging
from celery import shared_task

logger = logging.getLogger(__name__)

@shared_task()
def generate_recommendations_for_added_courses():
    logger.info('executing task 1: for generating recommendations for added courses')
    users = User.objects.all()
    for user in users:
        myCourses = MyCourses.objects.filter(user=user).first()
        if myCourses is not None and myCourses.course_ids is not None and len(myCourses.course_ids) > 0:
            courses = HybridRecommender().get_recommendation_for_added_courses(myCourses.course_ids)
            course_ids = []
            for _, row in courses.iterrows():
                course_ids.append(row['id'])
            myCourses.recommended_courses = course_ids
            myCourses.save()
    logger.info('task 1 completed')

@shared_task()
def generate_recommendations_for_user_prefs():
    print('executing task 2: for generating recommendations for user preferences')
    users = User.objects.all()
    for user in users:
        user_prefs = UserPreference.objects.filter(user=user).first()
        if user_prefs is not None:
            course_ids = []
            for topic in user_prefs.topics.all():
                courses = HybridRecommender().get_base_recommendations(topic.name.lower())
                for _, row in courses.iterrows():
                    course_ids.append(row['id'])
            user_prefs.recommended_courses = course_ids
            user_prefs.save()
    print('task 2 completed')
    
@shared_task()
def generate_recommendations_for_wishlist():
    logger.info('executing task 3: for generating recommendations for wishlist courses')
    users = User.objects.all()
    for user in users:
        wishlist = Wishlist.objects.filter(user=user).first()
        if wishlist is not None and wishlist.course_ids is not None and len(wishlist.course_ids) > 0:
            courses = HybridRecommender().get_recommendation_for_added_courses(wishlist.course_ids)
            course_ids = []
            for _, row in courses.iterrows():
                course_ids.append(row['id'])
            wishlist.recommended_courses = course_ids
            wishlist.save()
    logger.info('task 3 completed')