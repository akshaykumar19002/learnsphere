from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('<int:course_id>', views.course_detail, name='course_detail'),
    path('chat/', views.chat_view, name='chat'),
    path('wishlist/add_remove/<int:course_id>', views.toggle_course_in_wishlist, name='toggle_course_in_wishlist'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('search/<str:searchTxt>', views.dashboard, name='search'),
    path('categories/', views.categories, name='categories'),
    path('categories/<str:topic>/', views.categories, name='view_category'),
    path('my_courses/add/<int:course_id>', views.toggle_course_in_my_courses, name='toggle_course_in_my_courses'),
    path('my_courses/', views.my_courses, name='my_courses'),
    path('filter/<slug:type>', views.filter_courses, name='filter_courses'),
    path('filter/<slug:type>/<str:keyword>', views.filter_courses, name='filter_courses_by_topic'),
]
