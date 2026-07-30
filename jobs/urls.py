from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/new/', views.post_job, name='post_job'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('jobs/<int:job_id>/edit/', views.edit_job, name='edit_job'),
    path('jobs/<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('jobs/<int:job_id>/manage/', views.manage_applicants, name='manage_applicants'),
    path('applications/<int:application_id>/update-status/', views.update_application_status, name='update_application_status'),
    path('company/<int:company_id>/', views.company_detail, name='company_detail'),
    path('company/<int:company_id>/review/', views.add_review, name='add_review'),
    path('candidates/<int:seeker_id>/save/', views.save_candidate, name='save_candidate'),
    path('talent-pool/', views.talent_pool, name='talent_pool'),
    path('save-search/', views.save_search, name='save_search'),
    path('assessments/', views.assessments_view, name='assessments'),
    path('assessments/<int:assessment_id>/take/', views.take_assessment, name='take_assessment'),
    path('employers/', views.employer_list, name='employer_list'),
]
