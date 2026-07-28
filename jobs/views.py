from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg, Count
from django.core.mail import send_mail
from django.conf import settings
from .models import Job, Application, JobEngagement, SavedCandidate
from accounts.models import EmployerProfile, CompanyReview, User
from django.views.decorators.cache import cache_page

def home(request):
    from .models import JobCategory
    recent_jobs = Job.objects.select_related('employer__employer_profile').filter(is_active=True).order_by('-created_at')[:6]
    
    # Calculate Dynamic Stats
    active_jobs_count = Job.objects.filter(is_active=True).count()
    employers_count = User.objects.filter(is_employer=True).count()
    
    processed_apps = Application.objects.exclude(status='PENDING').order_by('-updated_at')[:50]
    if processed_apps:
        total_seconds = sum((app.updated_at - app.applied_at).total_seconds() for app in processed_apps)
        avg_hours = max(1, int(total_seconds / len(processed_apps) / 3600))
    else:
        avg_hours = 24
        
    # Popular Categories
    from django.db.models import Count, Q
    categories = JobCategory.objects.annotate(
        active_job_count=Count('jobs', filter=Q(jobs__is_active=True))
    ).order_by('-active_job_count', 'name')[:50]
    
    # Trending Companies
    from accounts.models import EmployerProfile
    trending_companies = EmployerProfile.objects.annotate(
        active_job_count=Count('user__jobs_posted', filter=Q(user__jobs_posted__is_active=True))
    ).order_by('-active_job_count', 'company_name')[:50]
    
    # Pricing Plans for cards
    from subscriptions.models import Plan
    plans = Plan.objects.all().order_by('price')
        
    return render(request, 'jobs/home.html', {
        'recent_jobs': recent_jobs,
        'active_jobs_count': active_jobs_count,
        'employers_count': employers_count,
        'avg_hours': avg_hours,
        'categories': categories,
        'trending_companies': trending_companies,
        'plans': plans,
    })

from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from .forms import JobForm

@login_required
def post_job(request):
    if not request.user.is_employer:
        messages.error(request, 'Only employers can post jobs.')
        return redirect('home')
        
    employer_profile = getattr(request.user, 'employer_profile', None)
    if employer_profile and employer_profile.get_completion_percentage() < 50:
        messages.error(request, 'Your profile must be at least 50% complete to post a job. Please update your profile.')
        return redirect('edit_profile')
        
    try:
        subscription = request.user.employer_profile.subscription
        if not subscription.can_post_job():
            messages.error(request, 'You have reached your job limit or your subscription is inactive. Please upgrade your plan.')
            return redirect('subscriptions:pricing')
    except Exception:
        messages.error(request, 'You need an active subscription to post a job.')
        return redirect('subscriptions:pricing')

    if request.method == 'POST':
        form = JobForm(request.POST, subscription=subscription)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = request.user
            job.save()
            
            # Consume EXTRA_JOB token or increment jobs_posted
            if subscription.plan.job_limit != -1 and subscription.jobs_posted >= subscription.plan.job_limit:
                extra_token = request.user.employer_profile.addons.filter(addon__addon_type='EXTRA_JOB', is_used=False).first()
                if extra_token:
                    extra_token.is_used = True
                    extra_token.save()
            else:
                subscription.jobs_posted += 1
                subscription.save()
                
            # Consume FEATURED_JOB token if applicable
            if job.is_featured and not subscription.plan.can_feature_jobs:
                featured_token = request.user.employer_profile.addons.filter(addon__addon_type='FEATURED_JOB', is_used=False).first()
                if featured_token:
                    featured_token.is_used = True
                    featured_token.save()
            
            # Notify followers
            if hasattr(request.user, 'employer_profile'):
                employer_profile = request.user.employer_profile
                followers = employer_profile.followers.all()
                if followers.exists():
                    from accounts.models import Notification
                    from django.urls import reverse
                    job_url = reverse('job_detail', args=[job.id])
                    for follower in followers:
                        Notification.objects.create(
                            user=follower.seeker.user,
                            message=f"{employer_profile.company_name} just posted a new job: {job.title}",
                            link=job_url
                        )
            
            messages.success(request, 'Job posted successfully!')
            return redirect('dashboard')
    else:
        form = JobForm(subscription=subscription)
        
    return render(request, 'jobs/post_job.html', {'form': form})

