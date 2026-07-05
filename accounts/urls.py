from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<int:user_id>/', views.applicant_profile, name='applicant_profile'),
    path('profile/education/add/', views.add_education, name='add_education'),
    path('profile/experience/add/', views.add_experience, name='add_experience'),
    path('profile/certification/add/', views.add_certification, name='add_certification'),
]
