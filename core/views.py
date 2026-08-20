from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Count
from accounts.models import User
from jobs.models import Job, Application
from .models import HeroSectionSettings
from .forms import HeroSectionSettingsForm

@user_passes_test(lambda u: u.is_staff)
def admin_hero_settings(request):
    settings_obj = HeroSectionSettings.objects.first()
    if not settings_obj:
        settings_obj = HeroSectionSettings.objects.create()
        
    if request.method == 'POST':
        form = HeroSectionSettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hero section settings updated successfully.')
            return redirect('admin_hero_settings')
    else:
        form = HeroSectionSettingsForm(instance=settings_obj)
        
    return render(request, 'core/admin_hero_settings.html', {'form': form})

@user_passes_test(lambda u: u.is_staff)
def admin_trusted_companies(request):
    from .models import TrustedCompany
    from .forms import TrustedCompanyForm
    
    companies = TrustedCompany.objects.all()
    
    if request.method == 'POST':
        form = TrustedCompanyForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Company logo added successfully.')
            return redirect('admin_trusted_companies')
    else:
        form = TrustedCompanyForm()
        
    return render(request, 'core/admin_trusted_companies.html', {'companies': companies, 'form': form})

@user_passes_test(lambda u: u.is_staff)
def admin_delete_trusted_company(request, company_id):
    from .models import TrustedCompany
    if request.method == 'POST':
        company = get_object_or_404(TrustedCompany, id=company_id)
        company.delete()
        messages.success(request, f"Company '{company.name}' deleted.")
    return redirect('admin_trusted_companies')

