from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg, Count
from django.core.mail import send_mail
from django.conf import settings
from .models import Job, Application, JobEngagement
from accounts.models import EmployerProfile, CompanyReview

def home(request):
    recent_jobs = Job.objects.select_related('employer__employer_profile').filter(is_active=True).order_by('-created_at')[:6]
    return render(request, 'jobs/home.html', {'recent_jobs': recent_jobs})

from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from .forms import JobForm

@login_required
def post_job(request):
    if not request.user.is_employer:
        messages.error(request, 'Only employers can post jobs.')
        return redirect('home')
        
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = request.user
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('dashboard')
    else:
        form = JobForm()
        
    return render(request, 'jobs/post_job.html', {'form': form})

def job_list(request):
    query = request.GET.get('q', '')
    location = request.GET.get('location', '')
    employment_type = request.GET.get('employment_type', '')
    remote_status = request.GET.get('remote_status', '')
    salary_min = request.GET.get('salary_min', '')
    date_posted = request.GET.get('date_posted', '')
    
    jobs = Job.objects.select_related('employer__employer_profile').filter(is_active=True).order_by('-created_at')
    
    if query:
        jobs = jobs.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(employer__employer_profile__company_name__icontains=query))
    if location:
        jobs = jobs.filter(location__icontains=location)
    if employment_type:
        jobs = jobs.filter(employment_type=employment_type)
    if remote_status:
        jobs = jobs.filter(remote_status=remote_status)
        
    if salary_min:
        try:
            salary_val = int(salary_min)
            jobs = jobs.filter(salary_min__gte=salary_val)
        except ValueError:
            pass
            
    if date_posted:
        now = timezone.now()
        if date_posted == '24h':
            jobs = jobs.filter(created_at__gte=now - timedelta(days=1))
        elif date_posted == '7d':
            jobs = jobs.filter(created_at__gte=now - timedelta(days=7))
        elif date_posted == '30d':
            jobs = jobs.filter(created_at__gte=now - timedelta(days=30))
            
    return render(request, 'jobs/job_list.html', {
        'jobs': jobs, 
        'query': query, 
        'location': location,
        'employment_type': employment_type,
        'remote_status': remote_status,
        'salary_min': salary_min,
        'date_posted': date_posted,
        'EMPLOYMENT_TYPES': Job.EMPLOYMENT_TYPES,
        'REMOTE_STATUS': Job.REMOTE_STATUS
    })

def job_detail(request, job_id):
    job = get_object_or_404(Job.objects.select_related('employer__employer_profile'), id=job_id, is_active=True)
    
    # Increment view count and track engagement
    job.views_count += 1
    job.save(update_fields=['views_count'])
    
    user = request.user if request.user.is_authenticated else None
    JobEngagement.objects.create(job=job, user=user, action_type='VIEW')
    
    has_applied = False
    if request.user.is_authenticated and request.user.is_seeker:
        has_applied = Application.objects.filter(job=job, applicant=request.user).exists()
        
    return render(request, 'jobs/job_detail.html', {'job': job, 'has_applied': has_applied})

@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if not request.user.is_seeker:
        return redirect('job_detail', job_id=job.id)
        
    if request.method == 'POST':
        cover_letter = request.POST.get('cover_letter', '')
        Application.objects.get_or_create(
            job=job,
            applicant=request.user,
            defaults={'cover_letter': cover_letter}
        )
        JobEngagement.objects.create(job=job, user=request.user, action_type='CLICK')
        return redirect('job_detail', job_id=job.id)
        
    return render(request, 'jobs/apply.html', {'job': job})

