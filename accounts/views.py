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
                    
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            try:
                from core.emails import send_html_email
                from django.urls import reverse
                login_url = request.build_absolute_uri(reverse('login'))
                send_html_email(
                    subject='Welcome to JobBee!',
                    template_name='emails/welcome.html',
                    context={'user': user, 'login_url': login_url},
                    to_email=user.email
                )
            except Exception as e:
                print(f"Error sending welcome email: {e}")
                
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

from django.http import JsonResponse
from django.views.decorators.http import require_GET

@require_GET
def check_availability(request):
    username = request.GET.get('username', None)
    email = request.GET.get('email', None)
    
    response_data = {'available': True, 'message': ''}
    
    if username:
        if User.objects.filter(username__iexact=username).exists():
            response_data = {'available': False, 'message': 'Username is already taken.'}
            
    if email:
        if User.objects.filter(email__iexact=email).exists():
            response_data = {'available': False, 'message': 'Email is already associated with an account.'}
            
    return JsonResponse(response_data)

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json

@require_POST
def set_social_role(request):
    try:
        data = json.loads(request.body)
        role = data.get('role')
        if role in ['seeker', 'employer']:
            request.session['social_role'] = role
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'message': 'Invalid role'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

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
def edit_additional_info(request):
    if not getattr(request.user, 'is_seeker', False):
        return redirect('dashboard')
        
    profile = request.user.seeker_profile
    from .forms import SeekerAdditionalInfoForm
    
    if request.method == 'POST':
        form = SeekerAdditionalInfoForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Additional info updated successfully!')
            return redirect('dashboard')
    else:
        form = SeekerAdditionalInfoForm(instance=profile)
        
    return render(request, 'accounts/form_page.html', {'form': form, 'title': 'Edit Additional Information'})
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
def add_reference(request):
    if not getattr(request.user, 'is_seeker', False):
        return redirect('dashboard')
        
    if request.method == 'POST':
        from .forms import ReferenceForm
        form = ReferenceForm(request.POST)
        if form.is_valid():
            ref = form.save(commit=False)
            ref.seeker = request.user.seeker_profile
            ref.save()
            return redirect('resume_builder')
    else:
        from .forms import ReferenceForm
        form = ReferenceForm()
    return render(request, 'accounts/form_page.html', {'form': form, 'title': 'Add Reference'})
@login_required
def resume_builder(request):
    if not getattr(request.user, 'is_seeker', False):
        return redirect('dashboard')
    return render(request, 'accounts/resume_builder.html', {
        'profile': request.user.seeker_profile
    })

@login_required
def export_resume_pdf(request):
    applicant_id = request.GET.get('applicant_id')
    if applicant_id:
        if not getattr(request.user, 'is_employer', False):
            return redirect('dashboard')
        from jobs.models import Application
        from .models import User
        has_applied = Application.objects.filter(job__employer=request.user, applicant_id=applicant_id).exists()
        if not has_applied:
            return redirect('dashboard')
        target_user = get_object_or_404(User, id=applicant_id)
        profile = target_user.seeker_profile
    else:
        if not getattr(request.user, 'is_seeker', False):
            return redirect('dashboard')
        target_user = request.user
        profile = request.user.seeker_profile
    from .models import ResumeTemplate
    
    preview_template_id = request.GET.get('template_id')
    
    if preview_template_id:
        active_template = get_object_or_404(ResumeTemplate, id=preview_template_id)
    else:
        active_template = profile.active_resume_template
        if not active_template:
            active_template = ResumeTemplate.objects.filter(is_active=True).first()
        
    template_path = active_template.html_template if active_template else 'accounts/resume_templates/free.html'
    
    from django.template.loader import render_to_string
    from django.http import HttpResponse
    from xhtml2pdf import pisa
    
    html_string = render_to_string(template_path, {'profile': profile, 'user': target_user})
    response = HttpResponse(content_type='application/pdf')
    
    if request.GET.get('preview') == 'true':
        response['Content-Disposition'] = f'inline; filename="resume_{target_user.username}.pdf"'
    else:
        response['Content-Disposition'] = f'attachment; filename="resume_{target_user.username}.pdf"'
    
    pisa_status = pisa.CreatePDF(html_string, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html_string + '</pre>')
    return response

