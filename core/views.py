from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Count
from accounts.models import User
from jobs.models import Job, Application

@user_passes_test(lambda u: u.is_staff)
def frontend_admin_dashboard(request):

    # Metrics
    total_users = User.objects.count()
    total_employers = User.objects.filter(is_employer=True).count()
    total_seekers = User.objects.filter(is_seeker=True).count()
    active_jobs = Job.objects.filter(is_active=True).count()
    total_applications = Application.objects.count()
    
    # Advanced Analytics
    # 1. Jobs by Employment Type
    jobs_by_type = Job.objects.values('employment_type').annotate(count=Count('id')).order_by('-count')
    cat_labels = [item['employment_type'] for item in jobs_by_type]
    cat_data = [item['count'] for item in jobs_by_type]

    # 2. Remote vs Onsite
    remote_jobs = Job.objects.filter(remote_status='REMOTE').count()
    onsite_jobs = Job.objects.exclude(remote_status='REMOTE').count()

    # 3. Top 5 Most Applied Jobs
    top_jobs = Job.objects.annotate(app_count=Count('applications')).order_by('-app_count')[:5]
    top_jobs_labels = [job.title for job in top_jobs]
    top_jobs_data = [job.app_count for job in top_jobs]
    
    # All Data for Tables
    all_users = User.objects.order_by('-date_joined')
    all_jobs = Job.objects.select_related('employer__employer_profile').order_by('-created_at')

    context = {
        'total_users': total_users,
        'total_employers': total_employers,
        'total_seekers': total_seekers,
        'active_jobs': active_jobs,
        'total_applications': total_applications,
        'all_users': all_users,
        'all_jobs': all_jobs,
        
        # Analytics Data
        'cat_labels': cat_labels,
        'cat_data': cat_data,
        'remote_jobs': remote_jobs,
        'onsite_jobs': onsite_jobs,
        'top_jobs_labels': top_jobs_labels,
        'top_jobs_data': top_jobs_data,
    }
    return render(request, 'core/admin_dashboard.html', context)

@user_passes_test(lambda u: u.is_staff)
def admin_toggle_user_status(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        if user == request.user:
            messages.error(request, "You cannot deactivate yourself!")
        else:
            user.is_active = not user.is_active
            user.save()
            status = "activated" if user.is_active else "deactivated"
            messages.success(request, f"User {user.email} has been {status}.")
    return redirect('frontend_admin')

@user_passes_test(lambda u: u.is_staff)
def admin_delete_job(request, job_id):
    if request.method == 'POST':
        job = get_object_or_404(Job, id=job_id)
        job.delete()
        messages.success(request, f"Job '{job.title}' has been deleted.")
    return redirect('frontend_admin')

def privacy_policy(request):
    return render(request, 'core/privacy.html')

def terms_of_service(request):
    return render(request, 'core/terms.html')

def help_center(request):
    return render(request, 'core/help.html')
