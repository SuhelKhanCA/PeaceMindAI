from django.urls import path
from main_app import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('feedback/', views.submit_feedback, name='submit_feedback'),
]