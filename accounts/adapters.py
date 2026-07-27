from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from .models import EmployerProfile, SeekerProfile

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        
        # Read the role from session (saved via JS right before auth)
        # Default to seeker if not found
        social_role = request.session.pop('social_role', 'seeker')
        
        if social_role == 'employer':
            user.is_employer = True
            user.save()
            EmployerProfile.objects.get_or_create(user=user, defaults={'company_name': user.username})
        else:
            user.is_seeker = True
            user.save()
            SeekerProfile.objects.get_or_create(user=user)
            
        return user