def job_list(request):
    query = request.GET.get('q', '')
    location = request.GET.get('location', '')
    employment_type = request.GET.get('employment_type', '')
    remote_status = request.GET.get('remote_status', '')
    salary_min = request.GET.get('salary_min', '')
    date_posted = request.GET.get('date_posted', '')
    company_size = request.GET.get('company_size', '')
    is_verified = request.GET.get('is_verified', '')
    category_id = request.GET.get('category', '')
    
    jobs = Job.objects.select_related('employer__employer_profile').filter(is_active=True).order_by('-is_featured', '-created_at')
    
    if query:
        jobs = jobs.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(employer__employer_profile__company_name__icontains=query))
    if location:
        jobs = jobs.filter(location__icontains=location)
    if employment_type:
        jobs = jobs.filter(employment_type=employment_type)
    if remote_status:
        jobs = jobs.filter(remote_status=remote_status)
    if company_size:
        jobs = jobs.filter(employer__employer_profile__company_size=company_size)
    if is_verified == 'true':
        jobs = jobs.filter(employer__employer_profile__is_verified=True)
    if category_id:
        jobs = jobs.filter(category_id=category_id)
        
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
            
    # Pagination
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    page = request.GET.get('page', 1)
    paginator = Paginator(jobs, 15)
    
    try:
        jobs_page = paginator.page(page)
    except PageNotAnInteger:
        jobs_page = paginator.page(1)
    except EmptyPage:
        jobs_page = paginator.page(paginator.num_pages)
            
    from accounts.models import EmployerProfile
    return render(request, 'jobs/job_list.html', {
        'jobs': jobs_page,
        'total_jobs': jobs.count(),
        'query': query, 
        'location': location,
        'employment_type': employment_type,
        'remote_status': remote_status,
        'salary_min': salary_min,
        'date_posted': date_posted,
        'company_size': company_size,
        'is_verified': is_verified,
        'category_id': category_id,
        'EMPLOYMENT_TYPES': Job.EMPLOYMENT_TYPES,
        'REMOTE_STATUS': Job.REMOTE_STATUS,
        'COMPANY_SIZE_CHOICES': EmployerProfile.COMPANY_SIZE_CHOICES,
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
        
    if hasattr(request.user, 'seeker_profile'):
        completion = request.user.seeker_profile.get_completion_percentage()
        if completion < 70:
            from django.contrib import messages
            messages.error(request, f"Your profile is only {completion}% complete. You need at least 70% to apply for jobs.")
            return redirect('job_detail', job_id=job.id)
        
    if request.method == 'POST':
        cover_letter = request.POST.get('cover_letter', '')
        
        app, created = Application.objects.get_or_create(
            job=job,
            applicant=request.user,
            defaults={
                'cover_letter': cover_letter,
                'match_score': 0
            }
        )
        
        # Trigger Celery task
        from .tasks import async_calculate_match_score
        async_calculate_match_score.delay(app.id)
        
        if created:
            from accounts.models import Notification
            Notification.objects.create(
                user=job.employer,
                message=f"New application for {job.title} from {request.user.first_name or request.user.username}",
                link=f"/jobs/{job.id}/manage/"
            )
            
            try:
                from core.emails import send_html_email
                from django.urls import reverse
                dashboard_url = request.build_absolute_uri(reverse('manage_applicants', args=[job.id]))
                send_html_email(
                    subject=f'New Application: {job.title}',
                    template_name='emails/job_application.html',
                    context={
                        'job': job,
                        'employer_name': job.employer.first_name or job.employer.username,
                        'applicant_name': request.user.get_full_name() or request.user.username,
                        'applicant_email': request.user.email,
                        'application': app,
                        'dashboard_url': dashboard_url
                    },
                    to_email=job.employer.email
                )
            except Exception as e:
                print(f"Error sending job app email: {e}")
            
        JobEngagement.objects.create(job=job, user=request.user, action_type='CLICK')
        return redirect('job_detail', job_id=job.id)
        
    return render(request, 'jobs/apply.html', {'job': job})

@login_required
def manage_applicants(request, job_id):
    job = get_object_or_404(Job, id=job_id, employer=request.user)
    applications_qs = job.applications.select_related('applicant__seeker_profile').prefetch_related('applicant__seeker_profile__education', 'applicant__seeker_profile__experience', 'applicant__seeker_profile__certifications', 'applicant__assessment_results__assessment').all().order_by('-match_score', '-applied_at')
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
            
    # Location
    location_counts_qs = job.applications.exclude(applicant__seeker_profile__location='').values('applicant__seeker_profile__location').annotate(count=Count('id')).order_by('-count')[:5]
    location_labels = [item['applicant__seeker_profile__location'] for item in location_counts_qs]
    location_data = [item['count'] for item in location_counts_qs]
    if not location_labels:
        location_labels = ['No Data']
        location_data = [0]
        
    # Timeline (Last 7 Days)
    from django.utils import timezone
    from datetime import timedelta
    today = timezone.now().date()
    timeline_labels = [(today - timedelta(days=i)).strftime('%b %d') for i in range(6, -1, -1)]
    views_timeline = [0] * 7
    applications_timeline = [0] * 7
    
    seven_days_ago = timezone.now() - timedelta(days=6)
    engagements_last_7 = job.engagements.filter(timestamp__gte=seven_days_ago)
    for eng in engagements_last_7:
        day_diff = (today - eng.timestamp.date()).days
        day_idx = 6 - day_diff
        if 0 <= day_idx <= 6:
            if eng.action_type == 'VIEW':
                views_timeline[day_idx] += 1
            elif eng.action_type == 'CLICK':
                applications_timeline[day_idx] += 1
                
    analytics = {
        'total_views': total_views,
        'total_clicks': total_clicks,
        'conversion_rate': round((total_clicks / total_views * 100) if total_views > 0 else 0, 1),
        'gender_data': [gender_counts['M'], gender_counts['F'], gender_counts['O'], gender_counts['P'], gender_counts['Unknown']],
        'gender_labels': ['Male', 'Female', 'Other', 'Prefer Not to Say', 'Unknown'],
        'age_data': [age_counts['18-24'], age_counts['25-34'], age_counts['35-44'], age_counts['45-54'], age_counts['55+'], age_counts['Unknown']],
        'age_labels': ['18-24', '25-34', '35-44', '45-54', '55+', 'Unknown'],
        'location_labels': location_labels,
        'location_data': location_data,
        'timeline_labels': timeline_labels,
        'views_timeline': views_timeline,
        'applications_timeline': applications_timeline
    }
    
    try:
        sub = request.user.employer_profile.subscription
        has_advanced_matching = sub.is_active() and sub.plan.has_advanced_matching
    except Exception:
        has_advanced_matching = False
        
    return render(request, 'jobs/manage_applicants.html', {
        'job': job, 
        'board': board, 
        'analytics': json.dumps(analytics),
        'has_advanced_matching': has_advanced_matching
    })

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

                    from accounts.models import Notification
                    Notification.objects.create(
                        user=application.applicant,
                        message=f"Your application for '{application.job.title}' is now {application.get_status_display()}.",
                        link="/dashboard/"
                    )

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

@login_required
def save_candidate(request, seeker_id):
    if not getattr(request.user, 'is_employer', False):
        return JsonResponse({'success': False}, status=403)
        
    if request.method == 'POST':
        try:
            seeker = get_object_or_404(User, id=seeker_id, is_seeker=True)
            saved, created = SavedCandidate.objects.get_or_create(
                employer=request.user,
                seeker=seeker
            )
            return JsonResponse({'success': True, 'created': created})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False}, status=405)