@user_passes_test(lambda u: u.is_staff)
def frontend_admin_dashboard(request):

    from subscriptions.models import EmployerSubscription, Transaction
    from django.db.models import Sum

    # Metrics
    total_users = User.objects.count()
    total_employers = User.objects.filter(is_employer=True).count()
    total_seekers = User.objects.filter(is_seeker=True).count()
    active_jobs = Job.objects.filter(is_active=True).count()
    total_applications = Application.objects.count()
    
    # Subscription Metrics
    active_subscriptions = EmployerSubscription.objects.filter(status='ACTIVE').count()
    total_revenue = Transaction.objects.filter(status='COMPLETED').aggregate(Sum('amount'))['amount__sum'] or 0
    
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
    
    # 4. Monthly Revenue Trend
    from django.db.models.functions import TruncMonth
    import json
    monthly_revenue = Transaction.objects.filter(status='COMPLETED').annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(total=Sum('amount')).order_by('month')
    
    revenue_labels = [rev['month'].strftime('%b %Y') for rev in monthly_revenue if rev['month']]
    revenue_data = [float(rev['total']) for rev in monthly_revenue]
    
    # All Data for Tables
    all_users = User.objects.order_by('-date_joined')
    all_jobs = Job.objects.select_related('employer__employer_profile').order_by('-created_at')
    
    from accounts.models import BKashTopUpRequest
    bkash_requests = BKashTopUpRequest.objects.all().order_by('-created_at')

    context = {
        'total_users': total_users,
        'total_employers': total_employers,
        'total_seekers': total_seekers,
        'active_jobs': active_jobs,
        'total_applications': total_applications,
        'active_subscriptions': active_subscriptions,
        'total_revenue': total_revenue,
        'all_users': all_users,
        'all_jobs': all_jobs,
        'bkash_requests': bkash_requests,
        
        # Analytics Data
        'cat_labels': cat_labels,
        'cat_data': cat_data,
        'remote_jobs': remote_jobs,
        'onsite_jobs': onsite_jobs,
        'top_jobs_labels': top_jobs_labels,
        'top_jobs_data': top_jobs_data,
        
        # Financial BI
        'revenue_labels': json.dumps(revenue_labels),
        'revenue_data': json.dumps(revenue_data),
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
def admin_toggle_employer_verification(request, profile_id):
    if request.method == 'POST':
        from accounts.models import EmployerProfile
        profile = get_object_or_404(EmployerProfile, id=profile_id)
        profile.is_verified = not profile.is_verified
        profile.save()
        status = "verified" if profile.is_verified else "unverified"
        messages.success(request, f"Employer {profile.company_name} has been {status}.")
    return redirect('frontend_admin')

@user_passes_test(lambda u: u.is_staff)
def admin_delete_job(request, job_id):
    if request.method == 'POST':
        job = get_object_or_404(Job, id=job_id)
        job.delete()
        messages.success(request, f"Job '{job.title}' has been deleted.")
    return redirect('frontend_admin')

@user_passes_test(lambda u: u.is_staff)
def admin_bkash_approve(request, request_id):
    if request.method == 'POST':
        from accounts.models import BKashTopUpRequest
        bkash_request = get_object_or_404(BKashTopUpRequest, id=request_id)
        if bkash_request.status == 'PENDING':
            bkash_request.status = 'APPROVED'
            bkash_request.save()
            messages.success(request, f"bKash Top-Up {bkash_request.transaction_id} approved.")
    return redirect('frontend_admin')

@user_passes_test(lambda u: u.is_staff)
def admin_bkash_reject(request, request_id):
    if request.method == 'POST':
        from accounts.models import BKashTopUpRequest
        bkash_request = get_object_or_404(BKashTopUpRequest, id=request_id)
        if bkash_request.status == 'PENDING':
            bkash_request.status = 'REJECTED'
            bkash_request.save()
            messages.success(request, f"bKash Top-Up {bkash_request.transaction_id} rejected.")
    return redirect('frontend_admin')

def privacy_policy(request):
    return render(request, 'core/privacy.html')

def terms_of_service(request):
    return render(request, 'core/terms.html')

@user_passes_test(lambda u: u.is_staff)
def export_platform_data_csv(request):
    import csv
    from django.http import HttpResponse
    from jobs.models import Job, Application
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="jobbee_bi_data.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Job ID', 'Title', 'Employer', 'Category', 'Employment Type', 'Remote Status', 'Created At', 'Views Count', 'Applications Count', 'Hired Count'])
    
    jobs = Job.objects.annotate(
        app_count=Count('applications')
    ).select_related('employer__employer_profile', 'category')
    
    for job in jobs:
        employer_name = job.employer.employer_profile.company_name if hasattr(job.employer, 'employer_profile') else job.employer.username
        category_name = job.category.name if job.category else "Uncategorized"
        hired_count = Application.objects.filter(job=job, status='OFFER').count()
        
        writer.writerow([
            job.id,
            job.title,
            employer_name,
            category_name,
            job.get_employment_type_display(),
            job.get_remote_status_display(),
            job.created_at.strftime('%Y-%m-%d'),
            job.views_count,
            job.app_count,
            hired_count
        ])
        
    return response

def help_center(request):
    return render(request, 'core/help.html')

# Testimonial CMS Views
@user_passes_test(lambda u: u.is_staff)
def admin_testimonials(request):
    from .models import Testimonial
    testimonials = Testimonial.objects.all()
    return render(request, 'core/admin_testimonials.html', {'testimonials': testimonials})

@user_passes_test(lambda u: u.is_staff)
def admin_create_testimonial(request):
    from .forms import TestimonialForm
    if request.method == 'POST':
        form = TestimonialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Testimonial created successfully!')
            return redirect('admin_testimonials')
    else:
        form = TestimonialForm()
    return render(request, 'core/admin_testimonial_form.html', {'form': form, 'title': 'Create Testimonial'})

@user_passes_test(lambda u: u.is_staff)
def admin_edit_testimonial(request, pk):
    from .models import Testimonial
    from .forms import TestimonialForm
    testimonial = get_object_or_404(Testimonial, pk=pk)
    if request.method == 'POST':
        form = TestimonialForm(request.POST, request.FILES, instance=testimonial)
        if form.is_valid():
            form.save()
            messages.success(request, 'Testimonial updated successfully!')
            return redirect('admin_testimonials')
    else:
        form = TestimonialForm(instance=testimonial)
    return render(request, 'core/admin_testimonial_form.html', {'form': form, 'title': 'Edit Testimonial', 'testimonial': testimonial})

@user_passes_test(lambda u: u.is_staff)
def admin_delete_testimonial(request, pk):
    from .models import Testimonial
    testimonial = get_object_or_404(Testimonial, pk=pk)
    if request.method == 'POST':
        testimonial.delete()
        messages.success(request, 'Testimonial deleted successfully!')
    return redirect('admin_testimonials')

def about_us(request):
    return render(request, 'core/about.html')

def services(request):
    from .models import Service
    services_list = Service.objects.all()
    return render(request, 'core/services.html', {'services': services_list})

def contact_us(request):
    return render(request, 'core/contact.html')

def subscribe_newsletter(request):
    from .models import NewsletterSubscriber
    from django.contrib import messages
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            NewsletterSubscriber.objects.get_or_create(email=email)
            messages.success(request, "Thank you for subscribing to our newsletter!")
    return redirect(request.META.get('HTTP_REFERER', '/'))

def set_currency(request):
    if request.method == 'POST':
        currency = request.POST.get('currency', 'BDT')
        request.session['user_currency'] = currency
    next_url = request.META.get('HTTP_REFERER', '/')
    return redirect(next_url)
