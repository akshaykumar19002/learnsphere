from learnsphere.mongo_utils import MongoDB
from django.db import models
from django.contrib.auth.models import User


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course_id = models.IntegerField(null=True, blank=True)
    rating = models.IntegerField()
    
    class Meta:
        unique_together = ('user', 'course_id')
    

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
        
    def get_all(self):
        return self.mongoClient.read()

    def get_topics(self):
        return self.mongoClient.read_column('topics')
    
    def get_by_topic(self, topic):
        return self.mongoClient.read({'topics': {'$regex': topic, '$options': 'i'}})

    def get_by_id(self, id):
        return self.mongoClient.read({'id': id})
    
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
