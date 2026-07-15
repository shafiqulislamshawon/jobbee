from celery import shared_task
from django.shortcuts import get_object_or_404
from .models import Application
from .utils import calculate_match_score

@shared_task
def async_calculate_match_score(application_id):
    """
    Calculate the match score for a given application asynchronously.
    """
    try:
        application = Application.objects.get(id=application_id)
        job = application.job
        seeker_profile = application.applicant.seeker_profile
        
        score = calculate_match_score(job, seeker_profile)
        
        application.match_score = score
        application.save()
        return f"Application {application_id} scored: {score}"
    except Application.DoesNotExist:
        return f"Application {application_id} does not exist"
    except Exception as e:
        return f"Error scoring application {application_id}: {str(e)}"
