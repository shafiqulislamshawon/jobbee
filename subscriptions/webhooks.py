import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Transaction, EmployerSubscription, EmployerAddOn

stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Fulfill the purchase...
        metadata = session.get('metadata', {})
        tx_id = metadata.get('transaction_id')
        
        if tx_id:
            try:
                tx = Transaction.objects.get(id=tx_id)
                tx.status = 'COMPLETED'
                tx.save()
                
                # Activate subscription or addon based on tx type
                if metadata.get('type') == 'subscription':
                    # handled by logic if needed, but the actual activation might be done beforehand 
                    # Wait, our current mock logic marks tx as completed immediately. 
                    # We will update the logic to mark it pending until webhook fires.
                    tx.subscription.is_active = True
                    tx.subscription.start_date = timezone.now()
                    tx.subscription.end_date = timezone.now() + timezone.timedelta(days=tx.subscription.plan.duration_days)
                    tx.subscription.save()
                    
                elif metadata.get('type') == 'addon':
                    addon_id = metadata.get('addon_id')
                    employer_id = metadata.get('employer_id')
                    
                    if addon_id and employer_id:
                        from accounts.models import EmployerProfile
                        from .models import AddOn
                        
                        employer_profile = EmployerProfile.objects.get(id=employer_id)
                        addon = AddOn.objects.get(id=addon_id)
                        
                        EmployerAddOn.objects.create(
                            employer=employer_profile,
                            addon=addon,
                            quantity=1,
                            is_used=False
                        )
                        
                        if addon.addon_type == 'VERIFICATION':
                            employer_profile.is_verified = True
                            employer_profile.save()
                        
            except Exception as e:
                pass

    return HttpResponse(status=200)
