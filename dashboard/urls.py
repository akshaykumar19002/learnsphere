from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    # path('feedback/<int:pk>/', views.feedback, name='feedback'),
    path('<int:course_id>', views.course_detail, name='course_detail'),
]
