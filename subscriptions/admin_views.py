from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from .models import AdSpace, AdBooking

@user_passes_test(lambda u: u.is_staff)
def admin_ads_dashboard(request):
    spaces = AdSpace.objects.all()
    bookings = AdBooking.objects.all().order_by('-created_at')
    
    return render(request, 'core/admin_ads_dashboard.html', {
        'spaces': spaces,
        'bookings': bookings
    })

@user_passes_test(lambda u: u.is_staff)
def admin_ads_approve(request, booking_id):
    if request.method == 'POST':
        booking = get_object_or_404(AdBooking, id=booking_id)
        booking.status = 'APPROVED'
        booking.save()
        messages.success(request, f'Ad booking #{booking.id} approved successfully.')
    return redirect('admin_ads_dashboard')

@user_passes_test(lambda u: u.is_staff)
def admin_ads_reject(request, booking_id):
    if request.method == 'POST':
        booking = get_object_or_404(AdBooking, id=booking_id)
        booking.status = 'REJECTED'
        booking.save()
        messages.success(request, f'Ad booking #{booking.id} rejected.')
    return redirect('admin_ads_dashboard')

from .models import Coupon, CouponUsage

@user_passes_test(lambda u: u.is_staff)
def admin_coupons(request):
    coupons = Coupon.objects.all().order_by('-created_at')
    
    if request.method == 'POST':
        code = request.POST.get('code')
        discount_type = request.POST.get('discount_type')
        discount_value = request.POST.get('discount_value')
        valid_from = request.POST.get('valid_from')
        valid_to = request.POST.get('valid_to') or None
        max_uses = request.POST.get('max_uses') or None
        
        try:
            Coupon.objects.create(
                code=code,
                discount_type=discount_type,
                discount_value=discount_value,
                valid_from=valid_from,
                valid_to=valid_to,
                max_uses=max_uses
            )
            messages.success(request, 'Coupon created successfully.')
        except Exception as e:
            messages.error(request, f'Error creating coupon: {e}')
            
        return redirect('admin_coupons')
        
    return render(request, 'core/admin_coupons.html', {'coupons': coupons})

@user_passes_test(lambda u: u.is_staff)
def admin_toggle_coupon(request, coupon_id):
    if request.method == 'POST':
        coupon = get_object_or_404(Coupon, id=coupon_id)
        coupon.is_active = not coupon.is_active
        coupon.save()
        messages.success(request, f'Coupon {coupon.code} is now {"active" if coupon.is_active else "inactive"}.')
    return redirect('admin_coupons')

@user_passes_test(lambda u: u.is_staff)
def admin_edit_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    if request.method == 'POST':
        coupon.code = request.POST.get('code')
        coupon.discount_type = request.POST.get('discount_type')
        coupon.discount_value = request.POST.get('discount_value')
        coupon.valid_from = request.POST.get('valid_from')
        valid_to = request.POST.get('valid_to')
        coupon.valid_to = valid_to if valid_to else None
        max_uses = request.POST.get('max_uses')
        coupon.max_uses = max_uses if max_uses else None
        
        try:
            coupon.save()
            messages.success(request, 'Coupon updated successfully.')
            return redirect('admin_coupons')
        except Exception as e:
            messages.error(request, f'Error updating coupon: {e}')
            
    return render(request, 'core/admin_edit_coupon.html', {'coupon': coupon})
