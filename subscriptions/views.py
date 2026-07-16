from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Plan, EmployerSubscription, Transaction, AddOn, EmployerAddOn, AdSpace, AdBooking

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
    
    use_wallet = request.POST.get('use_wallet') == 'true'
    
    if use_wallet:
        if employer_profile.credits >= plan.price:
            employer_profile.credits -= plan.price
            employer_profile.save()
            payment_method = "Wallet Balance"
        else:
            messages.error(request, "Insufficient wallet balance.")
            return redirect('subscriptions:checkout', plan_id=plan.id)
    else:
        payment_method = "Mock Instant Payment"
    
    # Check if they already have an active subscription and it's an upgrade (simplified for now)
    subscription, created = EmployerSubscription.objects.get_or_create(
        employer=employer_profile,
        defaults={
            'plan': plan,
            'end_date': timezone.now(), # Will be updated upon payment
            'status': 'PENDING'
        }
    )
    
    if not created and subscription.status != 'PENDING':
        # Create a new pending subscription for upgrade/renewal
        subscription = EmployerSubscription.objects.create(
            employer=employer_profile,
            plan=plan,
            end_date=timezone.now(),
            status='PENDING'
        )

    # Record the transaction as pending
    tx = Transaction.objects.create(
        subscription=subscription,
        amount=plan.price,
        payment_method="Wallet Balance" if use_wallet else "Stripe",
        status="COMPLETED" if use_wallet else "PENDING"
    )

    if use_wallet:
        # Activate immediately
        subscription.start_date = timezone.now()
        subscription.end_date = timezone.now() + timedelta(days=plan.duration_days)
        subscription.status = 'ACTIVE'
        subscription.save()
        messages.success(request, f"Successfully subscribed to the {plan.name} plan using Wallet!")
        return redirect('dashboard')
    
    # Otherwise, initiate Stripe Checkout
    import stripe
    from django.conf import settings
    from django.urls import reverse
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(plan.price * 100),
                        'product_data': {
                            'name': f"{plan.name} Subscription",
                        },
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            metadata={
                'type': 'subscription',
                'transaction_id': tx.id,
            },
            success_url=request.build_absolute_uri(reverse('subscriptions:payment_success')),
            cancel_url=request.build_absolute_uri(reverse('subscriptions:payment_cancel')),
        )
        return redirect(checkout_session.url)
    except Exception as e:
        messages.error(request, str(e))
        return redirect('subscriptions:checkout', plan_id=plan.id)

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
    
    use_wallet = request.POST.get('use_wallet') == 'true'
    
    if use_wallet:
        if employer_profile.credits >= addon.price:
            employer_profile.credits -= addon.price
            employer_profile.save()
            payment_method = "Wallet Balance"
        else:
            messages.error(request, "Insufficient wallet balance.")
    if use_wallet:
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
        
    # Otherwise, initiate Stripe Checkout
    import stripe
    from django.conf import settings
    from django.urls import reverse
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    try:
        # Create EmployerAddOn as pending (using is_used=False as a placeholder, we might need a pending status, but let's just create it and maybe mark it somehow. Or we just create it in the webhook. Creating it in the webhook is better, but passing its ID is easier if created first. Since EmployerAddOn doesn't have a status field, we will create it when the webhook fires by passing addon.id to metadata)
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(addon.price * 100),
                        'product_data': {
                            'name': f"{addon.name} Add-on",
                        },
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            metadata={
                'type': 'addon',
                'employer_id': employer_profile.id,
                'addon_id': addon.id,
            },
            success_url=request.build_absolute_uri(reverse('subscriptions:payment_success')),
            cancel_url=request.build_absolute_uri(reverse('subscriptions:payment_cancel')),
        )
        return redirect(checkout_session.url)
    except Exception as e:
        messages.error(request, str(e))
        return redirect('subscriptions:checkout_addon', addon_id=addon.id)

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
