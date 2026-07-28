from django.urls import path
from django.contrib.auth import views as auth_views
from django_ratelimit.decorators import ratelimit
from . import views

# Apply ratelimit to login view to prevent brute force attacks
login_view = ratelimit(key='ip', rate='10/m', block=True)(auth_views.LoginView.as_view(template_name='accounts/login.html'))

urlpatterns = [
    path('register/', views.register, name='register'),
    path('signup/', views.register, name='account_signup'),
    path('check-availability/', views.check_availability, name='check_availability'),
    path('set-social-role/', views.set_social_role, name='set_social_role'),
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/edit-additional/', views.edit_additional_info, name='edit_additional_info'),
    path('profile/education/add/', views.add_education, name='add_education'),
    path('employer/<int:employer_id>/follow/', views.toggle_follow_employer, name='toggle_follow_employer'),
    path('add-experience/', views.add_experience, name='add_experience'),
    path('add-certification/', views.add_certification, name='add_certification'),
    path('add-reference/', views.add_reference, name='add_reference'),
    path('applicant/<int:user_id>/', views.applicant_profile, name='applicant_profile'),
    path('resume-builder/', views.resume_builder, name='resume_builder'),
    path('export-resume-pdf/', views.export_resume_pdf, name='export_resume_pdf'),
    path('resume-templates/', views.template_gallery, name='template_gallery'),
    path('resume-templates/buy/<int:template_id>/', views.buy_template, name='buy_template'),
    path('referrals/', views.referrals_view, name='referrals'),
    path('ref/<int:ref_id>/', views.referral_signup, name='referral_signup'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/unread-count/', views.get_unread_count, name='get_unread_count'),
    path('employer-verification/', views.employer_verification, name='employer_verification'),
    path('wallet/top-up/', views.wallet_topup, name='wallet_topup'),
    path('manage-recruiters/', views.manage_recruiters, name='manage_recruiters'),
]
