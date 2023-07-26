from learnsphere.mongo_utils import MongoDB
from django.db import models
from django.contrib.auth.models import User
import uuid


class Feedback(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]  # 1-5 rating

    course_id = models.IntegerField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    date_posted = models.DateTimeField(auto_now_add=True)
    anonymous = models.BooleanField(default=False)
    
    def __str__(self):
        return f'Feedback by {self.user.username} for {self.course_id}'


class Course:
    
    def __init__(self):
        self.mongoClient = MongoDB('courses')
    
    def set(self, id, course_name, description, course_url, rating, review_count, website, topics):
        self.id = id
        self.course_name = course_name
        self.description = description
        self.course_url = course_url
        self.rating = rating
        self.review_count = review_count
        self.website = website
        self.topics = topics
        
    def get(self):
        course = vars(self)
        del course['mongoClient']
        
    def insert(self):
        course = self.get()
        self.mongoClient.create(course)
        
    def search(self, searchTxt):
        courses = []
        for course in self.mongoClient.search(searchTxt)[:10]:
            courses.append(self.get_by_id(course['id'])[0])
        return courses
        
    def get_all(self):
        return self.mongoClient.read()

    def get_topics(self):
        return self.mongoClient.read_column('topics')
    
    def get_by_topic(self, topic):
        return self.mongoClient.read({'topics': {'$regex': topic, '$options': 'i'}})
    
    def get_by_topics(self, topics):
        topics = '|'.join(topics)
        return self.mongoClient.read({'topics': {'$regex': topics, '$options': 'i'}})

    def get_by_id(self, id):
        return self.mongoClient.read({'id': id})
    
    def get_by_ids(self, ids):
        return self.mongoClient.read({'id': {'$in': ids}})
    
    def get_topic_by_ids(self, course_ids):
        return self.mongoClient.read_column('topics', {'id': {'$in': course_ids}})
    
    def update(self):
        self.mongoClient.update({'id': self.id}, self.get())
        
    def delete(self):
        self.mongoClient.delete({'id': self.id})
        
    def update_rating(self, course_id, rating, current_rating):
        course = self.mongoClient.read({'id': course_id})[0]
        if current_rating == 0:
            self.mongoClient.update({'id': course_id}, {'rating': ((course['rating'] * course['review_count']) + rating) / (course['review_count'] + 1), 'review_count': course['review_count'] + 1})
        else:
            self.mongoClient.update({'id': course_id}, {
                'rating': ((course['rating'] * course['review_count']) + (current_rating - rating)) / (course['review_count'] + 1)})

    def __str__(self):
        return self.course_name


class Session(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

class Chat(models.Model):
    session = models.ForeignKey(Session, related_name='chats', on_delete=models.CASCADE)
    user_message = models.TextField()
    bot_message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    course_ids = models.JSONField(default=list)
    recommended_courses = models.JSONField(default=list)
    
    def add_course(self, course_id):
        if course_id not in self.course_ids:
            self.course_ids.append(course_id)
            self.save()

    def remove_course(self, course_id):
        if course_id in self.course_ids:
            self.course_ids.remove(course_id)
            self.save()

    def has_course(self, course_id):
        return course_id in self.course_ids

    def __str__(self):
        return f'Wishlist of {self.user.username}'


class MyCourses(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    course_ids = models.JSONField(default=list)
    recommended_courses = models.JSONField(default=list)
    
    def add_course(self, course_id):
        if course_id not in self.course_ids:
            self.course_ids.append(course_id)
            self.save()

    def remove_course(self, course_id):
        if course_id in self.course_ids:
            self.course_ids.remove(course_id)
            self.save()

    def has_course(self, course_id):
        return course_id in self.course_ids

    def __str__(self):
        return f'My Courses - {self.user.username}'
