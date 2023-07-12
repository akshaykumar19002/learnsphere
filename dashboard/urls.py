from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    # path('feedback/<int:pk>/', views.feedback, name='feedback'),
    path('<int:course_id>', views.course_detail, name='course_detail'),
    path('chat/', views.chat_view, name='chat'),
    path('wishlist/add_remove/<int:course_id>', views.toggle_course_in_wishlist, name='toggle_course_in_wishlist'),
    path('wishlist/', views.wishlist, name='wishlist')
]