@login_required
def talent_pool(request):
    if not getattr(request.user, 'is_employer', False):
        return redirect('dashboard')
        
    saved_candidates = SavedCandidate.objects.filter(employer=request.user).select_related('seeker__seeker_profile').order_by('-saved_at')
    
    return render(request, 'jobs/talent_pool.html', {
        'saved_candidates': saved_candidates
    })

@login_required
def save_search(request):
    if not getattr(request.user, 'is_seeker', False):
        return JsonResponse({'success': False}, status=403)
        
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            query = data.get('query', '')
            location = data.get('location', '')
            SavedSearch.objects.create(user=request.user, query=query, location=location)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False}, status=405)

@login_required
def assessments_view(request):
    if not getattr(request.user, 'is_seeker', False):
        return redirect('home')
        
    from .models import Assessment, AssessmentResult
    assessments = Assessment.objects.all()
    results = AssessmentResult.objects.filter(seeker=request.user)
    results_dict = {r.assessment_id: r.score for r in results}
    
    return render(request, 'jobs/assessments.html', {
        'assessments': assessments,
        'results_dict': results_dict
    })

@login_required
def take_assessment(request, assessment_id):
    if not getattr(request.user, 'is_seeker', False):
        return redirect('home')
        
    from .models import Assessment, AssessmentResult
    assessment = get_object_or_404(Assessment, id=assessment_id)
    
    if request.method == 'POST':
        import random
        score = random.randint(65, 100)
        
        result, created = AssessmentResult.objects.get_or_create(
            seeker=request.user,
            assessment=assessment,
            defaults={'score': score}
        )
        
        if not created:
            result.score = score
            result.save()
            
        messages.success(request, f"You scored {score}% on the {assessment.name}!")
        return redirect('assessments')
        
    return render(request, 'jobs/take_assessment.html', {'assessment': assessment})
