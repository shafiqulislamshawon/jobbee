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

from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='10/m', block=True)
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            ref_id = request.session.get('referred_by')
            if ref_id:
                try:
                    from .models import Referral
                    referrer = User.objects.get(id=ref_id)
                    ref_obj = Referral.objects.filter(referred_email=user.email, referrer=referrer).first()
                    if not ref_obj:
                        ref_obj = Referral.objects.create(referrer=referrer, referred_email=user.email, status='REGISTERED')
                    ref_obj.status = 'REGISTERED'
                    ref_obj.referred_user = user
                    ref_obj.save()
                    del request.session['referred_by']
                except Exception:
                    pass
                    
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
        
        import json
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models.functions import TruncDate
        from django.db.models import Count
        
        # 1. Funnel Analytics
        shortlisted = Application.objects.filter(job__employer=request.user, status='SHORTLISTED').count()
        hired = Application.objects.filter(job__employer=request.user, status='OFFER').count()
        funnel_data = [total_views, total_applicants, shortlisted, hired]
        
        # 2. Application Trend (Last 30 Days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        daily_apps = Application.objects.filter(
            job__employer=request.user, 
            applied_at__gte=thirty_days_ago
        ).annotate(date=TruncDate('applied_at')).values('date').annotate(count=Count('id')).order_by('date')
        
        trend_labels = [app['date'].strftime('%b %d') for app in daily_apps]
        trend_data = [app['count'] for app in daily_apps]
        
        # Fill in missing days if necessary (optional, but let's keep it simple and just show active days for now)

        try:
            subscription = request.user.employer_profile.subscription
        except Exception:
            subscription = None
            
        return render(request, 'accounts/employer_dashboard.html', {
            'jobs': jobs,
            'total_jobs': total_jobs,
            'total_views': total_views,
            'total_applicants': total_applicants,
            'subscription': subscription,
            'funnel_data': json.dumps(funnel_data),
            'trend_labels': json.dumps(trend_labels),
            'trend_data': json.dumps(trend_data),
        })
    elif request.user.is_seeker:
        applications = request.user.applications.all().order_by('-applied_at')
        
        total_applications = applications.count()
        pending_applications = applications.filter(status='PENDING').count()
        rejected_applications = applications.filter(status='REJECTED').count()
        
        from jobs.utils import calculate_match_score
        active_jobs = Job.objects.filter(is_active=True).exclude(applications__applicant=request.user)
        recommended_jobs = []
        for job in active_jobs:
            score = calculate_match_score(job, request.user.seeker_profile)
            if score >= 30: # Only somewhat relevant jobs
                recommended_jobs.append({'job': job, 'score': score})
        recommended_jobs.sort(key=lambda x: x['score'], reverse=True)
        recommended_jobs = recommended_jobs[:5]
        
        return render(request, 'accounts/seeker_dashboard.html', {
            'applications': applications,
            'total_applications': total_applications,
            'pending_applications': pending_applications,
            'rejected_applications': rejected_applications,
            'recommended_jobs': recommended_jobs
        })
    return redirect('home')

@login_required
def edit_profile(request):
    if getattr(request.user, 'is_seeker', False):
        profile = request.user.seeker_profile
        FormClass = SeekerProfileForm
    elif getattr(request.user, 'is_employer', False):
        profile = request.user.employer_profile
        from .forms import EmployerProfileForm
        FormClass = EmployerProfileForm
    else:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            if request.user.is_employer:
                try:
                    sub = profile.subscription
                    has_banner_perm = sub.is_active() and sub.plan.has_banner
                except Exception:
                    has_banner_perm = False
                
                if not has_banner_perm and 'company_banner' in request.FILES:
                    messages.error(request, 'Your current plan does not support company banners. Please upgrade.')
                    return redirect('edit_profile')
                    
            form.save()
            
            if getattr(request.user, 'is_seeker', False):
                from .utils import analyze_resume
                analyze_resume(profile)
                
            messages.success(request, 'Profile updated successfully!')
            return redirect('dashboard')
    else:
        form = FormClass(instance=profile)
        
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
            from .utils import analyze_resume
            analyze_resume(request.user.seeker_profile)
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
            from .utils import analyze_resume
            analyze_resume(request.user.seeker_profile)
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
            from .utils import analyze_resume
            analyze_resume(request.user.seeker_profile)
            return redirect('dashboard')
    else:
        form = CertificationForm()
    return render(request, 'accounts/form_page.html', {'form': form, 'title': 'Add Certification'})

@login_required
def resume_builder(request):
    if not getattr(request.user, 'is_seeker', False):
        return redirect('dashboard')
    return render(request, 'accounts/resume_builder.html', {
        'profile': request.user.seeker_profile
    })

