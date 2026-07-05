from django import forms
from .models import Job

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'description', 'responsibilities', 'requirements', 
            'currency', 'salary_min', 'salary_max', 'employment_type', 'remote_status', 
            'location', 'benefits', 'skills', 'experience', 'education', 'deadline'
        ]
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }
