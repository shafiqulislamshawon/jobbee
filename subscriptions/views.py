from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
import json
from .models import Plan, EmployerSubscription, Transaction, AddOn, EmployerAddOn, AdSpace, AdBooking, Coupon

@login_required
def validate_coupon(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code')
            total = float(data.get('total', 0))
            
            coupon = Coupon.objects.filter(code__iexact=code).first()
            if not coupon:
                return JsonResponse({'valid': False, 'message': 'Invalid coupon code.'})
                
            is_valid, msg = coupon.check_validity()
            if not is_valid:
                return JsonResponse({'valid': False, 'message': msg})
                
            discount_amount = float(coupon.get_discount_amount(total))
            final_total = max(0.0, total - discount_amount)
            
            return JsonResponse({
                'valid': True,
                'discount_amount': discount_amount,
                'final_total': final_total,
                'message': f'Coupon applied! You save ৳{discount_amount:.2f}'
            })
        except Exception as e:
            return JsonResponse({'valid': False, 'message': str(e)})
            
    return JsonResponse({'valid': False, 'message': 'Invalid request method.'})

def pricing(request):
    plans = Plan.objects.all().order_by('price')
    return render(request, 'subscriptions/pricing.html', {'plans': plans})

@login_required
def checkout(request, plan_id):
    if not getattr(request.user, 'is_employer', False):
        messages.error(request, "Only employers can purchase subscriptions.")
        return redirect('home')
        
    plan = get_object_or_404(Plan, id=plan_id)
    return render(request, 'subscriptions/checkout.html', {'plan': plan})

@login_required
def process_checkout(request, plan_id):
    if request.method != 'POST':
        return redirect('subscriptions:pricing')
        
    if not getattr(request.user, 'is_employer', False):
        messages.error(request, "Only employers can purchase subscriptions.")
        return redirect('home')

    plan = get_object_or_404(Plan, id=plan_id)
    employer_profile = request.user.employer_profile
    
    final_price = float(plan.price)
    discount_amount = 0.0
    applied_coupon = None
    
    coupon_code = request.POST.get('coupon_code')
    if coupon_code:
        coupon = Coupon.objects.filter(code__iexact=coupon_code).first()
        if coupon:
            is_valid, msg = coupon.check_validity()
            if is_valid:
                discount_amount = float(coupon.get_discount_amount(final_price))
                final_price = max(0.0, final_price - discount_amount)
                applied_coupon = coupon
            else:
                messages.error(request, msg)
                return redirect('subscriptions:checkout', plan_id=plan.id)
        else:
            messages.error(request, "Invalid coupon code.")
            return redirect('subscriptions:checkout', plan_id=plan.id)
    
    if employer_profile.credits >= final_price:
        employer_profile.credits -= final_price
        employer_profile.save()
        
        if applied_coupon:
            applied_coupon.times_used += 1
            applied_coupon.save()
            from .models import CouponUsage
            CouponUsage.objects.create(
                coupon=applied_coupon,
                user=request.user,
                discount_amount=discount_amount,
                order_type='SUBSCRIPTION'
            )
    else:
        messages.error(request, "Insufficient wallet balance. Please top up your wallet.")
        return redirect('wallet_topup')
    
    # Check if they already have an active subscription and it's an upgrade
    subscription, created = EmployerSubscription.objects.get_or_create(
        employer=employer_profile,
        defaults={
            'plan': plan,
            'end_date': timezone.now(),
            'status': 'PENDING'
        }
    )
    
    if not created and subscription.status != 'PENDING':
        subscription = EmployerSubscription.objects.create(
            employer=employer_profile,
            plan=plan,
            end_date=timezone.now(),
            status='PENDING'
        )

    # Record the transaction
    tx = Transaction.objects.create(
        subscription=subscription,
        amount=plan.price,
        payment_method="Wallet Balance",
        status="COMPLETED"
    )

    # Activate immediately
    subscription.start_date = timezone.now()
    subscription.end_date = timezone.now() + timedelta(days=plan.duration_days)
    subscription.status = 'ACTIVE'
    subscription.save()
    messages.success(request, f"Successfully subscribed to the {plan.name} plan using Wallet!")
    return redirect('dashboard')

def payment_success(request):
    messages.success(request, "Payment successful! Your account has been updated.")
    return redirect('dashboard')

def payment_cancel(request):
    messages.error(request, "Payment was cancelled.")
    return redirect('dashboard')

def addons_store(request):
    addons = AddOn.objects.all().order_by('price')
    return render(request, 'subscriptions/addons.html', {'addons': addons})

@login_required
def checkout_addon(request, addon_id):
    if not getattr(request.user, 'is_employer', False):
        messages.error(request, "Only employers can purchase add-ons.")
        return redirect('home')
        
    addon = get_object_or_404(AddOn, id=addon_id)
    return render(request, 'subscriptions/checkout_addon.html', {'addon': addon})

@login_required
def process_addon_checkout(request, addon_id):
    if request.method != 'POST':
        return redirect('subscriptions:addons_store')
        
    if not getattr(request.user, 'is_employer', False):
        messages.error(request, "Only employers can purchase add-ons.")
        return redirect('home')

    addon = get_object_or_404(AddOn, id=addon_id)
    employer_profile = request.user.employer_profile
    
    final_price = float(addon.price)
    discount_amount = 0.0
    applied_coupon = None
    
    coupon_code = request.POST.get('coupon_code')
    if coupon_code:
        coupon = Coupon.objects.filter(code__iexact=coupon_code).first()
        if coupon:
            is_valid, msg = coupon.check_validity()
            if is_valid:
                discount_amount = float(coupon.get_discount_amount(final_price))
                final_price = max(0.0, final_price - discount_amount)
                applied_coupon = coupon
            else:
                messages.error(request, msg)
                return redirect('subscriptions:checkout_addon', addon_id=addon.id)
        else:
            messages.error(request, "Invalid coupon code.")
            return redirect('subscriptions:checkout_addon', addon_id=addon.id)
            
    if employer_profile.credits >= final_price:
        employer_profile.credits -= final_price
        employer_profile.save()
        
        if applied_coupon:
            applied_coupon.times_used += 1
            applied_coupon.save()
            from .models import CouponUsage
            CouponUsage.objects.create(
                coupon=applied_coupon,
                user=request.user,
                discount_amount=discount_amount,
                order_type='ADDON'
            )
    else:
        messages.error(request, "Insufficient wallet balance. Please top up your wallet.")
        return redirect('wallet_topup')

    # Create EmployerAddOn
    EmployerAddOn.objects.create(
        employer=employer_profile,
        addon=addon,
        quantity=1,
        is_used=False
    )
    
    # If the addon is Employer Verification Badge, set is_verified to True immediately
    if addon.addon_type == 'VERIFICATION':
        employer_profile.is_verified = True
        employer_profile.save()
        
    messages.success(request, f"Successfully purchased {addon.name} using Wallet!")
    return redirect('dashboard')

@login_required
def billing_dashboard(request):
    if not getattr(request.user, 'is_employer', False):
        return redirect('home')
        
    employer = request.user.employer_profile
    transactions = Transaction.objects.filter(subscription__employer=employer).order_by('-created_at')
    addons = EmployerAddOn.objects.filter(employer=employer).order_by('-purchased_at')
    
    return render(request, 'subscriptions/billing_dashboard.html', {
        'transactions': transactions,
        'addons': addons
    })

@login_required
def download_invoice(request):
    transaction_id = request.GET.get('transaction_id')
    addon_id = request.GET.get('addon_id')
    
    if not getattr(request.user, 'is_employer', False):
        return redirect('home')
        
    employer = request.user.employer_profile
    
    from django.http import HttpResponse
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    import io
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 24)
    p.drawString(50, 750, "JOBBEE INVOICE")
    
    p.setFont("Helvetica", 12)
    p.drawString(50, 720, f"Company: {employer.company_name}")
    p.drawString(50, 700, f"Email: {request.user.email}")
    
    y = 650
    if transaction_id:
        tx = get_object_or_404(Transaction, id=transaction_id, subscription__employer=employer)
        p.drawString(50, y, f"Item: {tx.subscription.plan.name} Subscription")
        p.drawString(50, y-20, f"Amount: $ {tx.amount}")
        p.drawString(50, y-40, f"Payment Method: {tx.payment_method}")
        p.drawString(50, y-60, f"Date: {tx.created_at.strftime('%Y-%m-%d')}")
        p.drawString(50, y-80, f"Status: {tx.status}")
    elif addon_id:
        addon_purchase = get_object_or_404(EmployerAddOn, id=addon_id, employer=employer)
        p.drawString(50, y, f"Item: {addon_purchase.addon.name} Add-on")
        p.drawString(50, y-20, f"Amount: $ {addon_purchase.addon.price}")
        p.drawString(50, y-40, f"Date: {addon_purchase.purchased_at.strftime('%Y-%m-%d')}")
        
    p.showPage()
    p.save()
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice.pdf"'
    return response

from .forms import AdBookingForm

def ad_spaces(request):
    spaces = AdSpace.objects.filter(is_active=True)
    return render(request, 'subscriptions/ad_spaces.html', {'spaces': spaces})

@login_required
def ad_book(request, space_id):
    space = get_object_or_404(AdSpace, id=space_id, is_active=True)
    if request.method == 'POST':
        form = AdBookingForm(request.POST, request.FILES)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.ad_space = space
            days = (booking.end_date - booking.start_date).days
            if days <= 0:
                days = 1
            booking.total_price = space.price_per_day * days
            booking.save()
            messages.success(request, 'Ad space booked successfully. It is now pending approval.')
            return redirect('subscriptions:ad_spaces')
    else:
        form = AdBookingForm()
    
    return render(request, 'subscriptions/ad_book.html', {'form': form, 'space': space})