@login_required
def export_resume_pdf(request):
    if not getattr(request.user, 'is_seeker', False):
        return redirect('dashboard')
        
    profile = request.user.seeker_profile
    
    from django.http import HttpResponse
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="resume_{request.user.username}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    
    Story = []
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(name='Name', fontSize=24, leading=28, spaceAfter=12, textColor=colors.HexColor('#1f2937')))
    styles.add(ParagraphStyle(name='Contact', fontSize=10, leading=14, spaceAfter=24, textColor=colors.HexColor('#4b5563')))
    styles.add(ParagraphStyle(name='Heading', fontSize=14, leading=18, spaceAfter=6, spaceBefore=18, textColor=colors.HexColor('#111827'), fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='SubHeading', fontSize=12, leading=14, spaceAfter=4, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='BodyText', fontSize=10, leading=14, spaceAfter=12))
    styles.add(ParagraphStyle(name='DateText', fontSize=10, leading=14, spaceAfter=6, textColor=colors.HexColor('#6b7280')))

    # Name
    name = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
    Story.append(Paragraph(name, styles['Name']))
    
    # Contact Info
    contact_parts = [request.user.email]
    if profile.portfolio_url:
        contact_parts.append(profile.portfolio_url)
    contact_str = " | ".join(contact_parts)
    Story.append(Paragraph(contact_str, styles['Contact']))
    
    if profile.experience.exists():
        Story.append(Paragraph("EXPERIENCE", styles['Heading']))
        Story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb'), spaceAfter=12))
        for exp in profile.experience.all().order_by('-start_date'):
            Story.append(Paragraph(exp.job_title, styles['SubHeading']))
            dates = f"{exp.start_date.strftime('%B %Y')} - {'Present' if exp.is_current else exp.end_date.strftime('%B %Y')}"
            Story.append(Paragraph(f"{exp.company} | {dates}", styles['DateText']))
            if exp.description:
                Story.append(Paragraph(exp.description, styles['BodyText']))
            else:
                Story.append(Spacer(1, 12))
                
    if profile.education.exists():
        Story.append(Paragraph("EDUCATION", styles['Heading']))
        Story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb'), spaceAfter=12))
        for edu in profile.education.all().order_by('-start_date'):
            degree = f"{edu.degree}" + (f" in {edu.field_of_study}" if edu.field_of_study else "")
            Story.append(Paragraph(degree, styles['SubHeading']))
            dates = f"{edu.start_date.strftime('%Y')} - {edu.end_date.strftime('%Y') if edu.end_date else 'Present'}"
            Story.append(Paragraph(f"{edu.institution} | {dates}", styles['DateText']))
            if edu.description:
                Story.append(Paragraph(edu.description, styles['BodyText']))
            else:
                Story.append(Spacer(1, 12))

    if profile.skills:
        Story.append(Paragraph("SKILLS", styles['Heading']))
        Story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb'), spaceAfter=12))
        Story.append(Paragraph(profile.skills, styles['BodyText']))

    if profile.certifications.exists():
        Story.append(Paragraph("CERTIFICATIONS", styles['Heading']))
        Story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb'), spaceAfter=12))
        for cert in profile.certifications.all().order_by('-issue_date'):
            Story.append(Paragraph(cert.name, styles['SubHeading']))
            Story.append(Paragraph(f"{cert.issuer} | Issued: {cert.issue_date.strftime('%Y')}", styles['DateText']))
            Story.append(Spacer(1, 6))
            
    doc.build(Story)
    return response

from django.contrib import messages

@login_required
def referrals_view(request):
    from .models import Referral
    user_referrals = request.user.referrals_made.all().order_by('-created_at')
    
    total_invites = user_referrals.count()
    successful = user_referrals.filter(status__in=['REGISTERED', 'REWARDED']).count()
    
    credits = 0
    if getattr(request.user, 'is_employer', False):
        try:
            credits = request.user.employer_profile.credits
        except Exception:
            pass
            
    from django.urls import reverse
    ref_link = request.build_absolute_uri(reverse('referral_signup', args=[request.user.id]))
    
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            if not Referral.objects.filter(referred_email=email).exists() and not User.objects.filter(email=email).exists():
                Referral.objects.create(referrer=request.user, referred_email=email)
                messages.success(request, f"Invitation tracked for {email}!")
            else:
                messages.error(request, f"{email} has already been invited or registered.")
        return redirect('referrals')

    return render(request, 'accounts/referrals.html', {
        'referrals': user_referrals,
        'total_invites': total_invites,
        'successful': successful,
        'credits': credits,
        'ref_link': ref_link
    })

def referral_signup(request, ref_id):
    request.session['referred_by'] = ref_id
    return redirect('register')

@login_required
def notifications_view(request):
    notifications = request.user.notifications.all()
    # Mark all as read when viewed
    notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'accounts/notifications.html', {'notifications': notifications})

@login_required
def get_unread_count(request):
    from django.http import JsonResponse
    count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'count': count})

@login_required
def employer_verification(request):
    if not getattr(request.user, 'is_employer', False):
        return redirect('home')
        
    from django.contrib import messages
    employer_profile = request.user.employer_profile
    
    if request.method == 'POST':
        if 'verification_document' in request.FILES:
            employer_profile.verification_document = request.FILES['verification_document']
            employer_profile.verification_status = 'PENDING'
            employer_profile.save()
            messages.success(request, 'Verification document submitted successfully. Please wait for admin approval.')
            return redirect('dashboard')
            
    return render(request, 'accounts/employer_verification.html', {'employer_profile': employer_profile})

@login_required
def manage_recruiters(request):
    if not getattr(request.user, 'is_employer', False):
        return redirect('home')
        
    from django.contrib import messages
    from .models import RecruiterSeat
    employer_profile = request.user.employer_profile
    seats = RecruiterSeat.objects.filter(employer_profile=employer_profile)
    
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            try:
                user, created = User.objects.get_or_create(username=email, defaults={'email': email, 'is_employer': True})
                if created:
                    user.set_password('jobbee123')
                    user.save()
                    
                RecruiterSeat.objects.get_or_create(employer_profile=employer_profile, user=user)
                messages.success(request, f"Invited {email} as a recruiter! They can login with password 'jobbee123'.")
            except Exception as e:
                messages.error(request, f"Error inviting recruiter: {str(e)}")
        return redirect('manage_recruiters')
        
    return render(request, 'accounts/manage_recruiters.html', {'seats': seats})