@login_required
def manage_applicants(request, job_id):
    job = get_object_or_404(Job, id=job_id, employer=request.user)
    applications_qs = job.applications.select_related('applicant__seeker_profile').prefetch_related('applicant__seeker_profile__education', 'applicant__seeker_profile__experience', 'applicant__seeker_profile__certifications').all()
    applications = list(applications_qs)
    
    board = {
        'PENDING': [app for app in applications if app.status == 'PENDING'],
        'REVIEWED': [app for app in applications if app.status == 'REVIEWED'],
        'SHORTLISTED': [app for app in applications if app.status == 'SHORTLISTED'],
        'INTERVIEW': [app for app in applications if app.status == 'INTERVIEW'],
        'OFFER': [app for app in applications if app.status == 'OFFER'],
        'REJECTED': [app for app in applications if app.status == 'REJECTED'],
    }
    
    # Analytics Aggregation (Optimized with DB aggregation)
    total_views = job.engagements.filter(action_type='VIEW').count()
    total_clicks = job.engagements.filter(action_type='CLICK').count()
    
    gender_counts_qs = job.engagements.filter(user__isnull=False).values('user__seeker_profile__gender').annotate(count=Count('id'))
    age_counts_qs = job.engagements.filter(user__isnull=False).values('user__seeker_profile__age_group').annotate(count=Count('id'))
    
    gender_counts = {'M': 0, 'F': 0, 'O': 0, 'P': 0, 'Unknown': 0}
    for item in gender_counts_qs:
        g = item['user__seeker_profile__gender'] if item['user__seeker_profile__gender'] else 'Unknown'
        if g in gender_counts:
            gender_counts[g] += item['count']
        else:
            gender_counts['Unknown'] += item['count']
            
    age_counts = {'18-24': 0, '25-34': 0, '35-44': 0, '45-54': 0, '55+': 0, 'Unknown': 0}
    for item in age_counts_qs:
        a = item['user__seeker_profile__age_group'] if item['user__seeker_profile__age_group'] else 'Unknown'
        if a in age_counts:
            age_counts[a] += item['count']
        else:
            age_counts['Unknown'] += item['count']
                
    analytics = {
        'total_views': total_views,
        'total_clicks': total_clicks,
        'conversion_rate': round((total_clicks / total_views * 100) if total_views > 0 else 0, 1),
        'gender_data': [gender_counts['M'], gender_counts['F'], gender_counts['O'], gender_counts['P'], gender_counts['Unknown']],
        'gender_labels': ['Male', 'Female', 'Other', 'Prefer Not to Say', 'Unknown'],
        'age_data': [age_counts['18-24'], age_counts['25-34'], age_counts['35-44'], age_counts['45-54'], age_counts['55+'], age_counts['Unknown']],
        'age_labels': ['18-24', '25-34', '35-44', '45-54', '55+', 'Unknown']
    }
    
    return render(request, 'jobs/manage_applicants.html', {'job': job, 'board': board, 'analytics': json.dumps(analytics)})

@login_required
def update_application_status(request, application_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_status = data.get('status')
            
            application = get_object_or_404(Application, id=application_id, job__employer=request.user)
            if new_status in dict(Application.STATUS_CHOICES):
                old_status = application.status
                application.status = new_status
                application.save()
                
                if old_status != new_status and application.applicant.email:
                    subject = f"Update on your application for {application.job.title}"
                    company_name = application.job.employer.employer_profile.company_name or application.job.employer.username
                    message = f"Hello {application.applicant.first_name or application.applicant.username},\n\nYour application status for '{application.job.title}' at {company_name} has been updated to: {application.get_status_display()}.\n\nGood luck!\n- JobBee Team"
                    send_mail(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@jobbee.com'), [application.applicant.email], fail_silently=True)

                return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False}, status=405)

def company_detail(request, company_id):
    company = get_object_or_404(EmployerProfile, id=company_id)
    jobs = Job.objects.filter(employer=company.user, is_active=True).order_by('-created_at')
    reviews = company.reviews.select_related('reviewer').all().order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    return render(request, 'jobs/company_detail.html', {
        'company': company,
        'jobs': jobs,
        'reviews': reviews,
        'avg_rating': avg_rating
    })

@login_required
def add_review(request, company_id):
    if not getattr(request.user, 'is_seeker', False):
        return redirect('company_detail', company_id=company_id)
        
    company = get_object_or_404(EmployerProfile, id=company_id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        title = request.POST.get('title')
        body = request.POST.get('body')
        
        if rating and title and body:
            CompanyReview.objects.create(
                employer=company,
                reviewer=request.user,
                rating=int(rating),
                title=title,
                body=body
            )
            return redirect('company_detail', company_id=company.id)
            
    return render(request, 'jobs/add_review.html', {'company': company})
