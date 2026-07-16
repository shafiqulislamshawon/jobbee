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
