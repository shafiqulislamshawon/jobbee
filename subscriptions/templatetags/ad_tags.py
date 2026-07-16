from django import template
from django.utils import timezone
from subscriptions.models import AdSpace, AdBooking

register = template.Library()

@register.inclusion_tag('subscriptions/includes/render_ad.html')
def render_ad(identifier):
    try:
        ad_space = AdSpace.objects.get(identifier=identifier, is_active=True)
    except AdSpace.DoesNotExist:
        return {'ad': None, 'ad_space': None}

    today = timezone.now().date()
    # Find an active booking for this space
    active_booking = AdBooking.objects.filter(
        ad_space=ad_space,
        status='APPROVED',
        start_date__lte=today,
        end_date__gte=today
    ).order_by('?').first() # Randomly pick one if multiple are active on same day

    return {
        'ad': active_booking,
        'ad_space': ad_space
    }