@login_required
def template_gallery(request):
    if not getattr(request.user, 'is_seeker', False):
        return redirect('dashboard')
        
    from .models import ResumeTemplate, PurchasedTemplate
    templates = ResumeTemplate.objects.filter(is_active=True).order_by('price')
    purchased = PurchasedTemplate.objects.filter(user=request.user).values_list('template_id', flat=True)
    
    if request.method == 'POST':
        template_id = request.POST.get('template_id')
        template = ResumeTemplate.objects.get(id=template_id)
        if template.is_free or template.id in purchased:
            request.user.seeker_profile.active_resume_template = template
            request.user.seeker_profile.save()
            messages.success(request, f'Template "{template.name}" selected!')
            return redirect('resume_builder')
            
    return render(request, 'accounts/template_gallery.html', {
        'templates': templates,
        'purchased_ids': list(purchased),
        'active_template': request.user.seeker_profile.active_resume_template
    })

@login_required
def buy_template(request, template_id):
    if not getattr(request.user, 'is_seeker', False):
        return redirect('dashboard')
        
    from .models import ResumeTemplate, PurchasedTemplate
    
    template = ResumeTemplate.objects.get(id=template_id)
    if template.is_free:
        return redirect('template_gallery')
        
    profile = request.user.seeker_profile
    
    final_price = float(template.price)
    discount_amount = 0.0
    applied_coupon = None
    
    coupon_code = request.POST.get('coupon_code')
    if coupon_code:
        from subscriptions.models import Coupon, CouponUsage
        coupon = Coupon.objects.filter(code__iexact=coupon_code).first()
        if coupon:
            is_valid, msg = coupon.check_validity()
            if is_valid:
                discount_amount = float(coupon.get_discount_amount(final_price))
                final_price = max(0.0, final_price - discount_amount)
                applied_coupon = coupon
            else:
                messages.error(request, msg)
                return redirect('template_gallery')
        else:
            messages.error(request, "Invalid coupon code.")
            return redirect('template_gallery')
            
    if profile.wallet_balance >= final_price:
        profile.wallet_balance -= final_price
        
        if applied_coupon:
            applied_coupon.times_used += 1
            applied_coupon.save()
            CouponUsage.objects.create(
                coupon=applied_coupon,
                user=request.user,
                discount_amount=discount_amount,
                order_type='TEMPLATE'
            )
        
        # Grant access
        PurchasedTemplate.objects.get_or_create(
            user=request.user,
            template=template
        )
        
        # Set as active
        profile.active_resume_template = template
        profile.save()
        
        messages.success(request, f'Successfully purchased {template.name}!')
        return redirect('resume_builder')
    else:
        messages.error(request, 'Insufficient wallet balance. Please top up your wallet.')
        return redirect('wallet_topup')

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

import json
@login_required
def wallet_topup(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        bkash_number = request.POST.get('bkash_number')
        transaction_id = request.POST.get('transaction_id')
        
        if amount and bkash_number and transaction_id:
            from .models import BKashTopUpRequest
            if BKashTopUpRequest.objects.filter(transaction_id=transaction_id).exists():
                messages.error(request, "This transaction ID has already been submitted.")
            else:
                BKashTopUpRequest.objects.create(
                    user=request.user,
                    amount=amount,
                    bkash_number=bkash_number,
                    transaction_id=transaction_id,
                    status='PENDING'
                )
                messages.success(request, "Your top-up request has been submitted and is pending admin approval.")
                return redirect('wallet_topup')
        else:
            messages.error(request, "Please fill in all fields.")
            
    return render(request, 'accounts/wallet_topup.html')

@login_required
def toggle_follow_employer(request, employer_id):
    if not request.user.is_seeker:
        return JsonResponse({'status': 'error', 'message': 'Only seekers can follow employers'})
    
    from .models import EmployerProfile, EmployerFollower
    employer = get_object_or_404(EmployerProfile, id=employer_id)
    seeker = request.user.seeker_profile
    
    follower, created = EmployerFollower.objects.get_or_create(
        employer=employer,
        seeker=seeker
    )
    
    if not created:
        follower.delete()
        is_following = False
        message = f"You unfollowed {employer.company_name}"
    else:
        is_following = True
        message = f"You are now following {employer.company_name}"
        
    return JsonResponse({
        'status': 'success',
        'is_following': is_following,
        'message': message
    })
