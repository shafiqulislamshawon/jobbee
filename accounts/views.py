from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from jobs.models import Job, Application
from .models import User
from .forms import CustomUserCreationForm, SeekerProfileForm, EducationForm, ExperienceForm, CertificationForm

@login_required
def applicant_profile(request, user_id):
    applicant = get_object_or_404(User, id=user_id, is_seeker=True)
    seeker_profile = getattr(applicant, 'seeker_profile', None)
    return render(request, 'accounts/applicant_profile.html', {
        'applicant': applicant,
        'seeker_profile': seeker_profile
    })

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def dashboard(request):
    from django.db.models import Sum
    from jobs.models import Job, Application
    
    if request.user.is_employer:
        jobs = Job.objects.filter(employer=request.user).order_by('-created_at')
        total_jobs = jobs.count()
        total_views = jobs.aggregate(Sum('views_count'))['views_count__sum'] or 0
        total_applicants = Application.objects.filter(job__employer=request.user).count()
        
        return render(request, 'accounts/employer_dashboard.html', {
            'jobs': jobs,
            'total_jobs': total_jobs,
            'total_views': total_views,
            'total_applicants': total_applicants
        })
    elif request.user.is_seeker:
        applications = request.user.applications.all().order_by('-applied_at')
        
        total_applications = applications.count()
        pending_applications = applications.filter(status='PENDING').count()
        rejected_applications = applications.filter(status='REJECTED').count()
        
        return render(request, 'accounts/seeker_dashboard.html', {
            'applications': applications,
            'total_applications': total_applications,
            'pending_applications': pending_applications,
            'rejected_applications': rejected_applications
        })
    return redirect('home')

@login_required
def edit_profile(request):
    if not getattr(request.user, 'is_seeker', False):
        return redirect('dashboard')
    
    profile = request.user.seeker_profile
    if request.method == 'POST':
        form = SeekerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = SeekerProfileForm(instance=profile)
        
    return render(request, 'accounts/form_page.html', {'form': form, 'title': 'Edit Profile'})

@login_required
def add_education(request):
    if not getattr(request.user, 'is_seeker', False):
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            edu = form.save(commit=False)
            edu.seeker = request.user.seeker_profile
            edu.save()
            return redirect('dashboard')
    else:
        form = EducationForm()
    return render(request, 'accounts/form_page.html', {'form': form, 'title': 'Add Education'})

@login_required
def add_experience(request):
    if not getattr(request.user, 'is_seeker', False):
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = ExperienceForm(request.POST)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.seeker = request.user.seeker_profile
            exp.save()
            return redirect('dashboard')
    else:
        form = ExperienceForm()
    return render(request, 'accounts/form_page.html', {'form': form, 'title': 'Add Experience'})

@login_required
def add_certification(request):
    if not getattr(request.user, 'is_seeker', False):
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = CertificationForm(request.POST)
        if form.is_valid():
            cert = form.save(commit=False)
            cert.seeker = request.user.seeker_profile
            cert.save()
            return redirect('dashboard')
    else:
        form = CertificationForm()
    return render(request, 'accounts/form_page.html', {'form': form, 'title': 'Add Certification'})

