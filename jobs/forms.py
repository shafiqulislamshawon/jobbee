from django import forms
from .models import Job

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'description', 'responsibilities', 'requirements', 
            'currency', 'salary_min', 'salary_max', 'employment_type', 'remote_status', 
            'location', 'benefits', 'skills', 'experience', 'education', 'deadline',
            'is_featured'
        ]
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.subscription = kwargs.pop('subscription', None)
        super(JobForm, self).__init__(*args, **kwargs)
        if not self.subscription or not self.subscription.is_active():
            self.fields.pop('is_featured', None)
        elif not self.subscription.plan.can_feature_jobs:
            has_featured_token = self.subscription.employer.addons.filter(addon__addon_type='FEATURED_JOB', is_used=False).exists()
            if not has_featured_token:
                self.fields.pop('is_featured', None)
